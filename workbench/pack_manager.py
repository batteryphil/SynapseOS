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
import urllib.request
from typing import Dict, Any, List, Optional, Tuple


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
        default_profile = {
            "active_pack_id": "pack_1_core",
            "current_pack_id": "pack_1_core",
            "completed_packs": [],
            "earned_badges": ["m1_moon_gravity"],
            "lifetime_points": 300,
            "lifetime_stars": 3,
            "packs_installed_count": 1,
            "last_freed_bytes": 0,
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
    ) -> None:
        if earned_badges is not None:
            merged = set(self.profile.get("earned_badges", [])) | set(earned_badges)
            self.profile["earned_badges"] = sorted(merged)
        if bonus_points > 0:
            self.profile["lifetime_points"] = int(self.profile.get("lifetime_points", 300)) + bonus_points
        if bonus_stars > 0:
            self.profile["lifetime_stars"] = int(self.profile.get("lifetime_stars", 3)) + bonus_stars
        self.profile["current_pack_id"] = self.profile.get("active_pack_id", "pack_1_core")

        try:
            with open(self.profile_path, "w", encoding="utf-8") as f:
                json.dump(self.profile, f, indent=2)
        except Exception:
            pass

    def award_badge(self, badge_id: str, points: int = 100, stars: int = 3) -> bool:
        """Award a trophy badge to the student profile if not already earned. Persists to disk immediately."""
        existing = set(self.profile.get("earned_badges", []))
        was_new = badge_id not in existing
        existing.add(badge_id)
        if was_new:
            self.save_profile(earned_badges=existing, bonus_points=points, bonus_stars=stars)
        else:
            self.save_profile(earned_badges=existing)
        return was_new

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

    def install_pack(
        self,
        target_pack_id_or_url: str,
        current_badges: Optional[set] = None,
    ) -> Tuple[Dict[str, Any], int]:
        """
        Save student trophies/scores, delete old learning package files to save space,
        and install the requested learning pack (by ID, local JSON path, or HTTPS URL).
        """
        old_pid = self.profile.get("active_pack_id", "pack_1_core")
        completed = list(self.profile.get("completed_packs", []))
        if old_pid not in completed:
            completed.append(old_pid)
        self.profile["completed_packs"] = completed

        # Award +300 bonus points & +3 stars + pack completion trophy badge!
        pack_badge = f"trophy_{old_pid}_complete"
        merged_badges = set(self.profile.get("earned_badges", [])) | (current_badges or set()) | {pack_badge}
        self.save_profile(earned_badges=merged_badges, bonus_points=300, bonus_stars=3)

        # Delete old learning package files from disk first!
        freed_bytes = self._purge_old_pack_files()

        # Load new pack from URL, local file, or built-in catalog
        new_pack: Optional[Dict[str, Any]] = None
        if target_pack_id_or_url.startswith(("http://", "https://")):
            try:
                with urllib.request.urlopen(target_pack_id_or_url, timeout=6) as resp:
                    new_pack = json.loads(resp.read().decode("utf-8"))
            except Exception:
                new_pack = None
        elif os.path.isfile(target_pack_id_or_url):
            try:
                with open(target_pack_id_or_url, "r", encoding="utf-8") as f:
                    new_pack = json.load(f)
            except Exception:
                new_pack = None

        if not new_pack:
            pid = target_pack_id_or_url if target_pack_id_or_url in LEARNING_PACKS else "pack_1_core"
            new_pack = LEARNING_PACKS[pid]

        new_pid = new_pack.get("pack_id", "pack_1_core")
        self.profile["active_pack_id"] = new_pid
        self.profile["current_pack_id"] = new_pid
        self.profile["packs_installed_count"] = int(self.profile.get("packs_installed_count", 1)) + 1
        self._write_pack_file(new_pack)
        self.save_profile()
        return new_pack, freed_bytes

    def cycle_next_pack(self, current_badges: Optional[set] = None) -> Tuple[Dict[str, Any], int]:
        """Advance to the next Learning Package (Pack 1 -> Pack 2 -> Pack 3 -> Pack 1), purging old pack files."""
        cur_pid = self.profile.get("active_pack_id", "pack_1_core")
        idx = PACK_ORDER.index(cur_pid) if cur_pid in PACK_ORDER else 0
        next_pid = PACK_ORDER[(idx + 1) % len(PACK_ORDER)]
        return self.install_pack(next_pid, current_badges=current_badges)

    def _build_upgrade_summary(self, new_pack: Dict[str, Any], freed_bytes: int) -> Dict[str, Any]:
        return {
            "new_pack_id": new_pack.get("pack_id", "pack_1_core"),
            "new_pack_title": new_pack.get("title_en", "New Pack"),
            "new_pack_title_fr": new_pack.get("title_fr", "Nouveau Pack"),
            "freed_bytes": freed_bytes,
            "freed_kb": round(max(1024, freed_bytes) / 1024.0, 1),
            "purged_files": 1,
            "earned_badges": list(self.profile.get("earned_badges", [])),
            "lifetime_points": int(self.profile.get("lifetime_points", 300)),
            "lifetime_stars": int(self.profile.get("lifetime_stars", 3)),
            "completed_packs": list(self.profile.get("completed_packs", [])),
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
        print("SynapseOS Student Trophy Vault & Learning Pack Status:")
        print(f"  • Active Pack      : {pack.get('title_en')} ({pack.get('pack_id')}, Levels {min(lv_nums)}-{max(lv_nums)})")
        print(f"  • Completed Packs  : {', '.join(mgr.profile.get('completed_packs', [])) or 'None yet'}")
        print(f"  • Gold Trophies    : {len(mgr.profile.get('earned_badges', []))} ({', '.join(mgr.profile.get('earned_badges', []))})")
        print(f"  • Lifetime Score   : {mgr.profile.get('lifetime_points', 300)} pts ({mgr.profile.get('lifetime_stars', 3)} Stars)")
        print(f"  • Active Pack Disk : {os.path.getsize(mgr.active_pack_file) / 1024.0:.1f} KB ({mgr.active_pack_file})")
        print(f"  • Trophy Vault File: {os.path.getsize(mgr.profile_path) if os.path.exists(mgr.profile_path) else 0} B ({mgr.profile_path})")


if __name__ == "__main__":
    main()
