"""
SynapseOS Potato-Optimized NEAT (Neuroevolution of Augmenting Topologies) Engine.
Pure Python + math implementation requiring 0 external dependencies and <5MB RAM.
Supports dynamic structural mutation (Add Node, Add Synapse), historical innovation
numbers, speciation compatibility distance, crossover, and live neuron activation inspection.
"""

import math
import random
import copy
from typing import Dict, List, Tuple, Optional, Any


def tanh_act(x: float) -> float:
    x = max(-20.0, min(20.0, x))
    return math.tanh(x)


class NodeGene:
    def __init__(self, node_id: int, node_type: str, layer: float, bias: float = 0.0):
        self.id = node_id
        self.type = node_type  # 'input', 'hidden', 'output'
        self.layer = layer     # 0.0 for input, 1.0 for output, (0.0..1.0) for hidden
        self.bias = bias
        self.last_activation = 0.0

    def copy(self) -> "NodeGene":
        n = NodeGene(self.id, self.type, self.layer, self.bias)
        n.last_activation = self.last_activation
        return n


class ConnectionGene:
    def __init__(self, in_node: int, out_node: int, weight: float, enabled: bool, innovation: int):
        self.in_node = in_node
        self.out_node = out_node
        self.weight = weight
        self.enabled = enabled
        self.innovation = innovation

    def copy(self) -> "ConnectionGene":
        return ConnectionGene(self.in_node, self.out_node, self.weight, self.enabled, self.innovation)


class InnovationTracker:
    """Tracks global historical markings for structural mutations."""
    def __init__(self, start_node_id: int):
        self.current_innovation = 0
        self.next_node_id = start_node_id
        self.connection_history: Dict[Tuple[int, int], int] = {}

    def get_innovation(self, in_node: int, out_node: int) -> int:
        key = (in_node, out_node)
        if key not in self.connection_history:
            self.current_innovation += 1
            self.connection_history[key] = self.current_innovation
        return self.connection_history[key]

    def allocate_node_id(self) -> int:
        nid = self.next_node_id
        self.next_node_id += 1
        return nid


class NEATGenome:
    def __init__(self, num_inputs: int, num_outputs: int, tracker: InnovationTracker, sparse_init: bool = False):
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.nodes: Dict[int, NodeGene] = {}
        self.connections: Dict[int, ConnectionGene] = {}
        self.fitness: float = 0.0
        self.adjusted_fitness: float = 0.0

        # Create input nodes (0 .. num_inputs - 1)
        for i in range(num_inputs):
            self.nodes[i] = NodeGene(i, "input", layer=0.0, bias=0.0)

        # Create output nodes (num_inputs .. num_inputs + num_outputs - 1)
        for o in range(num_outputs):
            oid = num_inputs + o
            self.nodes[oid] = NodeGene(oid, "output", layer=1.0, bias=random.gauss(0.0, 0.3))

        # Initial minimal connections
        for i in range(num_inputs):
            for o in range(num_outputs):
                if sparse_init and random.random() < 0.4:
                    continue
                oid = num_inputs + o
                innov = tracker.get_innovation(i, oid)
                w = random.gauss(0.0, 0.8)
                self.connections[innov] = ConnectionGene(i, oid, w, True, innov)

    def copy(self) -> "NEATGenome":
        g = object.__new__(NEATGenome)
        g.num_inputs = self.num_inputs
        g.num_outputs = self.num_outputs
        g.nodes = {k: v.copy() for k, v in self.nodes.items()}
        g.connections = {k: v.copy() for k, v in self.connections.items()}
        g.fitness = self.fitness
        g.adjusted_fitness = self.adjusted_fitness
        return g

    def forward(self, inputs: List[float]) -> List[float]:
        """Evaluate feed-forward network ordered by topological layer."""
        for i in range(min(len(inputs), self.num_inputs)):
            self.nodes[i].last_activation = float(inputs[i])

        # Group non-input nodes sorted by layer
        eval_nodes = sorted(
            [n for n in self.nodes.values() if n.type != "input"],
            key=lambda n: n.layer
        )

        # Pre-accumulate incoming signals per target node
        incoming: Dict[int, List[ConnectionGene]] = {n.id: [] for n in eval_nodes}
        for conn in self.connections.values():
            if conn.enabled and conn.out_node in incoming:
                incoming[conn.out_node].append(conn)

        for node in eval_nodes:
            s = node.bias
            for conn in incoming[node.id]:
                src = self.nodes.get(conn.in_node)
                if src is not None:
                    s += src.last_activation * conn.weight
            node.last_activation = tanh_act(s)

        return [self.nodes[self.num_inputs + o].last_activation for o in range(self.num_outputs)]

    def mutate_weights(self, prob: float = 0.8, power: float = 0.5) -> None:
        for conn in self.connections.values():
            if random.random() < prob:
                if random.random() < 0.1:
                    conn.weight = random.gauss(0.0, 1.0)
                else:
                    conn.weight += random.gauss(0.0, power)
                    conn.weight = max(-6.0, min(6.0, conn.weight))

        for node in self.nodes.values():
            if node.type != "input" and random.random() < prob:
                node.bias += random.gauss(0.0, power * 0.5)
                node.bias = max(-4.0, min(4.0, node.bias))

    def mutate_add_connection(self, tracker: InnovationTracker) -> None:
        node_list = list(self.nodes.values())
        for _ in range(15):
            n1 = random.choice(node_list)
            n2 = random.choice(node_list)
            if n1.layer >= n2.layer:
                continue
            # Check if connection already exists
            exists = any(
                c.in_node == n1.id and c.out_node == n2.id
                for c in self.connections.values()
            )
            if not exists:
                innov = tracker.get_innovation(n1.id, n2.id)
                self.connections[innov] = ConnectionGene(
                    n1.id, n2.id, random.gauss(0.0, 0.8), True, innov
                )
                return

    def mutate_add_node(self, tracker: InnovationTracker, max_hidden: int = 16) -> None:
        hidden_count = sum(1 for n in self.nodes.values() if n.type == "hidden")
        if hidden_count >= max_hidden:
            return
        enabled_conns = [c for c in self.connections.values() if c.enabled]
        if not enabled_conns:
            return
        conn = random.choice(enabled_conns)
        src_node = self.nodes[conn.in_node]
        dst_node = self.nodes[conn.out_node]
        new_layer = (src_node.layer + dst_node.layer) / 2.0
        if abs(new_layer - src_node.layer) < 1e-4:
            return

        conn.enabled = False
        new_id = tracker.allocate_node_id()
        self.nodes[new_id] = NodeGene(new_id, "hidden", layer=new_layer, bias=0.0)

        innov1 = tracker.get_innovation(src_node.id, new_id)
        innov2 = tracker.get_innovation(new_id, dst_node.id)
        self.connections[innov1] = ConnectionGene(src_node.id, new_id, 1.0, True, innov1)
        self.connections[innov2] = ConnectionGene(new_id, dst_node.id, conn.weight, True, innov2)

    def mutate_remove_node(self) -> bool:
        """Remove a hidden neuron and clean up its incident synapses."""
        hidden_ids = [nid for nid, n in self.nodes.items() if n.type == "hidden"]
        if not hidden_ids:
            return False
        victim_id = random.choice(hidden_ids)
        del self.nodes[victim_id]
        to_delete = [
            innov for innov, c in self.connections.items()
            if c.in_node == victim_id or c.out_node == victim_id
        ]
        for innov in to_delete:
            del self.connections[innov]
        # Re-enable a disabled connection if any exist so signal flow stays healthy
        disabled = [c for c in self.connections.values() if not c.enabled and c.in_node in self.nodes and c.out_node in self.nodes]
        if disabled:
            random.choice(disabled).enabled = True
        return True

    def mutate_remove_connection(self) -> bool:
        """Prune/disable an enabled synapse while keeping at least 2 active connections."""
        enabled = [c for c in self.connections.values() if c.enabled]
        if len(enabled) <= 2:
            return False
        victim = random.choice(enabled)
        victim.enabled = False
        return True

    @staticmethod
    def crossover(parent1: "NEATGenome", parent2: "NEATGenome") -> "NEATGenome":
        """Crossover assuming parent1 is at least as fit as parent2."""
        if parent2.fitness > parent1.fitness:
            parent1, parent2 = parent2, parent1

        child = parent1.copy()
        for innov, conn1 in child.connections.items():
            if innov in parent2.connections:
                conn2 = parent2.connections[innov]
                if random.random() < 0.5:
                    conn1.weight = conn2.weight
                if not conn1.enabled or not conn2.enabled:
                    conn1.enabled = (random.random() > 0.75)
        return child

    @staticmethod
    def compatibility_distance(g1: "NEATGenome", g2: "NEATGenome", c1: float = 1.0, c2: float = 1.0, c3: float = 0.4) -> float:
        if not g1.connections and not g2.connections:
            return 0.0
        k1 = set(g1.connections.keys())
        k2 = set(g2.connections.keys())
        matching = k1.intersection(k2)
        disjoint_excess = len(k1.symmetric_difference(k2))
        n = max(len(k1), len(k2), 1)
        if n < 20:
            n = 1

        weight_diff = 0.0
        if matching:
            weight_diff = sum(abs(g1.connections[i].weight - g2.connections[i].weight) for i in matching) / len(matching)

        return (c1 * disjoint_excess / n) + (c3 * weight_diff)


class NEATPopulation:
    def __init__(
        self,
        num_inputs: int,
        num_outputs: int,
        pop_size: int = 80,
        conn_add_prob: float = 0.15,
        node_add_prob: float = 0.05,
        weight_mutate_power: float = 0.60,
        compat_threshold: float = 2.8
    ):
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.pop_size = pop_size
        self.conn_add_prob = conn_add_prob
        self.node_add_prob = node_add_prob
        self.weight_mutate_power = weight_mutate_power
        self.compat_threshold = compat_threshold

        self.tracker = InnovationTracker(start_node_id=num_inputs + num_outputs)
        self.genomes: List[NEATGenome] = [
            NEATGenome(num_inputs, num_outputs, self.tracker) for _ in range(pop_size)
        ]
        self.species: List[List[NEATGenome]] = []
        self.generation: int = 1
        self.best_genome: NEATGenome = self.genomes[0].copy()
        self.best_fitness_ever: float = -1e9
        self.history_best: List[float] = []
        self.history_avg: List[float] = []

    def modify_structure(self, delta_neurons: int = 0, delta_synapses: int = 0) -> Dict[str, int]:
        """Directly add or subtract hidden neurons or synapses across the active population & champion."""
        targets = [self.best_genome] + self.genomes
        for g in targets:
            if delta_neurons > 0:
                for _ in range(delta_neurons):
                    g.mutate_add_node(self.tracker, max_hidden=32)
            elif delta_neurons < 0:
                for _ in range(abs(delta_neurons)):
                    g.mutate_remove_node()
            if delta_synapses > 0:
                for _ in range(delta_synapses):
                    g.mutate_add_connection(self.tracker)
            elif delta_synapses < 0:
                for _ in range(abs(delta_synapses)):
                    g.mutate_remove_connection()
        hidden = sum(1 for n in self.best_genome.nodes.values() if n.type == "hidden")
        enabled_conns = sum(1 for c in self.best_genome.connections.values() if c.enabled)
        return {
            "total_nodes": len(self.best_genome.nodes),
            "hidden_nodes": hidden,
            "enabled_synapses": enabled_conns,
        }

    def speciate(self) -> None:
        representatives = [s[0] for s in self.species if s]
        new_species: List[List[NEATGenome]] = [[] for _ in representatives]

        for g in self.genomes:
            placed = False
            for idx, rep in enumerate(representatives):
                if NEATGenome.compatibility_distance(g, rep) < self.compat_threshold:
                    new_species[idx].append(g)
                    placed = True
                    break
            if not placed:
                representatives.append(g)
                new_species.append([g])

        self.species = [s for s in new_species if len(s) > 0]

    def evolve_generation(self) -> Dict[str, Any]:
        """Speciate, record telemetry, and breed next generation."""
        self.genomes.sort(key=lambda g: g.fitness, reverse=True)
        gen_best = self.genomes[0]
        gen_avg = sum(g.fitness for g in self.genomes) / max(1, len(self.genomes))

        if gen_best.fitness > self.best_fitness_ever:
            self.best_fitness_ever = gen_best.fitness
            self.best_genome = gen_best.copy()

        self.history_best.append(round(gen_best.fitness, 2))
        self.history_avg.append(round(gen_avg, 2))

        self.speciate()

        # Build next generation
        next_gen: List[NEATGenome] = [self.best_genome.copy()]  # Always preserve global champion

        # Keep top elite from each species
        surviving_parents: List[NEATGenome] = []
        for s in self.species:
            s.sort(key=lambda g: g.fitness, reverse=True)
            if len(next_gen) < self.pop_size // 4:
                next_gen.append(s[0].copy())
            cutoff = max(1, len(s) // 2)
            surviving_parents.extend(s[:cutoff])

        if not surviving_parents:
            surviving_parents = self.genomes[:max(2, len(self.genomes) // 3)]

        while len(next_gen) < self.pop_size:
            p1 = random.choice(surviving_parents)
            p2 = random.choice(surviving_parents)
            child = NEATGenome.crossover(p1, p2)
            child.mutate_weights(prob=0.8, power=self.weight_mutate_power)
            if random.random() < self.conn_add_prob:
                child.mutate_add_connection(self.tracker)
            if random.random() < self.node_add_prob:
                child.mutate_add_node(self.tracker)
            next_gen.append(child)

        self.genomes = next_gen[:self.pop_size]
        self.generation += 1

        return {
            "generation": self.generation - 1,
            "best_fitness": round(gen_best.fitness, 2),
            "avg_fitness": round(gen_avg, 2),
            "species_count": len(self.species),
            "best_nodes": len(gen_best.nodes),
            "best_conns": sum(1 for c in gen_best.connections.values() if c.enabled)
        }
