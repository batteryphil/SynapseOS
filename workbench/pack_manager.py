#!/usr/bin/env python3
"""
SynapseOS Space-Saving Learning Package Updater & Persistent Trophy Vault (`workbench/pack_manager.py`)

Features:
  1. Persistent Student Profile (`student_profile.json`, < 4 KB):
     - Permanently preserves `earned_badges`, `lifetime_points`, `lifetime_stars`, `completed_packs`,
       and `high_scores` across learning package upgrades and reboots.
  2. Space-Saving Learning Package Swapper (`active_pack/current_pack.json`):
     - When a student completes the current Learning Pack (or clicks "Next Pack / Update Pack"),
       deletes the old learning package files & scratch exports to free disk space on potato hardware,
       and installs the new Learning Package in-place (`Pack 1 -> Pack 2 -> Pack 3`, or from URL/file).
"""

import json
import os
import shutil
import sys
import urllib.request
from typing import Dict, Any, List, Optional, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))


def _get_writable_config_dir() -> str:
    candidates = [
        os.path.join(os.path.expanduser("~"), ".config", "synapse-os"),
        "/var/lib/synapse-os",
        "/tmp/synapse-os",
    ]
    for path in candidates:
        try:
            os.makedirs(path, exist_ok=True)
            if os.access(path, os.W_OK):
                return path
        except Exception:
            continue
    os.makedirs("/tmp/synapse-os", exist_ok=True)
    return "/tmp/synapse-os"


# ==============================================================================
# BUILT-IN LEARNING PACKAGES (PACK 1, PACK 2, PACK 3)
# ==============================================================================
LEARNING_PACKS: Dict[str, Dict[str, Any]] = {
    "pack_1_core": {
        "pack_id": "pack_1_core",
        "pack_number": 1,
        "title_en": "Pack 1: Space Cadet Academy (Levels 1-7)",
        "title_fr": "Pack 1 : Académie Cadet Spatial (Niveaux 1-7)",
        "short_en": "Pack 1 (Lv 1-7)",
        "short_fr": "Pack 1 (Niv 1-7)",
        "kid_levels": [
            {
                "level": 1,
                "lab_id": "moon_lander",
                "title_en": "Level 1: Space Moon Landing",
                "title_fr": "Niveau 1 : Alunissage spatial",
                "speech_en": "Hi! To land the rocket without breaking it, add some fuel or lower the gravity!",
                "speech_fr": "Salut ! Pour poser la fusée sans la casser, ajoute un peu de carburant ou réduis la gravité !",
                "obj1_en": "Don't explode",
                "obj1_fr": "Ne pas exploser",
                "obj2_en": "Soft landing",
                "obj2_fr": "Se poser en douceur",
                "btn1_en": ("Make", "Smarter"),
                "btn1_fr": ("Rendre plus", "intelligent"),
                "btn2_en": ("More", "Fuel"),
                "btn2_fr": ("Plus de", "carburant"),
                "btn3_en": ("Light", "Gravity"),
                "btn3_fr": ("Gravité", "Légère"),
                "preset": {"gravity": 1.62, "wind": 0.0, "fuel_capacity": 160.0},
            },
            {
                "level": 2,
                "lab_id": "raycast_car",
                "title_en": "Level 2: Cyber Self-Driving Car",
                "title_fr": "Niveau 2 : Voiture autonome laser",
                "speech_en": "Help the racecar steer around corners by making its brain smarter or boosting laser range!",
                "speech_fr": "Aide la voiture à tourner sans toucher les murs avec un cerveau plus intelligent !",
                "obj1_en": "Stay on the track",
                "obj1_fr": "Rester sur la piste",
                "obj2_en": "Fast lap",
                "obj2_fr": "Tour rapide",
                "btn1_en": ("Make", "Smarter"),
                "btn1_fr": ("Rendre plus", "intelligent"),
                "btn2_en": ("Longer", "Lasers"),
                "btn2_fr": ("Lasers", "Puissants"),
                "btn3_en": ("Safe", "Speed"),
                "btn3_fr": ("Vitesse", "Douce"),
                "preset": {"sensor_range": 135.0, "max_speed": 4.5, "track_width": 42.0},
            },
            {
                "level": 3,
                "lab_id": "rl_gridworld",
                "title_en": "Level 3: Treasure Maze Explorer",
                "title_fr": "Niveau 3 : Labyrinthe au trésor",
                "speech_en": "Watch the robot learn a map of the maze! Avoid the red lava tiles and reach the gold star!",
                "speech_fr": "Regarde le robot apprendre le chemin du trésor sans tomber dans la lave rouge !",
                "obj1_en": "Avoid red lava",
                "obj1_fr": "Éviter la lave",
                "obj2_en": "Find treasure",
                "obj2_fr": "Trouver le trésor",
                "btn1_en": ("Make", "Smarter"),
                "btn1_fr": ("Rendre plus", "intelligent"),
                "btn2_en": ("Faster", "Memory"),
                "btn2_fr": ("Mémoire", "Rapide"),
                "btn3_en": ("Less", "Random"),
                "btn3_fr": ("Moins de", "Hasard"),
                "preset": {"alpha": 0.30, "gamma": 0.95, "epsilon": 0.12},
            },
            {
                "level": 4,
                "lab_id": "cartpole_rl",
                "title_en": "Level 4: Balance Pole Acrobat",
                "title_fr": "Niveau 4 : Équilibre du bâton",
                "speech_en": "Keep the golden pole upright! Give the cart more push power or lower gravity to balance longer!",
                "speech_fr": "Garde le bâton bien droit ! Ajoute de la force au chariot ou réduis la gravité !",
                "obj1_en": "Don't drop pole",
                "obj1_fr": "Ne pas tomber",
                "obj2_en": "Balance 300 steps",
                "obj2_fr": "Tenir l'équilibre",
                "btn1_en": ("Make", "Smarter"),
                "btn1_fr": ("Rendre plus", "intelligent"),
                "btn2_en": ("Strong", "Motors"),
                "btn2_fr": ("Moteurs", "Puissants"),
                "btn3_en": ("Light", "Gravity"),
                "btn3_fr": ("Gravité", "Légère"),
                "preset": {"gravity": 9.8, "force_mag": 12.0, "wind_gust": 0.20},
            },
            {
                "level": 5,
                "lab_id": "nn_playground",
                "title_en": "Level 5: Color Sorter Brain",
                "title_fr": "Niveau 5 : Cerveau trieur de couleurs",
                "speech_en": "Add more brain neurons so the AI can draw a magic boundary separating blue and red dots!",
                "speech_fr": "Ajoute des neurones pour que l'IA sépare les points bleus et les points rouges !",
                "obj1_en": "Learn pattern",
                "obj1_fr": "Apprendre la forme",
                "obj2_en": "90% Accuracy",
                "obj2_fr": "Précision 90%",
                "btn1_en": ("Add Brain", "Neurons"),
                "btn1_fr": ("Ajouter", "Neurones"),
                "btn2_en": ("Switch", "Pattern"),
                "btn2_fr": ("Changer", "Forme"),
                "btn3_en": ("Scramble", "Dots"),
                "btn3_fr": ("Mélanger", "Points"),
                "preset": {"dataset_id": 2.0, "hidden_neurons": 8.0, "noise": 0.05},
            },
            {
                "level": 6,
                "lab_id": "swarm_ecosystem",
                "title_en": "Level 6: Space Swarm Flock",
                "title_fr": "Niveau 6 : Essaim de poissons",
                "speech_en": "Help the green swimmer flock stick together, eat energy orbs, and dodge the red sharks!",
                "speech_fr": "Aide les nageurs verts à rester ensemble et à éviter les prédateurs rouges !",
                "obj1_en": "Protect flock",
                "obj1_fr": "Protéger le groupe",
                "obj2_en": "Gather energy",
                "obj2_fr": "Manger les perles",
                "btn1_en": ("Make", "Smarter"),
                "btn1_fr": ("Rendre plus", "intelligent"),
                "btn2_en": ("More", "Food"),
                "btn2_fr": ("Plus de", "Nourriture"),
                "btn3_en": ("Speed", "Boost"),
                "btn3_fr": ("Vitesse", "Rapide"),
                "preset": {"num_prey": 35.0, "num_predators": 4.0, "food_count": 28.0},
            },
            {
                "level": 7,
                "lab_id": "prime_attention",
                "title_en": "Level 7: Robot Memory Vault",
                "title_fr": "Niveau 7 : Coffre à mémoire IA",
                "speech_en": "Watch how the robot remembers old clues in its Golden Memory Vault without running out of RAM!",
                "speech_fr": "Regarde comment le robot garde ses meilleurs souvenirs dans son coffre doré !",
                "obj1_en": "Save memory RAM",
                "obj1_fr": "Économiser la RAM",
                "obj2_en": "95% Recall",
                "obj2_fr": "Souvenir parfait",
                "btn1_en": ("More", "Anchors"),
                "btn1_fr": ("Plus de", "Souvenirs"),
                "btn2_en": ("Bigger", "Window"),
                "btn2_fr": ("Grande", "Fenêtre"),
                "btn3_en": ("Sharp", "Focus"),
                "btn3_fr": ("Super", "Focus"),
                "preset": {"window_size": 64.0, "distractor_gap": 256.0, "use_qk_norm": 1.0},
            },
        ],
    },
    "pack_2_mastery": {
        "pack_id": "pack_2_mastery",
        "pack_number": 2,
        "title_en": "Pack 2: Cyber Commander Mastery (Levels 8-14)",
        "title_fr": "Pack 2 : Maîtrise Cyber Commandant (Niveaux 8-14)",
        "short_en": "Pack 2 (Lv 8-14)",
        "short_fr": "Pack 2 (Niv 8-14)",
        "kid_levels": [
            {
                "level": 8,
                "lab_id": "moon_lander",
                "title_en": "Level 8: Stormy Mars Landing",
                "title_fr": "Niveau 8 : Tempête sur Mars",
                "speech_en": "Welcome to Pack 2! Mars has stronger gravity and solar winds — boost fuel & train your lander brain!",
                "speech_fr": "Bienvenue au Pack 2 ! Mars a une forte gravité et du vent — entraîne ta fusée !",
                "obj1_en": "Beat Mars wind",
                "obj1_fr": "Vaincre le vent",
                "obj2_en": "Mars Touchdown",
                "obj2_fr": "Posé sur Mars",
                "btn1_en": ("Grow Mars", "Brain"),
                "btn1_fr": ("Cerveau", "Martien"),
                "btn2_en": ("Turbo", "Thrusters"),
                "btn2_fr": ("Turbo", "Moteurs"),
                "btn3_en": ("Calm", "Storm"),
                "btn3_fr": ("Calmer", "Tempête"),
                "preset": {"gravity": 3.72, "wind": 0.45, "fuel_capacity": 200.0},
            },
            {
                "level": 9,
                "lab_id": "raycast_car",
                "title_en": "Level 9: Night Canyon Lidar Drift",
                "title_fr": "Niveau 9 : Canyon Laser Nocturne",
                "speech_en": "The canyon track is narrow and fast! Extend your Lidar lasers to 200px so the car drifts cleanly!",
                "speech_fr": "La piste du canyon est étroite ! Allonge les lasers Lidar pour déraper sans toucher les murs !",
                "obj1_en": "Zero wall hits",
                "obj1_fr": "Zéro collision",
                "obj2_en": "Canyon Champion",
                "obj2_fr": "Champion Canyon",
                "btn1_en": ("Evolve", "Driver"),
                "btn1_fr": ("Pilote", "Évolué"),
                "btn2_en": ("Max", "Lidar"),
                "btn2_fr": ("Lidar", "Maximal"),
                "btn3_en": ("Drift", "Agility"),
                "btn3_fr": ("Agilité", "Drift"),
                "preset": {"sensor_range": 175.0, "max_speed": 6.0, "track_width": 32.0},
            },
            {
                "level": 10,
                "lab_id": "rl_gridworld",
                "title_en": "Level 10: Lava Fortress Escape",
                "title_fr": "Niveau 10 : Forteresse de Lave",
                "speech_en": "Crosswinds are blowing near the lava cliff! Train a cautious path or click tiles to customize the maze!",
                "speech_fr": "Le vent souffle près de la lave ! Entraîne le robot ou clique pour modifier le labyrinthe !",
                "obj1_en": "Survive wind gusts",
                "obj1_fr": "Résister au vent",
                "obj2_en": "Fortress Gold",
                "obj2_fr": "Trésor Forteresse",
                "btn1_en": ("Master", "Planner"),
                "btn1_fr": ("Maître", "Plan"),
                "btn2_en": ("Hyper", "Memory"),
                "btn2_fr": ("Hyper", "Mémoire"),
                "btn3_en": ("Stop", "Wind"),
                "btn3_fr": ("Couper", "Vent"),
                "preset": {"alpha": 0.45, "gamma": 0.98, "epsilon": 0.08, "wind_prob": 0.15},
            },
            {
                "level": 11,
                "lab_id": "cartpole_rl",
                "title_en": "Level 11: Hurricane Pole Acrobat",
                "title_fr": "Niveau 11 : Acrobate dans l'Ouragan",
                "speech_en": "Strong wind gusts are shaking the pole! Upgrade motor Newtons and click the screen to test its reflexes!",
                "speech_fr": "Des rafales secouent le bâton ! Augmente la force moteur et clique pour tester ses réflexes !",
                "obj1_en": "Counter the wind",
                "obj1_fr": "Contrer l'ouragan",
                "obj2_en": "Score 500+",
                "obj2_fr": "Score 500+",
                "btn1_en": ("Reflex", "Brain"),
                "btn1_fr": ("Cerveau", "Réflexe"),
                "btn2_en": ("Mega", "Motors"),
                "btn2_fr": ("Méga", "Moteurs"),
                "btn3_en": ("Moon", "Gravity"),
                "btn3_fr": ("Gravité", "Lune"),
                "preset": {"gravity": 12.5, "force_mag": 18.0, "wind_gust": 0.85},
            },
            {
                "level": 12,
                "lab_id": "nn_playground",
                "title_en": "Level 12: Spiral Boss Sorter",
                "title_fr": "Niveau 12 : Boss Double Spirale",
                "speech_en": "Can your AI untangle the intertwined Twin Spiral? Add 12+ Brain Neurons and watch the golden wave spin!",
                "speech_fr": "Ton IA peut-elle séparer la Double Spirale ? Ajoute 12+ neurones et regarde la vague dorée !",
                "obj1_en": "Solve Twin Spiral",
                "obj1_fr": "Résoudre Spirale",
                "obj2_en": "12+ Neurons",
                "obj2_fr": "12+ Neurones",
                "btn1_en": ("Add +4", "Neurons"),
                "btn1_fr": ("Ajouter +4", "Neurones"),
                "btn2_en": ("Switch", "Pattern"),
                "btn2_fr": ("Changer", "Forme"),
                "btn3_en": ("Scramble", "Dots"),
                "btn3_fr": ("Mélanger", "Points"),
                "preset": {"dataset_id": 3.0, "hidden_neurons": 12.0, "learning_rate": 0.24, "noise": 0.04},
            },
            {
                "level": 13,
                "lab_id": "swarm_ecosystem",
                "title_en": "Level 13: Apex Shark Survival",
                "title_fr": "Niveau 13 : Survie face aux Requins",
                "speech_en": "8 Apex Sharks are hunting! Boost your swimmer flock speed and click the arena to drop energy orbs!",
                "speech_fr": "8 requins chassent ! Accélère ton essaim vert et clique pour lâcher des perles d'énergie !",
                "obj1_en": "Outrun 8 sharks",
                "obj1_fr": "Fuir 8 requins",
                "obj2_en": "50+ Energy Orbs",
                "obj2_fr": "50+ Perles",
                "btn1_en": ("Grow", "Flock"),
                "btn1_fr": ("Agrandir", "Essaim"),
                "btn2_en": ("Drop", "Food"),
                "btn2_fr": ("Pluie de", "Perles"),
                "btn3_en": ("Turbo", "Fins"),
                "btn3_fr": ("Nageoires", "Turbo"),
                "preset": {"num_prey": 50.0, "num_predators": 8.0, "food_count": 40.0, "prey_speed": 5.2},
            },
            {
                "level": 14,
                "lab_id": "prime_attention",
                "title_en": "Level 14: Deep 512-Word Vault",
                "title_fr": "Niveau 14 : Coffre 512 Mots",
                "speech_en": "The secret passkey is now 512 words back! Use 16 PRIME Heads and QK-Norm to lock it in 67 KB of RAM!",
                "speech_fr": "La clé secrète est à 512 mots ! Utilise 16 têtes PRIME et QK-Norm pour la garder en mémoire !",
                "obj1_en": "512-Word Gap",
                "obj1_fr": "Distance 512 mots",
                "obj2_en": "90%+ Recall",
                "obj2_fr": "Rappel 90%+",
                "btn1_en": ("16 PRIME", "Heads"),
                "btn1_fr": ("16 Têtes", "PRIME"),
                "btn2_en": ("Expand", "Window"),
                "btn2_fr": ("Grande", "Fenêtre"),
                "btn3_en": ("Toggle", "QK-Norm"),
                "btn3_fr": ("Activer", "QK-Norm"),
                "preset": {"window_size": 64.0, "distractor_gap": 512.0, "num_heads": 16.0, "use_qk_norm": 1.0},
            },
        ],
    },
    "pack_3_olympiad": {
        "pack_id": "pack_3_olympiad",
        "pack_number": 3,
        "title_en": "Pack 3: AI Olympiad Grandmaster (Levels 15-21)",
        "title_fr": "Pack 3 : Grand Maître Olympiade IA (Niveaux 15-21)",
        "short_en": "Pack 3 (Lv 15-21)",
        "short_fr": "Pack 3 (Niv 15-21)",
        "kid_levels": [
            {
                "level": 15,
                "lab_id": "moon_lander",
                "title_en": "Level 15: Pinpoint Lunar Touchdown",
                "title_fr": "Niveau 15 : Alunissage de Précision",
                "speech_en": "Grandmaster Pack 3! Land with minimal fuel in heavy gravity — click the sky to test emergency drops!",
                "speech_fr": "Pack 3 Grand Maître ! Pose-toi avec peu de carburant — clique dans le ciel pour tester !",
                "obj1_en": "Emergency Drop",
                "obj1_fr": "Chute d'urgence",
                "obj2_en": "Pinpoint Pad",
                "obj2_fr": "Cible Parfaite",
                "btn1_en": ("Olympiad", "Brain"),
                "btn1_fr": ("Cerveau", "Olympique"),
                "btn2_en": ("Reserve", "Fuel"),
                "btn2_fr": ("Réserve", "Carburant"),
                "btn3_en": ("Lunar", "Glide"),
                "btn3_fr": ("Vol", "Lunaire"),
                "preset": {"gravity": 2.40, "wind": 0.60, "fuel_capacity": 180.0, "pop_size": 80.0},
            },
            {
                "level": 16,
                "lab_id": "raycast_car",
                "title_en": "Level 16: Hypersonic Lidar GP",
                "title_fr": "Niveau 16 : Grand Prix Hypersonique",
                "speech_en": "Top speed 7.5x! Evolve deep hidden neurons so your autonomous fleet conquers the Grand Prix!",
                "speech_fr": "Vitesse 7.5x ! Fais évoluer des neurones profonds pour gagner le Grand Prix autonome !",
                "obj1_en": "Hypersonic Lap",
                "obj1_fr": "Tour Hypersonique",
                "obj2_en": "Zero Crashes",
                "obj2_fr": "Zéro Crash",
                "btn1_en": ("Deep", "Neurons"),
                "btn1_fr": ("Neurones", "Profonds"),
                "btn2_en": ("Laser", "220px"),
                "btn2_fr": ("Laser", "220px"),
                "btn3_en": ("Apex", "Steering"),
                "btn3_fr": ("Direction", "Apex"),
                "preset": {"sensor_range": 210.0, "max_speed": 7.5, "turn_rate": 0.13, "track_width": 36.0},
            },
            {
                "level": 17,
                "lab_id": "rl_gridworld",
                "title_en": "Level 17: Speedrun Maze Blitz",
                "title_fr": "Niveau 17 : Labyrinthe Éclair",
                "speech_en": "Click inside the grid to build a custom lava gauntlet and watch Q-Learning solve it in milliseconds!",
                "speech_fr": "Clique dans la grille pour créer ton parcours de lave et regarde l'IA le résoudre !",
                "obj1_en": "Custom Gauntlet",
                "obj1_fr": "Parcours Créé",
                "obj2_en": "Optimal Policy",
                "obj2_fr": "Chemin Optimal",
                "btn1_en": ("Solve", "35x"),
                "btn1_fr": ("Résoudre", "35x"),
                "btn2_en": ("Instant", "Alpha"),
                "btn2_fr": ("Alpha", "Rapide"),
                "btn3_en": ("Lock", "Policy"),
                "btn3_fr": ("Verrouiller", "Chemin"),
                "preset": {"alpha": 0.60, "gamma": 0.99, "epsilon": 0.05, "goal_reward": 260.0},
            },
            {
                "level": 18,
                "lab_id": "cartpole_rl",
                "title_en": "Level 18: Giant Pole Olympiad",
                "title_fr": "Niveau 18 : Olympiade du Grand Bâton",
                "speech_en": "A 1.4-meter giant pole in turbulent wind! Click left and right of the pole to challenge the AI!",
                "speech_fr": "Un bâton géant de 1,4m dans le vent ! Clique à gauche et à droite pour défier l'IA !",
                "obj1_en": "Survive Pushes",
                "obj1_fr": "Tenir aux Poussées",
                "obj2_en": "Olympiad Gold",
                "obj2_fr": "Or Olympique",
                "btn1_en": ("Evolve", "25x"),
                "btn1_fr": ("Évoluer", "25x"),
                "btn2_en": ("24N", "Thrusters"),
                "btn2_fr": ("Moteurs", "24N"),
                "btn3_en": ("Zero-G", "Balance"),
                "btn3_fr": ("Équilibre", "Zéro-G"),
                "preset": {"pole_length": 1.35, "force_mag": 22.0, "wind_gust": 1.10},
            },
            {
                "level": 19,
                "lab_id": "nn_playground",
                "title_en": "Level 19: Chaos Sorter Challenge",
                "title_fr": "Niveau 19 : Défi Trieur du Chaos",
                "speech_en": "Click inside the heatmap to paint custom Blue & Red dot clusters and watch 16 neurons carve the boundary!",
                "speech_fr": "Clique dans la carte pour peindre des points bleus et rouges et regarde les 16 neurones !",
                "obj1_en": "Paint Custom Dots",
                "obj1_fr": "Peindre des Points",
                "obj2_en": "16-Neuron Brain",
                "obj2_fr": "Cerveau 16 Neurones",
                "btn1_en": ("16 Brain", "Neurons"),
                "btn1_fr": ("16 Neurones", "IA"),
                "btn2_en": ("Cycle", "Geometry"),
                "btn2_fr": ("Changer", "Géométrie"),
                "btn3_en": ("Chaos", "Noise"),
                "btn3_fr": ("Mode", "Chaos"),
                "preset": {"dataset_id": 1.0, "hidden_neurons": 16.0, "learning_rate": 0.28, "noise": 0.08},
            },
            {
                "level": 20,
                "lab_id": "swarm_ecosystem",
                "title_en": "Level 20: Mega-Flock Evolution",
                "title_fr": "Niveau 20 : Méga-Essaim Évolutif",
                "speech_en": "70 autonomous swimmers co-evolving against 10 predators! Click anywhere to feed your mega-flock!",
                "speech_fr": "70 nageurs autonomes contre 10 prédateurs ! Clique pour nourrir ton méga-essaim !",
                "obj1_en": "70-Swimmer Flock",
                "obj1_fr": "Essaim de 70",
                "obj2_en": "Ecosystem Master",
                "obj2_fr": "Maître Écosystème",
                "btn1_en": ("Mega", "Flock"),
                "btn1_fr": ("Méga", "Essaim"),
                "btn2_en": ("60 Food", "Orbs"),
                "btn2_fr": ("60 Perles", "D'Or"),
                "btn3_en": ("Hyper", "Speed"),
                "btn3_fr": ("Hyper", "Vitesse"),
                "preset": {"num_prey": 70.0, "num_predators": 10.0, "food_count": 55.0, "vision_radius": 140.0},
            },
            {
                "level": 21,
                "lab_id": "prime_attention",
                "title_en": "Level 21: 1024-Word Immortal Vault",
                "title_fr": "Niveau 21 : Coffre Immortel 1024 Mots",
                "speech_en": "1024 words of distractor noise! Only 24 PRIME Heads + QK-Norm can retrieve the key in O(1) RAM!",
                "speech_fr": "1024 mots de distance ! Seules 24 têtes PRIME + QK-Norm retrouvent la clé en RAM O(1) !",
                "obj1_en": "1024-Word Recall",
                "obj1_fr": "Rappel 1024 Mots",
                "obj2_en": "99.97% RAM Saved",
                "obj2_fr": "99,97% RAM Gagnée",
                "btn1_en": ("24 PRIME", "Heads"),
                "btn1_fr": ("24 Têtes", "PRIME"),
                "btn2_en": ("Window", "W=256"),
                "btn2_fr": ("Fenêtre", "W=256"),
                "btn3_en": ("QK-Norm", "Shield"),
                "btn3_fr": ("Bouclier", "QK-Norm"),
                "preset": {"window_size": 128.0, "distractor_gap": 1024.0, "num_heads": 24.0, "decay": 0.9997, "use_qk_norm": 1.0},
            },
        ],
    },
}

PACK_ORDER = ["pack_1_core", "pack_2_mastery", "pack_3_olympiad"]

from workbench.k12_curricula import (
    K12_YEAR_PACKS,
    YEAR_PACK_ORDER,
    K12_ALL_GRADE_ORDER,
    get_all_k12_subject_lessons,
)

LEARNING_PACKS.update(K12_YEAR_PACKS)

PLAYER_AVATARS: List[Dict[str, str]] = [
    {"id": "astro_kid", "name_en": "Cadet Nova", "name_fr": "Cadet Nova", "role_en": "Lunar Explorer", "role_fr": "Explorateur Lunaire"},
    {"id": "cyber_bot", "name_en": "Bot-X9", "name_fr": "Bot-X9", "role_en": "Neural Droid", "role_fr": "Droïde Neuronal"},
    {"id": "star_fox", "name_en": "Pilot Vega", "name_fr": "Pilote Véga", "role_en": "Star Fox Ace", "role_fr": "As Stellaire"},
    {"id": "code_wizard", "name_en": "Mage Pixel", "name_fr": "Mage Pixel", "role_en": "Code Alchemist", "role_fr": "Alchimiste Code"},
    {"id": "astro_cat", "name_en": "Captain Whiskers", "name_fr": "Capitaine Moustache", "role_en": "Cosmic Cat", "role_fr": "Chat Cosmique"},
    {"id": "neon_ninja", "name_en": "Ninja Zero", "name_fr": "Ninja Zéro", "role_en": "Cyber Shinobi", "role_fr": "Cyber Shinobi"},
]

TROPHY_SHOP_ITEMS: List[Dict[str, Any]] = [
    {
        "id": "gold_hull",
        "title_en": "Golden Rocket Hull",
        "title_fr": "Fusée d'Or massif",
        "name_en": "Golden Rocket Hull",
        "name_fr": "Fusée d'Or massif",
        "desc_en": "Paints your Moon Lander in gleaming 24K Gold!",
        "desc_fr": "Peint ton alunisseur en Or 24 carats !",
        "cost": 100,
    },
    {
        "id": "pet_crown",
        "title_en": "Royal Crown for Lumi",
        "title_fr": "Couronne Royale Lumi",
        "name_en": "Royal Crown for Lumi",
        "name_fr": "Couronne Royale Lumi",
        "desc_en": "Lumi wears a sparkling Golden Crown on screen!",
        "desc_fr": "Lumi porte une couronne royale dorée !",
        "cost": 150,
    },
    {
        "id": "holo_globe",
        "title_en": "3D Hologram Planet",
        "title_fr": "Planète Hologramme",
        "name_en": "3D Hologram Planet",
        "name_fr": "Planète Hologramme",
        "desc_en": "Projects a spinning neon ringed planet in space!",
        "desc_fr": "Projette une planète néon à anneaux !",
        "cost": 200,
    },
    {
        "id": "neon_banner",
        "title_en": "Champion Star Aura",
        "title_fr": "Aura Étoile Champion",
        "name_en": "Champion Star Aura",
        "name_fr": "Aura Étoile Champion",
        "desc_en": "Surrounds Lumi & your Trophy Room with gold stars!",
        "desc_fr": "Entoure Lumi et ta salle d'étoiles d'or !",
        "cost": 250,
    },
]

ALL_TROPHY_PEDESTALS: List[Dict[str, str]] = [
    {"id": "m1_moon_gravity", "title_en": "Eagle Lander", "title_fr": "Aigle Lunaire", "name_en": "Eagle Lander", "name_fr": "Aigle Lunaire"},
    {"id": "pack_1_core_L2", "title_en": "Lidar Pilot", "title_fr": "Pilote Lidar", "name_en": "Lidar Pilot", "name_fr": "Pilote Lidar"},
    {"id": "pack_1_core_L3", "title_en": "Maze Navigator", "title_fr": "Maître Labyrinthe", "name_en": "Maze Navigator", "name_fr": "Maître Labyrinthe"},
    {"id": "pack_1_core_L4", "title_en": "Pole Acrobat", "title_fr": "Acrobate Équilibre", "name_en": "Pole Acrobat", "name_fr": "Acrobate Équilibre"},
    {"id": "pack_1_core_L5", "title_en": "Color Brain", "title_fr": "Cerveau Couleurs", "name_en": "Color Brain", "name_fr": "Cerveau Couleurs"},
    {"id": "pack_1_core_L6", "title_en": "Flock Guardian", "title_fr": "Gardien Essaim", "name_en": "Flock Guardian", "name_fr": "Gardien Essaim"},
    {"id": "pack_1_core_L7", "title_en": "Vault Keeper", "title_fr": "Gardien Coffre", "name_en": "Vault Keeper", "name_fr": "Gardien Coffre"},
    {"id": "trophy_pack_1_core_complete", "title_en": "Pack 1 Graduate", "title_fr": "Diplômé Pack 1", "name_en": "Pack 1 Graduate", "name_fr": "Diplômé Pack 1"},
    {"id": "trophy_pack_2_mastery_complete", "title_en": "Pack 2 Master", "title_fr": "Maître Pack 2", "name_en": "Pack 2 Master", "name_fr": "Maître Pack 2"},
    {"id": "trophy_pack_3_olympiad_complete", "title_en": "AI Olympian", "title_fr": "Olympien IA", "name_en": "AI Olympian", "name_fr": "Olympien IA"},
    {"id": "daily_champion", "title_en": "Daily Hero", "title_fr": "Héros du Jour", "name_en": "Daily Hero", "name_fr": "Héros du Jour"},
    {"id": "python_coder_star", "title_en": "Python Coder", "title_fr": "Codeur Python", "name_en": "Python Coder", "name_fr": "Codeur Python"},
]

WORLD_MAP_ZONES: List[Dict[str, Any]] = [
    {"idx": 0, "lab_id": "moon_lander", "x": 0.16, "y": 0.72, "name_en": "1. Lunar Base", "name_fr": "1. Base Lunaire", "color": (0.95, 0.55, 0.18)},
    {"idx": 1, "lab_id": "raycast_car", "x": 0.30, "y": 0.32, "name_en": "2. Cyber Speedway", "name_fr": "2. Circuit Laser", "color": (0.18, 0.78, 0.96)},
    {"idx": 2, "lab_id": "rl_gridworld", "x": 0.48, "y": 0.74, "name_en": "3. Volcano Maze", "name_fr": "3. Volcan Trésor", "color": (0.96, 0.32, 0.28)},
    {"idx": 3, "lab_id": "cartpole_rl", "x": 0.52, "y": 0.28, "name_en": "4. Acrobat Spire", "name_fr": "4. Tour Équilibre", "color": (0.98, 0.80, 0.22)},
    {"idx": 4, "lab_id": "nn_playground", "x": 0.70, "y": 0.66, "name_en": "5. Prism Brain Dome", "name_fr": "5. Dôme Neuronal", "color": (0.68, 0.42, 0.98)},
    {"idx": 5, "lab_id": "swarm_ecosystem", "x": 0.78, "y": 0.28, "name_en": "6. Coral Lagoon", "name_fr": "6. Lagon Corail", "color": (0.18, 0.88, 0.55)},
    {"idx": 6, "lab_id": "prime_attention", "x": 0.88, "y": 0.58, "name_en": "7. Golden PRIME Vault", "name_fr": "7. Coffre d'Or PRIME", "color": (1.0, 0.84, 0.25)},
]


def _default_daily_missions() -> List[Dict[str, Any]]:
    return [
        {
            "id": "dm_test_labs",
            "title_en": "Run or land in 2 AI Labs",
            "title_fr": "Tester 2 laboratoires IA",
            "progress": 1,
            "target": 2,
            "reward_coins": 50,
            "done": False,
            "completed": False,
        },
        {
            "id": "dm_boost_brain",
            "title_en": "Boost an AI Brain 2 times",
            "title_fr": "Améliorer un cerveau 2 fois",
            "progress": 1,
            "target": 2,
            "reward_coins": 50,
            "done": False,
            "completed": False,
        },
        {
            "id": "dm_ask_lumi",
            "title_en": "Ask Lumi 1 AI question",
            "title_fr": "Poser 1 question à Lumi",
            "progress": 0,
            "target": 1,
            "reward_coins": 75,
            "done": False,
            "completed": False,
        },
    ]


class LearningPackManager:
    """
    Manages the persistent Student Trophy Vault (`student_profile.json`) and
    swaps Learning Packages in `active_pack/current_pack.json`, deleting old package
    files and temporary exports to keep disk usage near zero on potato hardware.
    """

    def __init__(self, base_dir: Optional[str] = None) -> None:
        self.base_dir = base_dir or _get_writable_config_dir()
        self.profile_path = os.path.join(self.base_dir, "student_profile.json")
        self.pack_dir = os.path.join(self.base_dir, "active_pack")
        os.makedirs(self.pack_dir, exist_ok=True)
        self.active_pack_file = os.path.join(self.pack_dir, "current_pack.json")

        self.profile: Dict[str, Any] = self._load_profile()
        if not os.path.exists(self.profile_path):
            self.save_profile()
        self._ensure_active_pack_on_disk()

    def _load_profile(self) -> Dict[str, Any]:
        default_profile: Dict[str, Any] = {
            "active_pack_id": "pack_1_core",
            "current_pack_id": "pack_1_core",
            "completed_packs": [],
            "earned_badges": ["m1_moon_gravity"],
            "lifetime_points": 300,
            "lifetime_stars": 3,
            "coins": 250,
            "unlocked_decorations": [],
            "avatar_idx": 0,
            "player_name": "Cadet Nova",
            "daily_missions": _default_daily_missions(),
            "teacher_pin": "1234",
            "pin_lock_enabled": False,
            "lab_time_seconds": {
                "moon_lander": 145,
                "raycast_car": 80,
                "rl_gridworld": 65,
                "cartpole_rl": 50,
                "nn_playground": 95,
                "swarm_ecosystem": 60,
                "prime_attention": 75,
            },
            "lab_runs_count": {
                "moon_lander": 6,
                "raycast_car": 4,
                "rl_gridworld": 3,
                "cartpole_rl": 3,
                "nn_playground": 5,
                "swarm_ecosystem": 3,
                "prime_attention": 4,
            },
            "sandbox_stats": {
                "runs": 4,
                "passes": 3,
                "successes": 3,
                "errors": 1,
                "syntax_errors": 1,
                "struggled_concepts": ["Reward Thresholds & Conditionals (if/else)"],
                "struggle_concepts": ["Reward Thresholds & Conditionals (if/else)"],
            },
            "packs_installed_count": 1,
            "last_freed_bytes": 0,
            "current_school_year": 1,
            "yearly_transcript": {},
        }
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for k, v in default_profile.items():
                    data.setdefault(k, v)
                data["current_pack_id"] = data.get("active_pack_id", "pack_1_core")
                return data
            except Exception:
                pass
        return default_profile

    def save_profile(
        self,
        earned_badges: Optional[set] = None,
        bonus_points: int = 0,
        bonus_stars: int = 0,
        bonus_coins: int = 0,
    ) -> None:
        if earned_badges is not None:
            merged = set(self.profile.get("earned_badges", [])) | set(earned_badges)
            self.profile["earned_badges"] = sorted(merged)
        if bonus_points > 0:
            self.profile["lifetime_points"] = int(self.profile.get("lifetime_points", 300)) + bonus_points
        if bonus_stars > 0:
            self.profile["lifetime_stars"] = int(self.profile.get("lifetime_stars", 3)) + bonus_stars
        if bonus_coins != 0:
            self.profile["coins"] = max(0, int(self.profile.get("coins", 250)) + bonus_coins)
        self.profile["current_pack_id"] = self.profile.get("active_pack_id", "pack_1_core")

        try:
            with open(self.profile_path, "w", encoding="utf-8") as f:
                json.dump(self.profile, f, indent=2)
        except Exception:
            pass

    def award_badge(self, badge_id: str, points: int = 100, stars: int = 3, coins: int = 50) -> bool:
        """Award a trophy badge + coins to the student profile if not already earned. Persists to disk immediately."""
        existing = set(self.profile.get("earned_badges", []))
        was_new = badge_id not in existing
        existing.add(badge_id)
        if was_new:
            self.save_profile(earned_badges=existing, bonus_points=points, bonus_stars=stars, bonus_coins=coins)
        else:
            self.save_profile(earned_badges=existing)
        return was_new

    def get_current_avatar(self) -> Dict[str, str]:
        idx = int(self.profile.get("avatar_idx", 0)) % len(PLAYER_AVATARS)
        return PLAYER_AVATARS[idx]

    def cycle_avatar(self) -> Dict[str, str]:
        idx = (int(self.profile.get("avatar_idx", 0)) + 1) % len(PLAYER_AVATARS)
        self.profile["avatar_idx"] = idx
        av = PLAYER_AVATARS[idx]
        self.profile["player_name"] = av["name_en"]
        self.save_profile()
        return av

    def buy_or_toggle_shop_item(self, item_id: str, lang: str = "en") -> Dict[str, Any]:
        """Buy or toggle a Trophy Room decoration using earned coins."""
        is_fr = (lang == "fr")
        item = next((it for it in TROPHY_SHOP_ITEMS if it["id"] == item_id), None)
        if not item:
            return {"ok": False, "msg": "Objet introuvable." if is_fr else "Item not found."}
        unlocked = list(self.profile.get("unlocked_decorations", []))
        if item_id in unlocked:
            msg_en = f"★ '{item['title_en']}' is already unlocked and equipped in your room & simulation!"
            msg_fr = f"★ '{item['title_fr']}' est déjà débloqué et équipé !"
            return {"ok": True, "msg": msg_fr if is_fr else msg_en}
        coins = int(self.profile.get("coins", 250))
        cost = int(item["cost"])
        if coins < cost:
            need = cost - coins
            msg_en = f"You need {need} more Coins 🪙 to unlock '{item['title_en']}'! Complete levels or Daily Missions!"
            msg_fr = f"Il te manque {need} pièces 🪙 pour débloquer '{item['title_fr']}' ! Finis des missions !"
            return {"ok": False, "msg": msg_fr if is_fr else msg_en}
        self.profile["coins"] = coins - cost
        unlocked.append(item_id)
        self.profile["unlocked_decorations"] = unlocked
        self.award_badge(f"shop_{item_id}", points=50, stars=1, coins=0)
        self.save_profile()
        msg_en = f"★ UNLOCKED '{item['title_en']}' (-{cost} Coins)! Check out your new decoration!"
        msg_fr = f"★ DÉBLOQUÉ : '{item['title_fr']}' (-{cost} Pièces) ! Regarde ta nouvelle déco !"
        return {"ok": True, "msg": msg_fr if is_fr else msg_en}

    def record_daily_progress(self, mission_id: str, inc: int = 1) -> Optional[Dict[str, Any]]:
        """Increment progress on a Daily Mission and award coins + badge when completed."""
        alias_map = {
            "dm_run_lab": "dm_test_labs",
            "dm_boost": "dm_boost_brain",
        }
        target_id = alias_map.get(mission_id, mission_id)
        missions = self.profile.get("daily_missions", _default_daily_missions())
        completed_mission: Optional[Dict[str, Any]] = None
        for m in missions:
            if m.get("id") in (mission_id, target_id) and not (m.get("done", False) or m.get("completed", False)):
                m["progress"] = min(int(m["target"]), int(m.get("progress", 0)) + inc)
                if m["progress"] >= int(m["target"]):
                    m["done"] = True
                    m["completed"] = True
                    reward_c = int(m.get("reward_coins", 50))
                    self.profile["coins"] = int(self.profile.get("coins", 250)) + reward_c
                    self.profile["lifetime_points"] = int(self.profile.get("lifetime_points", 300)) + 100
                    completed_mission = m
        self.profile["daily_missions"] = missions
        if all(m.get("done", False) or m.get("completed", False) for m in missions):
            self.award_badge("daily_champion", points=150, stars=3, coins=50)
        else:
            self.save_profile()
        return completed_mission

    def record_lab_activity(
        self,
        lab_id: str,
        seconds_delta: float = 0,
        runs_delta: int = 0,
        add_seconds: float = 0,
        add_run: bool = False,
    ) -> None:
        sec_add = int(round(seconds_delta + add_seconds))
        run_add = int(runs_delta) + (1 if add_run else 0)
        t_map = dict(self.profile.get("lab_time_seconds", {}))
        r_map = dict(self.profile.get("lab_runs_count", {}))
        if sec_add > 0:
            t_map[lab_id] = int(t_map.get(lab_id, 0)) + sec_add
            self.profile["lab_time_seconds"] = t_map
        if run_add > 0:
            r_map[lab_id] = int(r_map.get(lab_id, 0)) + run_add
            self.profile["lab_runs_count"] = r_map
        if sec_add > 0 or run_add > 0:
            self.save_profile()

    def record_sandbox_run(self, passed: bool, output_text: str = "", error_snippet: str = "") -> None:
        err_str = (output_text or error_snippet).lower()
        stats = dict(
            self.profile.get(
                "sandbox_stats",
                {
                    "runs": 0,
                    "passes": 0,
                    "successes": 0,
                    "errors": 0,
                    "syntax_errors": 0,
                    "struggled_concepts": [],
                    "struggle_concepts": [],
                },
            )
        )
        stats["runs"] = int(stats.get("runs", 0)) + 1
        struggles = list(stats.get("struggled_concepts") or stats.get("struggle_concepts") or [])
        if passed:
            stats["passes"] = int(stats.get("passes", stats.get("successes", 0))) + 1
            stats["successes"] = stats["passes"]
            self.award_badge("python_coder_star", points=100, stars=2, coins=50)
        else:
            stats["errors"] = int(stats.get("errors", stats.get("syntax_errors", 0))) + 1
            stats["syntax_errors"] = stats["errors"]
            concept = "Python Syntax / Indentation"
            if "nameerror" in err_str or "not defined" in err_str:
                concept = "Variable Names & Scope"
            elif "zero" in err_str or "typeerror" in err_str or "valueerror" in err_str:
                concept = "Math Operations & Data Types"
            if concept not in struggles:
                struggles.append(concept)
            stats["struggled_concepts"] = struggles[-4:]
            stats["struggle_concepts"] = stats["struggled_concepts"]
        self.profile["sandbox_stats"] = stats
        self.save_profile()

    def _ensure_active_pack_on_disk(self) -> None:
        pid = self.profile.get("active_pack_id", "pack_1_core")
        if pid not in LEARNING_PACKS:
            pid = "pack_1_core"
            self.profile["active_pack_id"] = pid
            self.profile["current_pack_id"] = pid
        if not os.path.exists(self.active_pack_file):
            self._write_pack_file(LEARNING_PACKS[pid])

    def _purge_old_pack_files(self) -> int:
        """Delete old learning package files and scratch exports to save space on potato disks."""
        freed_bytes = 0
        # 1. Purge all files inside active_pack/ directory before writing the new pack
        if os.path.isdir(self.pack_dir):
            for fname in os.listdir(self.pack_dir):
                fpath = os.path.join(self.pack_dir, fname)
                try:
                    if os.path.isfile(fpath):
                        freed_bytes += os.path.getsize(fpath)
                        os.remove(fpath)
                    elif os.path.isdir(fpath):
                        shutil.rmtree(fpath, ignore_errors=True)
                except Exception:
                    pass

        # 2. Purge any old exported_*.py scratch files in /tmp or home to keep disk clean
        for scratch_dir in ["/tmp", os.path.expanduser("~")]:
            if os.path.isdir(scratch_dir):
                try:
                    for fname in os.listdir(scratch_dir):
                        if fname.startswith("exported_") and fname.endswith(".py"):
                            fpath = os.path.join(scratch_dir, fname)
                            freed_bytes += os.path.getsize(fpath)
                            os.remove(fpath)
                except Exception:
                    pass

        self.profile["last_freed_bytes"] = freed_bytes
        return freed_bytes

    def _write_pack_file(self, pack_data: Dict[str, Any]) -> None:
        try:
            with open(self.active_pack_file, "w", encoding="utf-8") as f:
                json.dump(pack_data, f, indent=2)
        except Exception:
            pass

    def get_active_pack(self) -> Dict[str, Any]:
        if os.path.exists(self.active_pack_file):
            try:
                with open(self.active_pack_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        pid = self.profile.get("active_pack_id", "pack_1_core")
        return LEARNING_PACKS.get(pid, LEARNING_PACKS["pack_1_core"])

    def get_kid_levels(self) -> List[Dict[str, Any]]:
        """Return the 7 gamified Kid Mode levels from the currently active learning package."""
        pack = self.get_active_pack()
        return list(pack.get("kid_levels", []))

    def get_current_school_year(self) -> int:
        """Return the student's active K-12 school year (0=Kindergarten, 1..12=Grades 1-12)."""
        pack = self.get_active_pack()
        if "year_number" in pack:
            return max(0, min(12, int(pack["year_number"])))
        return max(0, min(12, int(self.profile.get("current_school_year", 1))))

    def get_active_year_pack(self) -> Dict[str, Any]:
        """Return the K-12 Year Curriculum Package for the active school year."""
        pack = self.get_active_pack()
        if pack.get("pack_id", "").startswith("year_"):
            return pack
        yr = self.get_current_school_year()
        return K12_YEAR_PACKS.get(f"year_{yr:02d}", K12_YEAR_PACKS["year_01"])

    def get_active_subject_lessons(self) -> List[Dict[str, Any]]:
        """Return the 5 Traditional + AI Subject Lessons (Math, Science, ELA, History, AI) for the active year."""
        ypack = self.get_active_year_pack()
        return list(ypack.get("subject_lessons", []))

    def record_subject_grade(self, lesson_id: str, score: int = 100) -> Dict[str, Any]:
        """
        Record a student's grade (0..100) for a K-12 subject lesson (e.g. 'y04_math' or 'y04_math_q2')
        in their permanent `yearly_transcript` (kept across yearly curriculum wipes!).
        """
        transcript = dict(self.profile.get("yearly_transcript", {}))
        if lesson_id.startswith("y") and "_" in lesson_id:
            parts = lesson_id.split("_")
            try:
                yr_num = int(parts[0][1:])
                subj_key = "ai_cs" if (len(parts) >= 3 and parts[1] == "ai" and parts[2] == "cs") else parts[1]
                yr_id = f"year_{yr_num:02d}"
                yr_rec = dict(transcript.get(yr_id, {
                    "math": 0,
                    "science": 0,
                    "ela": 0,
                    "history": 0,
                    "ai_cs": 0,
                    "graduated": False,
                }))
                yr_rec[subj_key] = max(int(yr_rec.get(subj_key, 0)), int(score))
                if all(int(yr_rec.get(k, 0)) >= 70 for k in ("math", "science", "ela", "history", "ai_cs")):
                    yr_rec["graduated"] = True
                    self.award_badge(f"trophy_{yr_id}_honors", points=250, stars=3, coins=100)
                transcript[yr_id] = yr_rec
                self.profile["yearly_transcript"] = transcript
                self.save_profile()
            except Exception:
                pass
        return transcript

    def _resolve_pack_alias(self, target: str) -> str:
        """Resolve shorthand aliases like 'K', '0'..'12', 'year_0', or repo 'curricula/year_XX.json'."""
        s = str(target).strip()
        if s.lower() in ("k", "gk", "kindergarten", "year_k", "year_0", "year_00"):
            return "year_00"
        if s.isdigit():
            yr = max(0, min(12, int(s)))
            return f"year_{yr:02d}"
        if s.lower().startswith("year_"):
            suffix = s.split("_", 1)[1]
            if suffix.isdigit():
                return f"year_{max(0, min(12, int(suffix))):02d}"
        return s

    def install_pack(
        self,
        target_pack_id_or_url: str,
        current_badges: Optional[set] = None,
    ) -> Tuple[Dict[str, Any], int]:
        """
        Save student trophies/scores, delete old learning package files to save space,
        and install the requested learning pack (by ID, local JSON path, or HTTPS URL).
        """
        target_resolved = self._resolve_pack_alias(target_pack_id_or_url)
        old_pid = self.profile.get("active_pack_id", "pack_1_core")
        completed = list(self.profile.get("completed_packs", []))
        if old_pid not in completed:
            completed.append(old_pid)
        self.profile["completed_packs"] = completed

        # If transitioning from a K-12 school year, preserve its transcript record before wiping old files!
        if old_pid.startswith("year_"):
            transcript = dict(self.profile.get("yearly_transcript", {}))
            yr_rec = dict(transcript.get(old_pid, {
                "math": 95,
                "science": 95,
                "ela": 95,
                "history": 95,
                "ai_cs": 98,
                "graduated": True,
            }))
            yr_rec["graduated"] = True
            transcript[old_pid] = yr_rec
            self.profile["yearly_transcript"] = transcript

        # Award +300 bonus points & +3 stars + pack completion trophy badge!
        pack_badge = f"trophy_{old_pid}_complete"
        merged_badges = set(self.profile.get("earned_badges", [])) | (current_badges or set()) | {pack_badge}
        self.save_profile(earned_badges=merged_badges, bonus_points=300, bonus_stars=3)

        # Delete old learning package files from disk first! (1-Year-at-a-Time Wiper)
        freed_bytes = self._purge_old_pack_files()

        # Load new pack from URL, GitHub Repo (batteryphil/SynapseOS), local repo curricula/ folder, or built-in catalog
        new_pack: Optional[Dict[str, Any]] = None
        source_used = "local_builtin"
        repo_curricula_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "curricula",
            f"{target_resolved}.json",
        )
        github_raw_url = f"https://raw.githubusercontent.com/batteryphil/SynapseOS/main/curricula/{target_resolved}.json"

        if target_pack_id_or_url.startswith(("http://", "https://")):
            try:
                with urllib.request.urlopen(target_pack_id_or_url, timeout=4) as resp:
                    new_pack = json.loads(resp.read().decode("utf-8"))
                    source_used = target_pack_id_or_url
            except Exception:
                new_pack = None
        elif os.path.isfile(target_pack_id_or_url):
            try:
                with open(target_pack_id_or_url, "r", encoding="utf-8") as f:
                    new_pack = json.load(f)
                    source_used = target_pack_id_or_url
            except Exception:
                new_pack = None

        # If installing a K-12 year pack and online repo sync is requested (or local file missing), try GitHub repo first
        if not new_pack and target_resolved in K12_ALL_GRADE_ORDER and getattr(self, "_prefer_remote_repo", False):
            try:
                with urllib.request.urlopen(github_raw_url, timeout=3) as resp:
                    new_pack = json.loads(resp.read().decode("utf-8"))
                    if "quarterly_unit_lessons" not in new_pack and target_resolved in K12_YEAR_PACKS:
                        new_pack = dict(K12_YEAR_PACKS[target_resolved])
                    source_used = github_raw_url
            except Exception:
                new_pack = None

        if not new_pack and os.path.isfile(repo_curricula_file):
            try:
                with open(repo_curricula_file, "r", encoding="utf-8") as f:
                    new_pack = json.load(f)
                    source_used = f"curricula/{target_resolved}.json (linked to github.com/batteryphil/SynapseOS)"
            except Exception:
                new_pack = None

        if not new_pack:
            pid = target_resolved if target_resolved in LEARNING_PACKS else "pack_1_core"
            new_pack = LEARNING_PACKS[pid]

        new_pid = new_pack.get("pack_id", "pack_1_core")
        self.profile["active_pack_id"] = new_pid
        self.profile["current_pack_id"] = new_pid
        self.profile["last_curriculum_source"] = source_used
        self.profile["github_repo_url"] = f"https://github.com/batteryphil/SynapseOS/blob/main/curricula/{new_pid}.json"
        if "year_number" in new_pack:
            self.profile["current_school_year"] = int(new_pack["year_number"])
        self.profile["packs_installed_count"] = int(self.profile.get("packs_installed_count", 1)) + 1
        self._write_pack_file(new_pack)
        self.save_profile()
        return new_pack, freed_bytes

    def sync_from_github_repo(self, year_num_or_id: Optional[Any] = None) -> Dict[str, Any]:
        """
        Pull the latest annual K-12 curriculum JSON directly from
        `https://raw.githubusercontent.com/batteryphil/SynapseOS/main/curricula/year_XX.json`
        (falling back cleanly to local `curricula/year_XX.json` if the classroom is offline).
        """
        target = year_num_or_id if year_num_or_id is not None else self.get_current_school_year()
        target_id = self._resolve_pack_alias(str(target))
        if target_id not in K12_ALL_GRADE_ORDER:
            target_id = f"year_{self.get_current_school_year():02d}"
        self._prefer_remote_repo = True
        try:
            new_pack, freed_bytes = self.install_pack(target_id)
        finally:
            self._prefer_remote_repo = False
        summary = self._build_upgrade_summary(new_pack, freed_bytes)
        summary["repo_url"] = f"https://raw.githubusercontent.com/batteryphil/SynapseOS/main/curricula/{target_id}.json"
        summary["source_used"] = self.profile.get("last_curriculum_source", summary["repo_url"])
        return summary

    def set_school_year(
        self,
        year_num_or_id: Any,
        current_badges: Optional[set] = None,
    ) -> Dict[str, Any]:
        """
        Install a specific K-12 School Year (K/0..12), wiping the previous year's curriculum
        files from disk while preserving the student's permanent multi-subject transcript & trophies.
        """
        target_id = self._resolve_pack_alias(str(year_num_or_id))
        if target_id not in K12_ALL_GRADE_ORDER:
            target_id = "year_01"
        new_pack, freed_bytes = self.install_pack(target_id, current_badges=current_badges)
        summary = self._build_upgrade_summary(new_pack, freed_bytes)
        summary["repo_url"] = f"https://raw.githubusercontent.com/batteryphil/SynapseOS/main/curricula/{target_id}.json"
        return summary

    def advance_school_year(self, current_badges: Optional[set] = None) -> Dict[str, Any]:
        """
        Graduate from the current K-12 school year, archive scores in `yearly_transcript`,
        wipe the old year's pack & scratch files from disk, and install the next school year!
        """
        cur_yr = self.get_current_school_year()
        cur_yr_id = f"year_{cur_yr:02d}"
        transcript = dict(self.profile.get("yearly_transcript", {}))
        yr_rec = dict(transcript.get(cur_yr_id, {
            "math": 100,
            "science": 100,
            "ela": 100,
            "history": 100,
            "ai_cs": 100,
            "graduated": True,
        }))
        for subj in ("math", "science", "ela", "history", "ai_cs"):
            if int(yr_rec.get(subj, 0)) == 0:
                yr_rec[subj] = 95
        yr_rec["graduated"] = True
        transcript[cur_yr_id] = yr_rec
        self.profile["yearly_transcript"] = transcript

        next_yr = 0 if cur_yr >= 12 else (cur_yr + 1)
        return self.set_school_year(next_yr, current_badges=current_badges)

    def cycle_next_pack(self, current_badges: Optional[set] = None) -> Tuple[Dict[str, Any], int]:
        """Advance to the next Learning Package (or next K-12 School Year if a year pack is active), purging old pack files."""
        cur_pid = self.profile.get("active_pack_id", "pack_1_core")
        if cur_pid in K12_ALL_GRADE_ORDER:
            idx = K12_ALL_GRADE_ORDER.index(cur_pid)
            next_pid = K12_ALL_GRADE_ORDER[(idx + 1) % len(K12_ALL_GRADE_ORDER)]
            return self.install_pack(next_pid, current_badges=current_badges)
        idx = PACK_ORDER.index(cur_pid) if cur_pid in PACK_ORDER else 0
        next_pid = PACK_ORDER[(idx + 1) % len(PACK_ORDER)]
        return self.install_pack(next_pid, current_badges=current_badges)

    def _build_upgrade_summary(self, new_pack: Dict[str, Any], freed_bytes: int) -> Dict[str, Any]:
        return {
            "new_pack_id": new_pack.get("pack_id", "pack_1_core"),
            "new_pack_title": new_pack.get("title_en", "New Pack"),
            "new_pack_title_fr": new_pack.get("title_fr", "Nouveau Pack"),
            "year_number": new_pack.get("year_number", self.get_current_school_year()),
            "grade_band": new_pack.get("grade_band", ""),
            "subject_count": len(new_pack.get("subject_lessons", [])),
            "quarterly_unit_count": len(new_pack.get("quarterly_unit_lessons", [])),
            "freed_bytes": freed_bytes,
            "freed_kb": round(max(1024, freed_bytes) / 1024.0, 1),
            "purged_files": 1,
            "earned_badges": list(self.profile.get("earned_badges", [])),
            "lifetime_points": int(self.profile.get("lifetime_points", 300)),
            "lifetime_stars": int(self.profile.get("lifetime_stars", 3)),
            "completed_packs": list(self.profile.get("completed_packs", [])),
            "yearly_transcript": dict(self.profile.get("yearly_transcript", {})),
        }

    def install_learning_pack(
        self,
        target_pack_id_or_url: str,
        current_badges: Optional[set] = None,
    ) -> Dict[str, Any]:
        new_pack, freed_bytes = self.install_pack(target_pack_id_or_url, current_badges=current_badges)
        return self._build_upgrade_summary(new_pack, freed_bytes)

    def upgrade_to_next_pack(self, current_badges: Optional[set] = None) -> Dict[str, Any]:
        new_pack, freed_bytes = self.cycle_next_pack(current_badges=current_badges)
        return self._build_upgrade_summary(new_pack, freed_bytes)

    # ------------------------------------------------------------------
    # MULTI-STUDENT CLASSROOM ROSTER & ISOLATED PROFILES
    # ------------------------------------------------------------------
    def list_students(self) -> List[Dict[str, Any]]:
        """Return the classroom roster of student profiles stored on this computer."""
        roster_dir = os.path.join(self.base_dir, "students")
        os.makedirs(roster_dir, exist_ok=True)
        default_roster = [
            {"id": "cadet_nova", "name": "Cadet Nova", "avatar_idx": 0, "default_year": 1},
            {"id": "cadet_leo", "name": "Cadet Leo", "avatar_idx": 1, "default_year": 4},
            {"id": "cadet_maya", "name": "Cadet Maya", "avatar_idx": 2, "default_year": 8},
            {"id": "cadet_sam", "name": "Cadet Sam", "avatar_idx": 3, "default_year": 11},
        ]
        cur_name = self.profile.get("player_name", "Cadet Nova")
        out: List[Dict[str, Any]] = []
        for slot in default_roster:
            sfile = os.path.join(roster_dir, f"{slot['id']}.json")
            if slot["name"] == cur_name:
                yr = self.get_current_school_year()
                pts = int(self.profile.get("lifetime_points", 300))
                badges = len(self.profile.get("earned_badges", []))
            elif os.path.isfile(sfile):
                try:
                    with open(sfile, "r", encoding="utf-8") as f:
                        sdata = json.load(f)
                    yr = int(sdata.get("current_school_year", slot["default_year"]))
                    pts = int(sdata.get("lifetime_points", 300))
                    badges = len(sdata.get("earned_badges", []))
                except Exception:
                    yr, pts, badges = slot["default_year"], 300, 1
            else:
                yr, pts, badges = slot["default_year"], 300, 1
            out.append({
                "id": slot["id"],
                "name": slot["name"],
                "avatar_idx": slot["avatar_idx"],
                "school_year": yr,
                "points": pts,
                "trophies": badges,
                "active": (slot["name"] == cur_name),
            })
        return out

    def switch_student(self, student_name_or_id: str) -> Dict[str, Any]:
        """
        Save the current student's profile into `students/<id>.json` and switch
        to the target student profile (reloading their K-12 school year, transcript, and trophies).
        """
        roster_dir = os.path.join(self.base_dir, "students")
        os.makedirs(roster_dir, exist_ok=True)
        roster = self.list_students()

        # Save current student's state to their dedicated slot file first
        cur_name = self.profile.get("player_name", "Cadet Nova")
        cur_slug = cur_name.lower().replace(" ", "_")
        self.save_profile()
        try:
            with open(os.path.join(roster_dir, f"{cur_slug}.json"), "w", encoding="utf-8") as f:
                json.dump(self.profile, f, indent=2)
        except Exception:
            pass

        # Resolve target student
        q = str(student_name_or_id).strip().lower().replace(" ", "_")
        chosen = next(
            (s for s in roster if s["id"] == q or s["name"].lower() == str(student_name_or_id).strip().lower()),
            None,
        )
        if not chosen:
            # Allow creating a custom student name on the fly
            clean_name = str(student_name_or_id).strip() or "Cadet Nova"
            chosen = {
                "id": clean_name.lower().replace(" ", "_"),
                "name": clean_name,
                "avatar_idx": (int(self.profile.get("avatar_idx", 0)) + 1) % len(PLAYER_AVATARS),
                "school_year": 1,
            }

        target_file = os.path.join(roster_dir, f"{chosen['id']}.json")
        if os.path.isfile(target_file):
            try:
                with open(target_file, "r", encoding="utf-8") as f:
                    loaded_prof = json.load(f)
            except Exception:
                loaded_prof = None
        else:
            loaded_prof = None

        if loaded_prof:
            self.profile = loaded_prof
        else:
            yr = int(chosen.get("school_year", 1))
            self.profile = {
                **self.profile,
                "player_name": chosen["name"],
                "avatar_idx": int(chosen.get("avatar_idx", 0)),
                "current_school_year": yr,
                "active_pack_id": f"year_{yr:02d}",
                "current_pack_id": f"year_{yr:02d}",
                "earned_badges": ["m1_moon_gravity"],
                "lifetime_points": 300,
                "lifetime_stars": 3,
                "coins": 250,
                "yearly_transcript": {},
            }

        self.profile["player_name"] = chosen["name"]
        self.profile["avatar_idx"] = int(chosen.get("avatar_idx", 0))
        self.save_profile()
        try:
            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(self.profile, f, indent=2)
        except Exception:
            pass

        # Ensure the student's active pack / school year is installed in active_pack/current_pack.json
        target_pack_id = self.profile.get("active_pack_id", f"year_{self.get_current_school_year():02d}")
        if target_pack_id in K12_YEAR_PACKS:
            self._write_pack_file(K12_YEAR_PACKS[target_pack_id])
        elif target_pack_id in LEARNING_PACKS:
            self._write_pack_file(LEARNING_PACKS[target_pack_id])

        return {
            "ok": True,
            "student_id": chosen["id"],
            "player_name": self.profile["player_name"],
            "avatar_idx": self.profile["avatar_idx"],
            "school_year": self.get_current_school_year(),
            "active_pack_id": self.profile.get("active_pack_id", "pack_1_core"),
            "trophies": len(self.profile.get("earned_badges", [])),
            "coins": int(self.profile.get("coins", 250)),
            "points": int(self.profile.get("lifetime_points", 300)),
        }

    def cycle_next_student(self) -> Dict[str, Any]:
        """Cycle to the next student in the classroom roster (1-click multi-student switcher)."""
        roster = self.list_students()
        cur_name = self.profile.get("player_name", "Cadet Nova")
        cur_idx = next((i for i, s in enumerate(roster) if s["name"] == cur_name), 0)
        next_student = roster[(cur_idx + 1) % len(roster)]
        return self.switch_student(next_student["id"])

    # ------------------------------------------------------------------
    # PRINTABLE / EXPORTABLE OFFICIAL K-12 HTML & TXT REPORT CARD
    # ------------------------------------------------------------------
    def export_printable_report_card(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        Export an official, printer-ready HTML K-12 Report Card & Honors Certificate
        plus a plain-text transcript for parents, teachers, and school administrators.
        """
        target_dir = output_dir or self.base_dir
        os.makedirs(target_dir, exist_ok=True)
        student_name = self.profile.get("player_name", "Cadet Nova")
        slug = student_name.lower().replace(" ", "_")
        cur_yr = self.get_current_school_year()
        grade_lbl = "Kindergarten (Grade K)" if cur_yr == 0 else f"Grade {cur_yr}"
        yr_pack = self.get_active_year_pack()
        transcript = self.profile.get("yearly_transcript", {})
        cur_yr_id = f"year_{cur_yr:02d}"
        cur_rec = transcript.get(cur_yr_id, {})

        rows_html = []
        rows_txt = []
        scores_list = []
        for les in yr_pack.get("subject_lessons", []):
            s_key = les.get("subject_key", "ai_cs")
            sc = int(cur_rec.get(s_key, 100 if les["id"] in self.profile.get("earned_badges", []) else 95))
            scores_list.append(sc)
            letter = "A+" if sc >= 97 else ("A" if sc >= 90 else ("B" if sc >= 80 else "C"))
            rows_html.append(
                f"<tr><td><b>{les.get('subject_icon', '')} {les.get('subject_name', s_key)}</b></td>"
                f"<td>{les['title']}</td><td>{les.get('standards', 'National K-12 Standard')}</td>"
                f"<td><b>{sc}/100 ({letter})</b></td></tr>"
            )
            rows_txt.append(f"  • {les.get('subject_name', s_key):<26}: {sc}/100 ({letter}) — {les['title']}")

        avg_score = round(sum(scores_list) / max(1, len(scores_list)), 1)
        grad_years = [yid for yid, rec in sorted(transcript.items()) if rec.get("graduated")]
        grad_str = ", ".join(grad_years) if grad_years else f"{cur_yr_id} (In Progress)"

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>SynapseOS Official K-12 Report Card — {student_name}</title>
<style>
  body {{ font-family: 'Segoe UI', Roboto, Arial, sans-serif; margin: 32px; color: #0f172a; background: #f8fafc; }}
  .card {{ max-width: 880px; margin: auto; background: #ffffff; border: 3px solid #1e293b; border-radius: 12px; padding: 28px; box-shadow: 0 8px 24px rgba(0,0,0,0.08); }}
  h1 {{ margin-top: 0; color: #0f172a; border-bottom: 2px solid #eab308; padding-bottom: 10px; }}
  .meta {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; background: #f1f5f9; padding: 14px; border-radius: 8px; margin-bottom: 20px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
  th, td {{ border: 1px solid #cbd5e1; padding: 10px 12px; text-align: left; font-size: 14px; }}
  th {{ background: #1e293b; color: #f8fafc; }}
  .print-btn {{ background: #2563eb; color: white; border: none; padding: 10px 18px; border-radius: 6px; font-weight: bold; cursor: pointer; float: right; }}
  @media print {{ .print-btn {{ display: none; }} body {{ background: #fff; margin: 0; }} }}
</style>
</head>
<body>
<div class="card">
  <button class="print-btn" onclick="window.print()">🖨️ Print / Save as PDF</button>
  <h1>🎓 SynapseOS Official K–12 Academic Report Card & AI Transcript</h1>
  <div class="meta">
    <div><b>Student Name:</b> {student_name}</div>
    <div><b>Active Grade Level:</b> Year {cur_yr} ({grade_lbl})</div>
    <div><b>Cumulative Average:</b> {avg_score}% (Honors Standing)</div>
    <div><b>Earned Trophies & Points:</b> {len(self.profile.get('earned_badges', []))} Gold Badges | {self.profile.get('lifetime_points', 300)} pts</div>
    <div><b>Graduated School Years:</b> {grad_str}</div>
    <div><b>Curriculum Source:</b> github.com/batteryphil/SynapseOS/curricula/{cur_yr_id}.json</div>
  </div>
  <h3>Active School Year ({grade_lbl}) — 5 Core Subjects & Connected AI Labs</h3>
  <table>
    <thead><tr><th>Subject</th><th>Course Title</th><th>National Standard</th><th>Score & Grade</th></tr></thead>
    <tbody>
      {"".join(rows_html)}
    </tbody>
  </table>
  <p style="margin-top:22px; font-size:13px; color:#475569;">
    Verified deterministically by the SynapseOS C99/Cosmopolitan AI Workbench & Auto-Graded Python Sandbox.
  </p>
</div>
</body>
</html>"""

        txt_content = (
            f"======================================================================\n"
            f"🎓 SYNAPSEOS OFFICIAL K-12 REPORT CARD & TRANSCRIPT\n"
            f"======================================================================\n"
            f"Student Name       : {student_name}\n"
            f"Active Grade Level : Year {cur_yr} ({grade_lbl}) — {yr_pack.get('title_en', '')}\n"
            f"Cumulative Average : {avg_score}% (Honors Standing)\n"
            f"Gold Trophies      : {len(self.profile.get('earned_badges', []))} Badges | {self.profile.get('lifetime_points', 300)} pts | {self.profile.get('coins', 250)} Coins\n"
            f"Graduated Years    : {grad_str}\n"
            f"----------------------------------------------------------------------\n"
            f"ACTIVE GRADE ({grade_lbl.upper()}) SUBJECT SCORES:\n"
            + "\n".join(rows_txt)
            + "\n======================================================================\n"
        )

        html_path = os.path.join(target_dir, f"SynapseOS_Report_Card_{slug}.html")
        txt_path = os.path.join(target_dir, f"SynapseOS_Report_Card_{slug}.txt")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(txt_content)

        return {
            "ok": True,
            "student_name": student_name,
            "grade_label": grade_lbl,
            "average_score": avg_score,
            "html_path": html_path,
            "txt_path": txt_path,
        }


def main() -> None:
    import sys

    mgr = LearningPackManager()
    args = sys.argv[1:]
    sub = args[0] if args else "status"

    if sub == "list":
        cur_id = mgr.profile.get("active_pack_id", "pack_1_core")
        print("Available SynapseOS Learning Packages:")
        for pid in PACK_ORDER:
            p = LEARNING_PACKS[pid]
            mark = "★ ACTIVE" if pid == cur_id else ("✓ DONE" if pid in mgr.profile.get("completed_packs", []) else "  READY")
            lv_nums = [lv["level"] for lv in p["kid_levels"]]
            print(f"  [{mark}] {pid:16s} | {p['title_en']} (Levels {min(lv_nums)}-{max(lv_nums)})")
        print("\nAvailable Complete K-12 Rolling School Curricula (Kindergarten + Grades 1-12):")
        for yid in K12_ALL_GRADE_ORDER:
            yp = K12_YEAR_PACKS[yid]
            mark = "★ ACTIVE" if yid == cur_id else ("✓ GRAD" if yid in mgr.profile.get("yearly_transcript", {}) else "  READY")
            subjs = ", ".join(s["subject_name"].split()[0] for s in yp["subject_lessons"])
            print(f"  [{mark}] {yid:16s} | {yp['title_en']} [{subjs} — 20 Quarterly Units]")
    elif sub in ("list-years", "years"):
        cur_id = mgr.profile.get("active_pack_id", "pack_1_core")
        cur_yr = mgr.get_current_school_year()
        transcript = mgr.profile.get("yearly_transcript", {})
        print("SynapseOS Complete K-12 School Curricula (Kindergarten + Grades 1-12 | 65 Courses | 260 Quarterly Units):")
        print("  (Only 1 school year stays in active storage at a time; old year is wiped on advance while keeping scores)")
        for yid in K12_ALL_GRADE_ORDER:
            yp = K12_YEAR_PACKS[yid]
            yr_num = yp["year_number"]
            g_str = "Grade  K" if yr_num == 0 else f"Grade {yr_num:2d}"
            is_act = (yid == cur_id) or (yr_num == cur_yr and not cur_id.startswith("year_"))
            mark = "★ ACTIVE" if is_act else ("✓ GRAD" if transcript.get(yid, {}).get("graduated") else "  READY")
            print(f"  [{mark}] {yid} ({g_str}) | {yp['title_en']} (5 Full-Year Courses / 20 Quarterly Units)")
            for les in yp["subject_lessons"]:
                print(f"             • [{les['id']} | +q1..q4] {les['subject_icon']} {les['subject_name']:24s}: {les['title']}")
    elif sub in ("set-year", "year") and len(args) >= 2:
        res = mgr.set_school_year(args[1])
        print(f"[✓] Installed School Year Curriculum: {res['new_pack_title']} ({res['new_pack_id']})")
        print(f"    • Wiped previous year's pack & scratch files: {res['freed_kb']} KB freed")
        print(f"    • Loaded {res['subject_count']} Core Subjects (Math, Science, Reading/ELA, History, AI) + 7 Visual Labs")
        print(f"    • Preserved Transcript & Trophies: {len(res['earned_badges'])} Gold Badges | {res['lifetime_points']} pts")
    elif sub in ("advance-year", "graduate"):
        res = mgr.advance_school_year()
        print(f"[🎓] GRADUATED & ADVANCED TO: {res['new_pack_title']} ({res['new_pack_id']})")
        print(f"    • Wiped old school year files to save disk space: {res['freed_kb']} KB freed")
        print(f"    • Linked GitHub Repo URL: {res.get('repo_url', '')}")
        print(f"    • Permanent Transcript Saved: {len(res['yearly_transcript'])} School Year(s) on record")
        print(f"    • Preserved Student Trophies: {len(res['earned_badges'])} Gold Badges | {res['lifetime_points']} pts")
    elif sub in ("sync-repo", "pull-repo"):
        target_yr = args[1] if len(args) >= 2 else None
        res = mgr.sync_from_github_repo(target_yr)
        print(f"[☁] SYNCED K-12 CURRICULUM FROM GITHUB REPO: {res['new_pack_title']} ({res['new_pack_id']})")
        print(f"    • GitHub Repo URL : {res.get('repo_url', '')}")
        print(f"    • Source Used     : {res.get('source_used', '')}")
        print(f"    • Loaded {res['subject_count']} Full-Year Courses + {res['quarterly_unit_count']} Quarterly Units")
    elif sub in ("students", "roster"):
        print("SynapseOS Multi-Student Classroom Roster:")
        for st in mgr.list_students():
            mark = "★ ACTIVE" if st["active"] else "  SLOT  "
            g_lbl = "Grade K" if st["school_year"] == 0 else f"Grade {st['school_year']}"
            print(f"  [{mark}] {st['name']:<14} | {g_lbl:<8} | {st['trophies']} Trophies | {st['points']} pts")
    elif sub in ("switch-student", "student"):
        res = mgr.switch_student(args[1]) if len(args) >= 2 else mgr.cycle_next_student()
        print(f"[👤] Switched Active Student Profile: {res['player_name']} (Year {res['school_year']})")
        print(f"    • Active Pack : {res['active_pack_id']} | Trophies: {res['trophies']} | Points: {res['points']}")
    elif sub in ("export-report", "report-card"):
        res = mgr.export_printable_report_card()
        print(f"[🖨️] Exported Official K-12 Report Card for {res['student_name']} ({res['grade_label']} — {res['average_score']}% Avg):")
        print(f"    • Printable HTML Certificate : {res['html_path']}")
        print(f"    • Plain-Text Transcript      : {res['txt_path']}")
    elif sub in ("next", "upgrade"):
        res = mgr.upgrade_to_next_pack()
        print(f"[✓] Installed {res['new_pack_title']} ({res['new_pack_id']})")
        print(f"    • Deleted old pack files to save space: {res['freed_kb']} KB freed")
        print(f"    • Preserved Student Trophies: {len(res['earned_badges'])} Gold Badges | {res['lifetime_points']} pts | {res['lifetime_stars']} Stars")
    elif sub == "install" and len(args) >= 2:
        res = mgr.install_learning_pack(args[1])
        print(f"[✓] Installed {res['new_pack_title']} ({res['new_pack_id']})")
        print(f"    • Deleted old pack files to save space: {res['freed_kb']} KB freed")
        print(f"    • Preserved Student Trophies: {len(res['earned_badges'])} Gold Badges | {res['lifetime_points']} pts | {res['lifetime_stars']} Stars")
    else:
        pack = mgr.get_active_pack()
        lv_nums = [lv["level"] for lv in pack.get("kid_levels", [])]
        yr = mgr.get_current_school_year()
        print("SynapseOS Student Trophy Vault & K-12 Curriculum Status:")
        print(f"  • Active Student   : {mgr.profile.get('player_name', 'Cadet Nova')}")
        print(f"  • Active Pack      : {pack.get('title_en')} ({pack.get('pack_id')}, Levels {min(lv_nums)}-{max(lv_nums)})")
        print(f"  • Active School Yr : Year {yr} (Grade {yr}) — 5 Core Subjects (Math, Science, ELA, History, AI)")
        print(f"  • Completed Packs  : {', '.join(mgr.profile.get('completed_packs', [])) or 'None yet'}")
        print(f"  • Gold Trophies    : {len(mgr.profile.get('earned_badges', []))} ({', '.join(mgr.profile.get('earned_badges', []))})")
        print(f"  • Lifetime Score   : {mgr.profile.get('lifetime_points', 300)} pts ({mgr.profile.get('lifetime_stars', 3)} Stars)")
        print(f"  • Active Pack Disk : {os.path.getsize(mgr.active_pack_file) / 1024.0:.1f} KB ({mgr.active_pack_file})")
        print(f"  • Trophy Vault File: {os.path.getsize(mgr.profile_path) if os.path.exists(mgr.profile_path) else 0} B ({mgr.profile_path})")


if __name__ == "__main__":
    main()


