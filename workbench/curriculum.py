"""
SynapseOS Classroom & School AI Curriculum Suite (`workbench/curriculum.py`)
Provides 12 interactive, gamified Follow-Along Tutorials, Mission Quests,
and Hands-On Python Coding Challenges for students, kids, and beginners.
"""

from typing import List, Dict, Any, Tuple


SCHOOL_CURRICULUM: List[Dict[str, Any]] = [
    # ==========================================================================
    # TRACK 1: ROCKET ACADEMY (NEUROEVOLUTION & NEAT)
    # ==========================================================================
    {
        "id": "lesson_1_1",
        "track": "Track 1: Rocket Academy (NEAT)",
        "title": "1.1 First Moon Landing: Sensors & Thrusters",
        "grade_level": "Ages 9+ / Beginner",
        "lab_id": "moon_lander",
        "badge": "🏅 Lunar Cadet",
        "story": (
            "Welcome to Space Command! Your mission is to teach a fleet of robot rockets how to land "
            "softly between the green flags on the Moon—without programming any 'if/else' rules! "
            "Instead, each rocket has 8 eyes (sensors for height, speed, and tilt) wired to 4 thrusters."
        ),
        "steps": [
            "1. Click '🎯 Load Lesson Preset' below to set Moon Gravity (1.62 m/s²) and 60 Rockets.",
            "2. Watch Generation 1 in the center screen: most rockets crash because their brain wires start random!",
            "3. Click '⚡ Turbo +25 Gens' on the left panel to fast-forward 25 generations of evolution.",
            "4. Click '✅ Check Mission Goal' once your All-Time Best Score reaches 180 or higher!"
        ],
        "preset_params": {
            "gravity": 1.62,
            "wind": 0.0,
            "fuel_capacity": 160.0,
            "pop_size": 60.0,
            "conn_add_prob": 0.18,
            "node_add_prob": 0.06,
            "weight_mutate_power": 0.60,
            "landing_bonus": 240.0
        },
        "goal_metric": "best_ever",
        "goal_op": ">=",
        "goal_target": 180.0,
        "goal_desc": "Reach an All-Time Best Fitness >= 180.0 in NEAT Moon Lander",
        "coding_challenge": (
            "# 🎯 HANDS-ON CODING CHALLENGE 1.1:\n"
            "# Change `gravity` from 1.62 (Moon) to 3.72 (Mars) and `landing_bonus` to 300.0,\n"
            "# then click '▶ Run My Code' to see if your rockets can conquer Mars!\n\n"
            "from workbench.labs.moon_lander import NEATMoonLanderLab\n\n"
            "lab = NEATMoonLanderLab()\n"
            "lab.update_param('gravity', 1.62)        # <-- Try changing to 3.72 (Mars)!\n"
            "lab.update_param('landing_bonus', 240.0) # <-- Try changing to 300.0!\n"
            "lab.update_param('pop_size', 40)\n"
            "lab.reset_generation()\n\n"
            "for gen in range(1, 11):\n"
            "    while not lab.step_physics():\n"
            "        pass\n"
            "    t = lab.get_telemetry()\n"
            "    print(f\"Gen {gen:02d} | Best Score: {t['best_fitness']:6.1f} | Landed Rockets: {t['landed_last_gen']}\")\n"
        )
    },
    {
        "id": "lesson_1_2",
        "track": "Track 1: Rocket Academy (NEAT)",
        "title": "1.2 Growing a Bigger Brain: Neurons & Synapses",
        "grade_level": "Ages 10+ / Beginner",
        "lab_id": "moon_lander",
        "badge": "🧠 Brain Architect",
        "story": (
            "What makes NEAT special? Most AI starts with a fixed brain size, but NEAT starts tiny and "
            "grows new neurons (thinking circles) and synapses (green/red wires) only when needed!\n"
            "Green wires excite a thruster (FIRE!), while red wires inhibit a thruster (WAIT!)."
        ),
        "steps": [
            "1. Click '🎯 Load Lesson Preset' to turn UP 'Add Neuron Rate' to 0.18 and 'Add Synapse Rate' to 0.35.",
            "2. Look at the '🧠 Brain & Curves' panel on the right.",
            "3. Click '⚡ Turbo +25 Gens' and watch new hidden neurons appear in the middle layer of the brain!",
            "4. Reach at least 10 total neurons in your champion rocket's brain, then click '✅ Check Mission Goal'!"
        ],
        "preset_params": {
            "gravity": 1.62,
            "wind": 0.35,
            "fuel_capacity": 160.0,
            "pop_size": 60.0,
            "conn_add_prob": 0.35,
            "node_add_prob": 0.18,
            "weight_mutate_power": 0.65,
            "landing_bonus": 250.0
        },
        "goal_metric": "champion_nodes",
        "goal_op": ">=",
        "goal_target": 13.0,
        "goal_desc": "Evolve a champion rocket brain with at least 13 total nodes (8 inputs + 4 outputs + 1+ hidden neuron)",
        "coding_challenge": (
            "# 🎯 HANDS-ON CODING CHALLENGE 1.2:\n"
            "# Inspect a NEAT Genome's neurons and synaptic weights directly in Python!\n\n"
            "from workbench.labs.neat_core import NEATPopulation\n\n"
            "pop = NEATPopulation(num_inputs=4, num_outputs=2, pop_size=25, node_add_prob=0.25)\n"
            "for gen in range(1, 9):\n"
            "    for g in pop.genomes:\n"
            "        out = g.forward([1.0, -0.5, 0.2, 0.8])\n"
            "        g.fitness = out[0] * 50.0 - abs(out[1]) * 10.0\n"
            "    info = pop.evolve_generation()\n"
            "    print(f\"Gen {gen} -> Best Fitness: {info['best_fitness']} | Neurons: {info['best_nodes']} | Wires: {info['best_conns']}\")\n"
        )
    },
    {
        "id": "lesson_1_3",
        "track": "Track 1: Rocket Academy (NEAT)",
        "title": "1.3 Stormy Mars Landing & Reward Shaping",
        "grade_level": "Ages 11+ / Intermediate",
        "lab_id": "moon_lander",
        "badge": "🌪️ Storm Commander",
        "story": (
            "Sometimes AI finds sneaky loopholes called 'Reward Hacking'! If crashing hurts a lot (-100 points) "
            "and landing barely gives any points (+50), rockets might try to hover high in the sky forever. "
            "Your job is to land in a Mars windstorm by tuning the Landing Reward!"
        ),
        "steps": [
            "1. Click '🎯 Load Lesson Preset'—notice Crosswind is set to 0.65 and Gravity to 2.8!",
            "2. Drag the 'Landing Reward' slider on the left all the way up to 380.",
            "3. Click '⚡ Turbo +25 Gens' to train your fleet against the wind.",
            "4. Achieve a Best Score >= 200 in windy conditions and click '✅ Check Mission Goal'!"
        ],
        "preset_params": {
            "gravity": 2.80,
            "wind": 0.65,
            "fuel_capacity": 190.0,
            "pop_size": 70.0,
            "conn_add_prob": 0.20,
            "node_add_prob": 0.08,
            "weight_mutate_power": 0.65,
            "landing_bonus": 350.0
        },
        "goal_metric": "best_ever",
        "goal_op": ">=",
        "goal_target": 200.0,
        "goal_desc": "Reach All-Time Best Fitness >= 200.0 in a windy landing challenge",
        "coding_challenge": (
            "# 🎯 HANDS-ON CODING CHALLENGE 1.3:\n"
            "# Write your own custom Fitness Function for a lunar lander state!\n\n"
            "def my_custom_fitness(dist_to_pad, speed, tilt_angle, landed, crashed):\n"
            "    score = 100.0\n"
            "    score -= dist_to_pad * 80.0   # Reward getting closer to the pad\n"
            "    score -= speed * 40.0         # Penalize coming in too fast\n"
            "    score -= abs(tilt_angle) * 30.0\n"
            "    if landed:\n"
            "        score += 300.0            # <-- Try changing the landing jackpot!\n"
            "    if crashed:\n"
            "        score -= 100.0\n"
            "    return round(score, 1)\n\n"
            "print('Crash score:', my_custom_fitness(dist_to_pad=0.4, speed=3.5, tilt_angle=0.8, landed=False, crashed=True))\n"
            "print('Soft landing score:', my_custom_fitness(dist_to_pad=0.02, speed=0.3, tilt_angle=0.01, landed=True, crashed=False))\n"
        )
    },

    # ==========================================================================
    # TRACK 2: AUTONOMOUS DRIVING SCHOOL (LIDAR & SELF-DRIVING)
    # ==========================================================================
    {
        "id": "lesson_2_1",
        "track": "Track 2: Self-Driving School (Lidar)",
        "title": "2.1 How Robot Cars See with Laser Beams",
        "grade_level": "Ages 9+ / Beginner",
        "lab_id": "raycast_car",
        "badge": "🏎️ Lidar Navigator",
        "story": (
            "Self-driving cars use Lidar (Light Detection and Ranging)—invisible laser beams that bounce "
            "off road walls to measure distance! Watch the lead car's 5 laser beams turn green when the "
            "road ahead is clear and red when a wall is close."
        ),
        "steps": [
            "1. Click '🎯 Load Lesson Preset' to open the Self-Driving Lidar Car lab.",
            "2. Drag 'Lidar Ray Range' from 60 px up to 160 px so the cars can see corners early.",
            "3. Click '⚡ Turbo +25 Gens' to evolve steering and throttle brains.",
            "4. Reach an All-Time Best Score >= 500 and click '✅ Check Mission Goal'!"
        ],
        "preset_params": {
            "sensor_range": 145.0,
            "max_speed": 4.5,
            "turn_rate": 0.09,
            "track_width": 42.0,
            "pop_size": 40.0,
            "conn_add_prob": 0.16,
            "node_add_prob": 0.05,
            "weight_mutate_power": 0.55
        },
        "goal_metric": "best_ever",
        "goal_op": ">=",
        "goal_target": 500.0,
        "goal_desc": "Reach All-Time Best Score >= 500.0 in NEAT Self-Driving Lidar Car",
        "coding_challenge": (
            "# 🎯 HANDS-ON CODING CHALLENGE 2.1:\n"
            "# Test how Lidar sensor range affects self-driving car survival distance!\n\n"
            "from workbench.labs.raycast_car import NEATRaycastCarLab\n\n"
            "for lidar_range in [60.0, 150.0]:\n"
            "    lab = NEATRaycastCarLab()\n"
            "    lab.update_param('sensor_range', lidar_range)\n"
            "    lab.update_param('pop_size', 25)\n"
            "    lab.reset_generation()\n"
            "    stats = lab.fast_forward_generations(6)\n"
            "    print(f\"Lidar Range {lidar_range:5.1f} px -> Best Driving Score: {stats['best_ever']}\")\n"
        )
    },
    {
        "id": "lesson_2_2",
        "track": "Track 2: Self-Driving School (Lidar)",
        "title": "2.2 High-Speed Racing on a Narrow Track",
        "grade_level": "Ages 11+ / Intermediate",
        "lab_id": "raycast_car",
        "badge": "🏁 Grand Prix AI",
        "story": (
            "Driving slow on a wide highway is easy—but what happens when we narrow the road and boost "
            "top speed? If 'Steering Agility' is too low, the car understeers into the wall; if too high, "
            "it wobbles like a snake!"
        ),
        "steps": [
            "1. Click '🎯 Load Lesson Preset' to set a fast Max Speed (6.0) on a narrower 34 px track.",
            "2. Fine-tune 'Steering Agility' around 0.10 - 0.12.",
            "3. Click '⚡ Turbo +25 Gens' and beat a score of 650!"
        ],
        "preset_params": {
            "sensor_range": 165.0,
            "max_speed": 4.8,
            "turn_rate": 0.10,
            "track_width": 42.0,
            "pop_size": 45.0,
            "conn_add_prob": 0.18,
            "node_add_prob": 0.06,
            "weight_mutate_power": 0.50
        },
        "goal_metric": "best_ever",
        "goal_op": ">=",
        "goal_target": 650.0,
        "goal_desc": "Reach All-Time Best Score >= 650.0 at high speed",
        "coding_challenge": (
            "# 🎯 HANDS-ON CODING CHALLENGE 2.2:\n"
            "# Write a simple proportional steering controller from 5 lidar rays!\n\n"
            "def proportional_steer(rays):\n"
            "    # rays = [far_left, left, center, right, far_right]\n"
            "    left_space = rays[0] + rays[1]\n"
            "    right_space = rays[3] + rays[4]\n"
            "    steer = (right_space - left_space) * 0.5\n"
            "    return round(steer, 3)\n\n"
            "print('Wall on left  -> Steer:', proportional_steer([0.1, 0.2, 0.8, 0.9, 1.0]))\n"
            "print('Wall on right -> Steer:', proportional_steer([1.0, 0.9, 0.8, 0.2, 0.1]))\n"
        )
    },

    # ==========================================================================
    # TRACK 3: LAVA MAZE TREASURE HUNT (REINFORCEMENT LEARNING)
    # ==========================================================================
    {
        "id": "lesson_3_1",
        "track": "Track 3: Lava Maze (Reinforcement Learning)",
        "title": "3.1 Curiosity vs. Greed: How Q-Learning Explores",
        "grade_level": "Ages 9+ / Beginner",
        "lab_id": "rl_gridworld",
        "badge": "🧭 Treasure Seeker",
        "story": (
            "In Reinforcement Learning, the blue agent starts knowing NOTHING about where the ★ GOAL or "
            "red LAVA pits are. Every square stores 4 numbers (Q-values) for Up, Right, Down, Left. "
            "As the agent finds the treasure (+120 points), watch the green glow and arrows spread across the map!"
        ),
        "steps": [
            "1. Click '🎯 Load Lesson Preset' to switch to the RL Hazard GridWorld lab.",
            "2. Watch the blue circle explore and update the arrows (↑ → ↓ ←) in every square.",
            "3. Click '⚡ Turbo +25 Gens' twice to train 50+ episodes in milliseconds!",
            "4. Reach at least 15 Treasure Wins ('species' counter) and click '✅ Check Mission Goal'!"
        ],
        "preset_params": {
            "alpha": 0.30,
            "gamma": 0.95,
            "epsilon": 0.12,
            "goal_reward": 120.0,
            "lava_penalty": -100.0,
            "step_penalty": -1.0,
            "wind_prob": 0.0,
            "use_sarsa": 0.0
        },
        "goal_metric": "species",
        "goal_op": ">=",
        "goal_target": 15.0,
        "goal_desc": "Guide the RL agent to reach the ★ GOAL at least 15 times",
        "coding_challenge": (
            "# 🎯 HANDS-ON CODING CHALLENGE 3.1:\n"
            "# Run 80 episodes of Q-Learning and print the learned path arrows!\n\n"
            "from workbench.labs.rl_gridworld import RLGridWorldLab\n\n"
            "lab = RLGridWorldLab()\n"
            "lab.update_param('alpha', 0.35)\n"
            "lab.update_param('epsilon', 0.10)\n"
            "stats = lab.fast_forward_generations(80)\n"
            "print(f\"Episodes: {stats['generation']} | Goal Wins: {stats['species']} | Best Return: {stats['best_ever']}\")\n\n"
            "for r in range(lab.rows):\n"
            "    row_str = ''\n"
            "    for c in range(lab.cols):\n"
            "        if (c, r) == lab.goal_pos: row_str += ' ★ '\n"
            "        elif (c, r) in lab.lava_cells: row_str += ' 🔥'\n"
            "        elif (c, r) in lab.wall_cells: row_str += ' ██'\n"
            "        else:\n"
            "            best_a = max(range(4), key=lab.q_table[(c, r)].__getitem__)\n"
            "            row_str += f' {lab.ARROWS[best_a]} '\n"
            "    print(row_str)\n"
        )
    },
    {
        "id": "lesson_3_2",
        "track": "Track 3: Lava Maze (Reinforcement Learning)",
        "title": "3.2 Cautious SARSA vs. Bold Q-Learning Near Cliffs",
        "grade_level": "Ages 12+ / Intermediate",
        "lab_id": "rl_gridworld",
        "badge": "🛡️ Cliff Master",
        "story": (
            "What happens when a slippery wind blows near the lava cliff? "
            "Q-Learning is an 'optimist'—it walks right along the edge of the lava cliff assuming it won't slip. "
            "SARSA is 'cautious'—it remembers its own random slips and learns a safer path higher up!"
        ),
        "steps": [
            "1. Click '🎯 Load Lesson Preset' (sets Wind Slip = 0.15 and Algorithm = 1 for SARSA).",
            "2. Click '⚡ Turbo +25 Gens' twice so SARSA learns a safe path around the lava.",
            "3. Verify that your agent achieves a positive Best Score >= 50!"
        ],
        "preset_params": {
            "alpha": 0.25,
            "gamma": 0.96,
            "epsilon": 0.10,
            "goal_reward": 140.0,
            "lava_penalty": -120.0,
            "step_penalty": -0.8,
            "wind_prob": 0.15,
            "use_sarsa": 1.0
        },
        "goal_metric": "best_ever",
        "goal_op": ">=",
        "goal_target": 50.0,
        "goal_desc": "Achieve Best Return >= 50.0 using SARSA in windy cliff conditions",
        "coding_challenge": (
            "# 🎯 HANDS-ON CODING CHALLENGE 3.2:\n"
            "# Compare Q-Learning (use_sarsa=0) vs SARSA (use_sarsa=1) with 20% wind!\n\n"
            "from workbench.labs.rl_gridworld import RLGridWorldLab\n\n"
            "for name, sarsa_flag in [('Q-Learning', 0.0), ('SARSA', 1.0)]:\n"
            "    lab = RLGridWorldLab()\n"
            "    lab.update_param('wind_prob', 0.20)\n"
            "    lab.update_param('use_sarsa', sarsa_flag)\n"
            "    stats = lab.fast_forward_generations(100)\n"
            "    print(f\"{name:<12} -> Wins: {stats['species']:3d} | Avg Return: {stats['avg_fitness']:6.1f}\")\n"
        )
    },

    # ==========================================================================
    # TRACK 4: ROBOT BALANCE CHALLENGE (CARTPOLE CONTROL)
    # ==========================================================================
    {
        "id": "lesson_4_1",
        "track": "Track 4: Robot Balance (CartPole)",
        "title": "4.1 Balancing an Unstable Pendulum in the Wind",
        "grade_level": "Ages 9+ / Beginner",
        "lab_id": "cartpole_rl",
        "badge": "⚖️ Balance Master",
        "story": (
            "Have you ever balanced a broomstick upright on your palm? If it tilts right, you have to "
            "quickly slide your hand right to catch it! That's the classic CartPole problem used to test "
            "robotics AI around the world."
        ),
        "steps": [
            "1. Click '🎯 Load Lesson Preset' to open the CartPole Inverted Pendulum lab.",
            "2. Try dragging 'Pole Length'—longer poles fall slower, shorter poles fall super fast!",
            "3. Click '⚡ Turbo +25 Gens' and reach a Balance Score >= 500!"
        ],
        "preset_params": {
            "gravity": 9.8,
            "pole_length": 0.65,
            "force_mag": 12.0,
            "wind_gust": 0.25,
            "pop_size": 35.0,
            "conn_add_prob": 0.15,
            "node_add_prob": 0.05,
            "weight_mutate_power": 0.45
        },
        "goal_metric": "best_ever",
        "goal_op": ">=",
        "goal_target": 500.0,
        "goal_desc": "Reach a Best Balance Score >= 500.0 in CartPole",
        "coding_challenge": (
            "# 🎯 HANDS-ON CODING CHALLENGE 4.1:\n"
            "# Test CartPole balancing under Jupiter Gravity (22.0 m/s^2)!\n\n"
            "from workbench.labs.cartpole_rl import CartPoleLab\n\n"
            "lab = CartPoleLab()\n"
            "lab.update_param('gravity', 22.0)   # Jupiter gravity!\n"
            "lab.update_param('force_mag', 20.0) # Stronger motor to compensate\n"
            "lab.reset_generation()\n"
            "stats = lab.fast_forward_generations(15)\n"
            "print(f\"Jupiter CartPole Best Score: {stats['best_ever']} (Gen {stats['generation']})\")\n"
        )
    },

    # ==========================================================================
    # TRACK 5: INSIDE A NEURAL NETWORK (BACKPROPAGATION & SHAPES)
    # ==========================================================================
    {
        "id": "lesson_5_1",
        "track": "Track 5: Neural Networks (Backprop)",
        "title": "5.1 Cracking the XOR & Concentric Rings Puzzle",
        "grade_level": "Ages 10+ / Beginner & Coder",
        "lab_id": "nn_playground",
        "badge": "🔮 Pattern Wizard",
        "story": (
            "In 1969, scientists proved a single artificial neuron can only draw a straight line—so it "
            "couldn't separate a blue circle surrounded by an orange ring! Adding a 'Hidden Layer' of "
            "neurons lets the network bend and curve its decision boundary."
        ),
        "steps": [
            "1. Click '🎯 Load Lesson Preset' to open the Neural Network Backprop Playground on Concentric Rings.",
            "2. Watch the blue and orange background morph in real time as Backpropagation updates the weights!",
            "3. Try changing 'Dataset' slider from 1 (Rings) to 0 (XOR) or 2 (Two Moons).",
            "4. Reach at least 92% classification accuracy and click '✅ Check Mission Goal'!"
        ],
        "preset_params": {
            "dataset_id": 1.0,
            "hidden_neurons": 8.0,
            "learning_rate": 0.22,
            "l2_reg": 0.001,
            "noise": 0.05,
            "steps_per_frame": 6.0
        },
        "goal_metric": "best_ever",
        "goal_op": ">=",
        "goal_target": 92.0,
        "goal_desc": "Train the Neural Network to >= 92.0% classification accuracy",
        "coding_challenge": (
            "# 🎯 HANDS-ON CODING CHALLENGE 5.1:\n"
            "# Compare a tiny 2-neuron network vs a 12-neuron network on the Two Moons dataset!\n\n"
            "from workbench.labs.nn_playground import NeuralPlaygroundLab\n\n"
            "for neurons in [2, 12]:\n"
            "    lab = NeuralPlaygroundLab()\n"
            "    lab.update_param('dataset_id', 2) # Two Moons\n"
            "    lab.update_param('hidden_neurons', neurons)\n"
            "    stats = lab.fast_forward_generations(30)\n"
            "    print(f\"Hidden Neurons: {neurons:2d} -> Accuracy: {stats['best_fitness']:5.1f}% | Loss: {stats['avg_fitness']:.4f}\")\n"
        )
    },
    {
        "id": "lesson_5_2",
        "track": "Track 5: Neural Networks (Backprop)",
        "title": "5.2 Conquering the Spiral Challenge",
        "grade_level": "Ages 12+ / Intermediate",
        "lab_id": "nn_playground",
        "badge": "🌀 Spiral Master",
        "story": (
            "The Archimedean Spiral (Dataset = 3) is one of the toughest 2D tests for a small neural network! "
            "You'll need enough Hidden Layer Neurons (12–16) and a well-tuned Learning Rate to untangle the spiral."
        ),
        "steps": [
            "1. Click '🎯 Load Lesson Preset' to load the Spiral dataset with 14 Hidden Neurons.",
            "2. Click '⚡ Turbo +25 Gens' twice to train 500+ epochs of backpropagation.",
            "3. Reach >= 82% accuracy on the Spiral and click '✅ Check Mission Goal'!"
        ],
        "preset_params": {
            "dataset_id": 3.0,
            "hidden_neurons": 16.0,
            "learning_rate": 0.45,
            "l2_reg": 0.0005,
            "noise": 0.03,
            "steps_per_frame": 15.0
        },
        "goal_metric": "best_ever",
        "goal_op": ">=",
        "goal_target": 82.0,
        "goal_desc": "Achieve >= 82.0% accuracy on the Archimedean Spiral dataset",
        "coding_challenge": (
            "# 🎯 HANDS-ON CODING CHALLENGE 5.2:\n"
            "# Build a tiny neuron forward pass from scratch using math.tanh!\n\n"
            "import math\n\n"
            "def single_neuron(x, y, w_x, w_y, bias):\n"
            "    z = (x * w_x) + (y * w_y) + bias\n"
            "    return math.tanh(z)\n\n"
            "print('Neuron output for (1.0, 2.0):', round(single_neuron(1.0, 2.0, 0.8, -0.5, 0.1), 4))\n"
        )
    },

    # ==========================================================================
    # TRACK 6: NATURE'S ALGORITHMS & LINUX AI CODER
    # ==========================================================================
    {
        "id": "lesson_6_1",
        "track": "Track 6: Swarm & Linux Mastery",
        "title": "6.1 Predator-Prey Swarm Co-Evolution",
        "grade_level": "Ages 9+ / All Levels",
        "lab_id": "swarm_ecosystem",
        "badge": "🧬 Ecosystem Guardian",
        "story": (
            "In nature, starlings and fish don't have a leader—yet thousands of them move like one giant brain! "
            "Watch blue Prey evolve teamwork and predator dodging to eat green energy dots while red Predators chase them."
        ),
        "steps": [
            "1. Click '🎯 Load Lesson Preset' to launch the Predator-Prey Swarm Ecosystem.",
            "2. Increase 'Sensory Vision (px)' to 110 so prey spot red predators from farther away.",
            "3. Click '⚡ Turbo +25 Gens' and reach a Best Prey Score >= 200!"
        ],
        "preset_params": {
            "num_prey": 40.0,
            "num_predators": 4.0,
            "vision_radius": 110.0,
            "prey_speed": 4.2,
            "predator_speed": 4.0,
            "food_count": 32.0,
            "mutation_sigma": 0.20
        },
        "goal_metric": "best_ever",
        "goal_op": ">=",
        "goal_target": 200.0,
        "goal_desc": "Evolve a Prey flock with Best Survival Score >= 200.0",
        "coding_challenge": (
            "# 🎯 HANDS-ON CODING CHALLENGE 6.1:\n"
            "# Evolve the Predator-Prey Swarm and inspect the winning Prey's 4 evolved genes!\n\n"
            "from workbench.labs.swarm_ecosystem import SwarmEcosystemLab\n\n"
            "lab = SwarmEcosystemLab()\n"
            "stats = lab.fast_forward_generations(8)\n"
            "genes = stats['top_prey_genes']\n"
            "print('Champion Prey Score:', stats['best_ever'])\n"
            "print(f'Evolved Genes -> Food Drive: {genes[0]}, Evasion: {genes[1]}, Cohesion: {genes[2]}, Separation: {genes[3]}')\n"
        )
    },
    {
        "id": "lesson_6_2",
        "track": "Track 6: Swarm & Linux Mastery",
        "title": "6.2 Linux & Cortex AI Power User Quest",
        "grade_level": "Ages 10+ / All Levels",
        "lab_id": "moon_lander",
        "badge": "🐧 Linux AI Wizard",
        "story": (
            "You are running on SynapseOS—a real Linux operating system built for AI scientists! "
            "Whenever you want to know how to do something in Linux, you can ask Cortex at the bottom "
            "of this window (or type `??` in the terminal)."
        ),
        "steps": [
            "1. Switch to the '✏️ Hands-On Coding' tab on the right.",
            "2. Click '▶ Run My Code' to query the Cortex SQLite FTS5 Knowledge Base directly from Python!",
            "3. Or type a Linux question in the Cortex bar at the bottom and click '🐧 Linux Cmd (??)'."
        ],
        "preset_params": {
            "gravity": 1.62,
            "wind": 0.0,
            "fuel_capacity": 150.0,
            "pop_size": 50.0,
            "conn_add_prob": 0.18,
            "node_add_prob": 0.06,
            "weight_mutate_power": 0.60,
            "landing_bonus": 240.0
        },
        "goal_metric": "generation",
        "goal_op": ">=",
        "goal_target": 1.0,
        "goal_desc": "Explore Cortex Linux & AI Knowledge Base from Python",
        "coding_challenge": (
            "# 🎯 HANDS-ON CODING CHALLENGE 6.2:\n"
            "# Query your built-in Cortex SQLite FTS5 Knowledge Base in < 1 millisecond!\n\n"
            "from cortex.engine import CortexEngine\n\n"
            "engine = CortexEngine()\n"
            "cmd_info = engine.synthesize_command_and_instructions('boost ram on a potato with zram')\n"
            "print('🐧 Linux Task:', cmd_info['summary'])\n"
            "print('💡 Command:   ', cmd_info['command'])\n"
            "print('⚡ Speed:     ', cmd_info.get('source'))\n"
        )
    },
    # ==========================================================================
    # TRACK 7: PRIME MOMENT SLIDING-WINDOW ATTENTION (O(1) MEMORY VAULT)
    # ==========================================================================
    {
        "id": "lesson_7_1",
        "track": "Track 7: PRIME Moment Attention (O(1) Memory)",
        "title": "7.1 Solving Sliding-Window Amnesia with the PRIME Vault",
        "grade_level": "Ages 11+ / All Levels",
        "lab_id": "prime_attention",
        "badge": "🔑 Vault Keeper",
        "story": (
            "Normal AI chatbots either run out of RAM on long conversations (Softmax keeps every word in a giant 288,000 KB table) "
            "or forget old words as soon as they leave a small Sliding Window! PRIME Moment Attention fixes this: right before "
            "a secret passkey ('7492') falls out of the Sliding Window, it compresses it into a tiny 67 KB Memory Vault (S0, S1, S2)!"
        ),
        "steps": [
            "1. Click '▸ 1. Load Preset' to open Lab 7 (Window W=64, Passkey Gap N=256).",
            "2. Watch the animated token conveyor belt: even after 'KEY:7492' leaves the blue Window, the green PRIME Vault remembers it (88%+ recall)!",
            "3. Try dragging 'Window vs PRIME Blend' to 1.0 (Window Only) to see recall drop to 0%, then set it back to 0.45.",
            "4. Click '✓ 2. Check Goal' with Hybrid Recall >= 80%!"
        ],
        "preset_params": {
            "window_size": 64.0,
            "decay": 0.9990,
            "alpha": 0.45,
            "head_dim": 32.0,
            "use_qk_norm": 1.0,
            "distractor_gap": 256.0,
            "num_heads": 8.0,
        },
        "goal_metric": "best_fitness",
        "goal_op": ">=",
        "goal_target": 80.0,
        "goal_desc": "Achieve >= 80% Passkey Recall across a 256-token distractor gap using Hybrid PRIME Attention",
        "coding_challenge": (
            "# 🎯 HANDS-ON CODING CHALLENGE 7.1:\n"
            "# Benchmark the native C99 PRIME Moment Attention kernel on this CPU!\n\n"
            "from cortex.prime_window import benchmark_c_prime_engine\n\n"
            "res = benchmark_c_prime_engine(num_heads=8, head_dim=64, steps=1000)\n"
            "print('Engine Backend: ', res['backend'])\n"
            "print(f\"Decode Speed:   {res['tokens_per_sec']:,.1f} tokens/sec\")\n"
            "print('O(1) State RAM: 67.1 KB (vs 288,000 KB Softmax KV-Cache)')\n"
        )
    },
    {
        "id": "lesson_7_2",
        "track": "Track 7: PRIME Moment Attention (O(1) Memory)",
        "title": "7.2 Why QK-Norm Stops Parabolic Explosion",
        "grade_level": "Ages 12+ / Intermediate",
        "lab_id": "prime_attention",
        "badge": "⚡ Taylor Stabilizer",
        "story": (
            "PRIME approximates exponential attention exp(x) with a 2nd-order Taylor polynomial P(x) = 1 + x + 0.5*x^2. "
            "Without QK-Norm, large negative numbers (x < -2) bounce back up like a parabola and drown out the passkey! "
            "Turning QK-Norm ON keeps |x| <= 1.0 so the vault stays crystal clear even at 1,024 tokens."
        ),
        "steps": [
            "1. Click '▸ 1. Load Preset' (sets Passkey Gap N=512 and QK-Norm=1).",
            "2. Toggle 'QK-Norm' slider to 0 to see the red warning and watch recall collapse, then turn QK-Norm back to 1!",
            "3. Click '✓ 2. Check Goal' with Recall >= 70% at Gap=512!"
        ],
        "preset_params": {
            "window_size": 64.0,
            "decay": 0.9993,
            "alpha": 0.35,
            "head_dim": 32.0,
            "use_qk_norm": 1.0,
            "distractor_gap": 512.0,
            "num_heads": 8.0,
        },
        "goal_metric": "best_fitness",
        "goal_op": ">=",
        "goal_target": 70.0,
        "goal_desc": "Maintain >= 70% Passkey Recall at a 512-token gap with QK-Norm active",
        "coding_challenge": (
            "# 🎯 HANDS-ON CODING CHALLENGE 7.2:\n"
            "# Compare Taylor polynomial P(x) = 1 + x + 0.5*x^2 with and without QK-Norm!\n\n"
            "def taylor_p(x):\n"
            "    return 1.0 + x + 0.5 * (x ** 2)\n\n"
            "print('Bounded QK-Norm (x = -0.8): ', round(taylor_p(-0.8), 3), ' (Small, quiet distractor)')\n"
            "print('Unbounded Raw   (x = -4.0): ', round(taylor_p(-4.0), 3), ' (Explodes to +5.0 parabolic rebound!)')\n"
        )
    }
]


# ==============================================================================
# 35 INTERACTIVE LAB EXAMPLES / PRESETS (5 FOR EACH OF THE 7 AI LABS)
# ==============================================================================
LAB_EXAMPLES: Dict[str, List[Dict[str, Any]]] = {
    "moon_lander": [
        {
            "id": "ml_ex1",
            "title": "Ex 1: Apollo 11 Calm Moon Landing (g=1.62)",
            "desc": "Standard lunar gravity (1.62 m/s²), zero wind, 60 rockets evolving soft touchdown.",
            "params": {"gravity": 1.62, "wind": 0.0, "fuel_capacity": 160.0, "pop_size": 60.0, "conn_add_prob": 0.18, "node_add_prob": 0.06, "weight_mutate_power": 0.60, "landing_bonus": 240.0, "thruster_power": 1.65, "target_hidden": 1.0},
        },
        {
            "id": "ml_ex2",
            "title": "Ex 2: Mars Gale-Force Crosswind (g=3.72, Wind=+0.85)",
            "desc": "Strong sideways Martian dust storm! Rockets must tilt into the wind and fire side thrusters.",
            "params": {"gravity": 3.72, "wind": 0.85, "fuel_capacity": 220.0, "pop_size": 70.0, "conn_add_prob": 0.24, "node_add_prob": 0.10, "weight_mutate_power": 0.65, "landing_bonus": 320.0, "thruster_power": 1.95, "target_hidden": 3.0},
        },
        {
            "id": "ml_ex3",
            "title": "Ex 3: Deep 8-Neuron Brain Topology (+8 Hidden)",
            "desc": "Starts with 8 hidden neurons pre-grown in the middle layer for complex multi-thruster coordination.",
            "params": {"gravity": 2.10, "wind": -0.45, "fuel_capacity": 180.0, "pop_size": 60.0, "conn_add_prob": 0.35, "node_add_prob": 0.20, "weight_mutate_power": 0.55, "landing_bonus": 280.0, "thruster_power": 1.75, "target_hidden": 8.0},
        },
        {
            "id": "ml_ex4",
            "title": "Ex 4: Earth Heavy Booster Recovery (g=9.8, High Thrust)",
            "desc": "Full Earth gravity (9.8 m/s²) SpaceX-style suicide burn requiring high thrust (2.4x) and fast reflexes.",
            "params": {"gravity": 9.80, "wind": 0.15, "fuel_capacity": 280.0, "pop_size": 80.0, "conn_add_prob": 0.22, "node_add_prob": 0.08, "weight_mutate_power": 0.70, "landing_bonus": 360.0, "thruster_power": 2.40, "target_hidden": 4.0},
        },
        {
            "id": "ml_ex5",
            "title": "Ex 5: Low-Fuel Precision Touchdown (Fuel=70)",
            "desc": "Scarcity challenge: only 70 fuel units! Rockets that hover wastefully run dry and crash.",
            "params": {"gravity": 1.40, "wind": 0.0, "fuel_capacity": 70.0, "pop_size": 70.0, "conn_add_prob": 0.20, "node_add_prob": 0.07, "weight_mutate_power": 0.50, "landing_bonus": 390.0, "thruster_power": 1.70, "target_hidden": 2.0},
        },
    ],
    "raycast_car": [
        {
            "id": "rc_ex1",
            "title": "Ex 1: Highway Cruiser (Wide Lane, 150px Lidar)",
            "desc": "Generous 44px road corridor with long 150px laser lookahead for smooth beginner cornering.",
            "params": {"sensor_range": 150.0, "max_speed": 4.5, "turn_rate": 0.09, "track_width": 44.0, "pop_size": 40.0, "conn_add_prob": 0.16, "node_add_prob": 0.05, "weight_mutate_power": 0.55, "target_hidden": 1.0},
        },
        {
            "id": "rc_ex2",
            "title": "Ex 2: Formula-1 Narrow Track Sprint (Speed=7.5)",
            "desc": "Blistering 7.5 px/frame top speed on a tight 28px Monaco-style corridor with high steering agility.",
            "params": {"sensor_range": 190.0, "max_speed": 7.5, "turn_rate": 0.13, "track_width": 28.0, "pop_size": 50.0, "conn_add_prob": 0.22, "node_add_prob": 0.08, "weight_mutate_power": 0.50, "target_hidden": 3.0},
        },
        {
            "id": "rc_ex3",
            "title": "Ex 3: Foggy Night Short-Range Lidar (Range=60px)",
            "desc": "Cars can only see 60px ahead in thick fog and must rely on sharp 0.14 turn reflexes.",
            "params": {"sensor_range": 60.0, "max_speed": 3.8, "turn_rate": 0.14, "track_width": 36.0, "pop_size": 50.0, "conn_add_prob": 0.25, "node_add_prob": 0.10, "weight_mutate_power": 0.65, "target_hidden": 4.0},
        },
        {
            "id": "rc_ex4",
            "title": "Ex 4: Deep 8-Neuron Autonomous Brain (+8 Hidden)",
            "desc": "Pre-wires 8 hidden neurons so cars evolve smooth throttle modulation before sharp hairpins.",
            "params": {"sensor_range": 165.0, "max_speed": 6.0, "turn_rate": 0.11, "track_width": 34.0, "pop_size": 45.0, "conn_add_prob": 0.35, "node_add_prob": 0.18, "weight_mutate_power": 0.55, "target_hidden": 8.0},
        },
        {
            "id": "rc_ex5",
            "title": "Ex 5: 100-Car Rush Hour Mega-Fleet (Pop=100)",
            "desc": "Massive 100-car simultaneous neuroevolution population racing for the fastest lap.",
            "params": {"sensor_range": 140.0, "max_speed": 5.5, "turn_rate": 0.10, "track_width": 38.0, "pop_size": 100.0, "conn_add_prob": 0.20, "node_add_prob": 0.06, "weight_mutate_power": 0.60, "target_hidden": 2.0},
        },
    ],
    "rl_gridworld": [
        {
            "id": "rl_ex1",
            "title": "Ex 1: Bold Q-Learning Cliff Walker (Off-Policy)",
            "desc": "Zero wind + off-policy Q-Learning: learns the shortest path hugging the edge of the lava cliff.",
            "params": {"alpha": 0.35, "gamma": 0.96, "epsilon": 0.10, "goal_reward": 140.0, "lava_penalty": -100.0, "step_penalty": -1.0, "wind_prob": 0.0, "use_sarsa": 0.0, "max_ep_steps": 90.0},
        },
        {
            "id": "rl_ex2",
            "title": "Ex 2: Cautious SARSA in 20% Stormy Wind (On-Policy)",
            "desc": "On-policy SARSA accounts for random wind slips and learns a safe upper detour away from lava!",
            "params": {"alpha": 0.28, "gamma": 0.96, "epsilon": 0.12, "goal_reward": 160.0, "lava_penalty": -140.0, "step_penalty": -0.8, "wind_prob": 0.20, "use_sarsa": 1.0, "max_ep_steps": 110.0},
        },
        {
            "id": "rl_ex3",
            "title": "Ex 3: Hyper-Curious Explorer (Epsilon=0.45, Alpha=0.6)",
            "desc": "High 45% random curiosity explores every corner of the maze rapidly.",
            "params": {"alpha": 0.60, "gamma": 0.92, "epsilon": 0.45, "goal_reward": 150.0, "lava_penalty": -80.0, "step_penalty": -1.2, "wind_prob": 0.05, "use_sarsa": 0.0, "max_ep_steps": 100.0},
        },
        {
            "id": "rl_ex4",
            "title": "Ex 4: Myopic Short-Sighted Agent (Gamma=0.55)",
            "desc": "Low discount factor (γ=0.55) makes distant treasure barely visible until the agent is right next to it.",
            "params": {"alpha": 0.35, "gamma": 0.55, "epsilon": 0.15, "goal_reward": 200.0, "lava_penalty": -100.0, "step_penalty": -0.5, "wind_prob": 0.0, "use_sarsa": 0.0, "max_ep_steps": 90.0},
        },
        {
            "id": "rl_ex5",
            "title": "Ex 5: High-Stakes Lava Gauntlet (Lava=-250, Goal=+300)",
            "desc": "Massive lava punishment (-250) and high step penalty (-3.0) force ultra-efficient pathfinding.",
            "params": {"alpha": 0.30, "gamma": 0.98, "epsilon": 0.08, "goal_reward": 300.0, "lava_penalty": -250.0, "step_penalty": -3.0, "wind_prob": 0.10, "use_sarsa": 1.0, "max_ep_steps": 80.0},
        },
    ],
    "cartpole_rl": [
        {
            "id": "cp_ex1",
            "title": "Ex 1: Earth Standard Pendulum (g=9.8, L=0.65m)",
            "desc": "Classic OpenAI Gym CartPole benchmark under standard Earth gravity.",
            "params": {"gravity": 9.8, "pole_length": 0.65, "force_mag": 12.0, "wind_gust": 0.15, "pop_size": 35.0, "conn_add_prob": 0.15, "node_add_prob": 0.05, "weight_mutate_power": 0.45, "target_hidden": 1.0},
        },
        {
            "id": "cp_ex2",
            "title": "Ex 2: Jupiter Crushing Gravity (g=22.0, Force=24N)",
            "desc": "2.25x Earth gravity! The pole falls violently fast unless the cart motor fires at 24 Newtons.",
            "params": {"gravity": 22.0, "pole_length": 0.70, "force_mag": 24.0, "wind_gust": 0.20, "pop_size": 50.0, "conn_add_prob": 0.22, "node_add_prob": 0.08, "weight_mutate_power": 0.55, "target_hidden": 3.0},
        },
        {
            "id": "cp_ex3",
            "title": "Ex 3: Twitchy Short Pencil Balance (Length=0.25m)",
            "desc": "A tiny 25cm pencil has very low rotational inertia and requires lightning-fast micro-corrections.",
            "params": {"gravity": 9.8, "pole_length": 0.25, "force_mag": 14.0, "wind_gust": 0.10, "pop_size": 45.0, "conn_add_prob": 0.20, "node_add_prob": 0.07, "weight_mutate_power": 0.50, "target_hidden": 2.0},
        },
        {
            "id": "cp_ex4",
            "title": "Ex 4: Hurricane Gust Survival (Wind=1.8, +6 Neurons)",
            "desc": "Heavy random wind torque buffets the pole every frame; uses 6 hidden neurons for recovery.",
            "params": {"gravity": 9.8, "pole_length": 0.60, "force_mag": 18.0, "wind_gust": 1.80, "pop_size": 55.0, "conn_add_prob": 0.28, "node_add_prob": 0.12, "weight_mutate_power": 0.60, "target_hidden": 6.0},
        },
        {
            "id": "cp_ex5",
            "title": "Ex 5: Lunar Slow-Motion Giant Pole (g=1.62, L=1.65m)",
            "desc": "Low Moon gravity with a tall 1.65m pole creates graceful slow-motion balancing dynamics.",
            "params": {"gravity": 1.62, "pole_length": 1.65, "force_mag": 7.0, "wind_gust": 0.30, "pop_size": 30.0, "conn_add_prob": 0.14, "node_add_prob": 0.05, "weight_mutate_power": 0.40, "target_hidden": 0.0},
        },
    ],
    "nn_playground": [
        {
            "id": "nn_ex1",
            "title": "Ex 1: Concentric Rings (8 Neurons, Fast Convergence)",
            "desc": "Separates an inner blue circle from an outer orange ring in <100 epochs.",
            "params": {"dataset_id": 1.0, "hidden_neurons": 8.0, "learning_rate": 0.22, "l2_reg": 0.001, "noise": 0.05, "steps_per_frame": 6.0, "activation_gain": 1.2, "synapse_density": 4.0},
        },
        {
            "id": "nn_ex2",
            "title": "Ex 2: Classic XOR Quadrants (4 Neurons, Non-Linear)",
            "desc": "Minsky & Papert's famous 1969 XOR puzzle solved cleanly by 4 hidden neurons.",
            "params": {"dataset_id": 0.0, "hidden_neurons": 4.0, "learning_rate": 0.25, "l2_reg": 0.001, "noise": 0.04, "steps_per_frame": 6.0, "activation_gain": 1.4, "synapse_density": 4.0},
        },
        {
            "id": "nn_ex3",
            "title": "Ex 3: Two Interleaving Moons (10 Neurons, Sharp Boundary)",
            "desc": "Curves a S-shaped decision boundary between two crescent moons.",
            "params": {"dataset_id": 2.0, "hidden_neurons": 10.0, "learning_rate": 0.24, "l2_reg": 0.0005, "noise": 0.06, "steps_per_frame": 8.0, "activation_gain": 1.8, "synapse_density": 3.0},
        },
        {
            "id": "nn_ex4",
            "title": "Ex 4: Archimedean Double Spiral (18 Neurons, Deep MLP)",
            "desc": "High-capacity 18-neuron hidden layer untangling the intertwined double spiral.",
            "params": {"dataset_id": 3.0, "hidden_neurons": 18.0, "learning_rate": 0.28, "l2_reg": 0.0005, "noise": 0.02, "steps_per_frame": 12.0, "activation_gain": 2.2, "synapse_density": 4.0},
        },
        {
            "id": "nn_ex5",
            "title": "Ex 5: Under-Parameterized 1-Neuron Bottleneck (1 Neuron)",
            "desc": "Shows why 1 neuron fails on Rings—then click '[+ Add Neuron]' on the left to watch it solve it live!",
            "params": {"dataset_id": 1.0, "hidden_neurons": 1.0, "learning_rate": 0.20, "l2_reg": 0.001, "noise": 0.05, "steps_per_frame": 6.0, "activation_gain": 1.0, "synapse_density": 2.0},
        },
    ],
    "swarm_ecosystem": [
        {
            "id": "sw_ex1",
            "title": "Ex 1: Balanced Starling Murmuration (40 Prey, 4 Pred)",
            "desc": "Harmonious co-evolution of flocking cohesion, foraging, and predator dodging.",
            "params": {"num_prey": 40.0, "num_predators": 4.0, "vision_radius": 95.0, "prey_speed": 4.2, "predator_speed": 4.0, "food_count": 32.0, "mutation_sigma": 0.20},
        },
        {
            "id": "sw_ex2",
            "title": "Ex 2: Apex Wolfpack Ambush (10 Fast Predators)",
            "desc": "10 high-speed predators force prey to evolve extreme evasion and tight separation.",
            "params": {"num_prey": 50.0, "num_predators": 10.0, "vision_radius": 125.0, "prey_speed": 5.2, "predator_speed": 5.0, "food_count": 40.0, "mutation_sigma": 0.30},
        },
        {
            "id": "sw_ex3",
            "title": "Ex 3: 75-Prey Mega-Swarm Super-Organism",
            "desc": "Massive 75-agent prey school with 145px long-range sensory vision.",
            "params": {"num_prey": 75.0, "num_predators": 3.0, "vision_radius": 145.0, "prey_speed": 4.5, "predator_speed": 4.2, "food_count": 55.0, "mutation_sigma": 0.15},
        },
        {
            "id": "sw_ex4",
            "title": "Ex 4: Famine Desert Foraging (Only 10 Food Nodes)",
            "desc": "Severe resource scarcity where only the most aggressive food-seeking genotypes survive.",
            "params": {"num_prey": 30.0, "num_predators": 2.0, "vision_radius": 130.0, "prey_speed": 4.8, "predator_speed": 3.8, "food_count": 10.0, "mutation_sigma": 0.40},
        },
        {
            "id": "sw_ex5",
            "title": "Ex 5: Hyper-Speed Blitz Ecosystem (Speed=6.2)",
            "desc": "Maximum velocity pursuit and evasion with rapid evolutionary turnover.",
            "params": {"num_prey": 45.0, "num_predators": 6.0, "vision_radius": 110.0, "prey_speed": 6.2, "predator_speed": 6.0, "food_count": 35.0, "mutation_sigma": 0.25},
        },
    ],
    "prime_attention": [
        {
            "id": "pa_ex1",
            "title": "Ex 1: Hybrid Window + PRIME Vault (W=64, Gap=256 -> 88%)",
            "desc": "Passkey '7492' leaves the 64-token window but is recalled from the 67 KB O(1) PRIME Moment Vault!",
            "params": {"window_size": 64.0, "decay": 0.9990, "alpha": 0.45, "head_dim": 32.0, "use_qk_norm": 1.0, "distractor_gap": 256.0, "num_heads": 8.0},
        },
        {
            "id": "pa_ex2",
            "title": "Ex 2: Window-Only Amnesia Trap (Alpha=1.0 -> 0% Recall!)",
            "desc": "Pure Sliding Window without PRIME: as soon as Passkey '7492' steps past W=64, it is 100% forgotten!",
            "params": {"window_size": 64.0, "decay": 0.9990, "alpha": 1.00, "head_dim": 32.0, "use_qk_norm": 1.0, "distractor_gap": 256.0, "num_heads": 8.0},
        },
        {
            "id": "pa_ex3",
            "title": "Ex 3: Deep 1024-Token Long-Horizon Vault (Decay=0.9995)",
            "desc": "High λ=0.9995 retention horizon preserves the passkey across 1,024 distractor tokens in O(1) RAM.",
            "params": {"window_size": 64.0, "decay": 0.9995, "alpha": 0.30, "head_dim": 64.0, "use_qk_norm": 1.0, "distractor_gap": 1024.0, "num_heads": 16.0},
        },
        {
            "id": "pa_ex4",
            "title": "Ex 4: QK-Norm OFF Parabolic Rebound Crash (QK-Norm=0)",
            "desc": "Demonstrates why 2nd-order Taylor attention fails without QK-Norm: negative logits rebound and drown S2!",
            "params": {"window_size": 32.0, "decay": 0.9985, "alpha": 0.25, "head_dim": 32.0, "use_qk_norm": 0.0, "distractor_gap": 256.0, "num_heads": 8.0},
        },
        {
            "id": "pa_ex5",
            "title": "Ex 5: Ultra-Light 9 KB L2-Cache Potato Config (D=16, 4H)",
            "desc": "4 heads x 16-dim uses just 8.8 KB of L2 cache while running at 8,700+ tok/s in native C99.",
            "params": {"window_size": 48.0, "decay": 0.9990, "alpha": 0.40, "head_dim": 16.0, "use_qk_norm": 1.0, "distractor_gap": 128.0, "num_heads": 4.0},
        },
    ],
}


from workbench.k12_curricula import (
    K12_YEAR_PACKS,
    get_all_k12_subject_lessons,
    get_all_k12_lessons_with_quarters,
    get_subject_lessons_for_year,
)

ALL_CURRICULUM_LESSONS: List[Dict[str, Any]] = list(SCHOOL_CURRICULUM) + get_all_k12_lessons_with_quarters()


def get_examples_for_lab(lab_id: str) -> List[Dict[str, Any]]:
    return LAB_EXAMPLES.get(lab_id, LAB_EXAMPLES["moon_lander"])


def get_curriculum_for_year(year_num: int = 1, include_quarters: bool = True) -> List[Dict[str, Any]]:
    """
    Return the active school year's 5 Core Subject Courses (Math, Science, Reading/ELA,
    Social Studies/History, AI & Coding) + 20 Quarterly Unit Lessons (Q1-Q4), followed
    by the Core AI Lab Track missions.
    """
    year_subjects = get_subject_lessons_for_year(year_num, include_quarters=include_quarters)
    return list(year_subjects) + list(SCHOOL_CURRICULUM)


def get_lesson_by_id(lesson_id: str) -> Dict[str, Any]:
    for lesson in ALL_CURRICULUM_LESSONS:
        if lesson["id"] == lesson_id:
            return lesson
    return SCHOOL_CURRICULUM[0]


def get_lessons_for_lab(lab_id: str):
    """Return all curriculum lessons targeting a specific AI lab."""
    return [lesson for lesson in ALL_CURRICULUM_LESSONS if lesson["lab_id"] == lab_id]


def verify_lesson_goal(lesson: Dict[str, Any], telemetry: Dict[str, Any]) -> Tuple[bool, str]:
    """Check if the student's current simulation telemetry satisfies the lesson's mission goal."""
    metric_key = lesson["goal_metric"]
    target_val = float(lesson["goal_target"])
    actual_val = float(telemetry.get(metric_key, 0.0))

    passed = actual_val >= target_val if lesson["goal_op"] == ">=" else actual_val <= target_val
    if passed:
        return True, (
            f"🎉 MISSION ACCOMPLISHED! You earned the [{lesson['badge']}] badge!\n"
            f"   Your {metric_key} reached {actual_val} (Goal: {lesson['goal_op']} {target_val})."
        )
    return False, (
        f"⏳ Keep experimenting! Current {metric_key} = {actual_val} "
        f"(Goal: {lesson['goal_op']} {target_val}).\n"
        f"   Tip: Click '🎯 Load Lesson Preset' and then '⚡ Turbo +25 Gens'!"
    )

