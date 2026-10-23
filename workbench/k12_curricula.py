#!/usr/bin/env python3
"""
SynapseOS Complete K-12 Rolling Year-by-Year School Curriculum (`workbench/k12_curricula.py`)
=============================================================================================
Defines all 12 self-contained school years (`year_01` through `year_12`, Grades 1-12) and
writes them to `curricula/year_01.json` .. `curricula/year_12.json` for easy GitHub repo
hosting and annual updates.

Each Yearly Package (`year_01` .. `year_12`) includes:
  1. 5 Core Traditional + AI School Subject Modules (`subject_lessons`):
     - Mathematics (`math`)
     - Science (`science`)
     - Reading, Writing & Language Arts (`ela`)
     - Social Studies, History & Geography (`history`)
     - Connected AI & Computer Science Assignment (`ai_cs`)
  2. 7 Interactive Visual Lab Levels (`kid_levels`, bilingual EN/FR) tuned for that grade level.
"""

import json
import os
from typing import Dict, Any, List


YEAR_SPECS: List[Dict[str, Any]] = [
    {
        "year": 1,
        "pack_id": "year_01",
        "grade_label": "Grade 1 (Ages 6-7)",
        "band": "Band A: Elementary Discovery",
        "theme_en": "Year 1 (Grade 1): Counting, Sky & Seasons, Phonics, Maps & Robot Senses",
        "theme_fr": "Année 1 (CP) : Compter, Saisons, Lecture, Cartes & Sens du Robot",
        "short_en": "Year 1 (Grade 1)",
        "short_fr": "Année 1 (CP)",
        "math": {
            "title": "Y1 Math: Counting to 100, Addition & 2D Shapes",
            "story": (
                "TRADITIONAL MATH LESSON (GRADE 1):\n"
                "Numbers help us count everything around us! When we put two groups together, we use Addition (+). "
                "When we take away, we use Subtraction (-). We also compare numbers using Greater Than (>) and Less Than (<).\n\n"
                "• Example: If Lumi's rocket has 100 fuel units and we add 60 more, 100 + 60 = 160 fuel units!\n"
                "• Geometric Shapes: The landing pad is a flat rectangle, and the Moon is a round circle (sphere)."
            ),
            "code": (
                "# 📐 YEAR 1 MATH ASSIGNMENT: Addition & Comparing Numbers\n"
                "starting_fuel = 100\n"
                "bonus_fuel = 60\n"
                "total_fuel = starting_fuel + bonus_fuel\n"
                "pad_width = 52\n"
                "print(f'Total Rocket Fuel: {total_fuel} (Is {total_fuel} > 120? {total_fuel > 120})')\n"
                "assert total_fuel == 160, 'Total fuel should be 160!'\n"
            ),
            "lab_id": "moon_lander",
            "preset": {"gravity": 1.4, "fuel_capacity": 160.0, "wind": 0.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 150.0,
        },
        "science": {
            "title": "Y1 Science: Day & Night, Moon Phases & Push/Pull Forces",
            "story": (
                "TRADITIONAL SCIENCE LESSON (GRADE 1):\n"
                "Every object in the universe feels Pushes and Pulls called Forces!\n"
                "• Gravity is an invisible PULL force that pulls objects down toward the ground.\n"
                "• A Rocket Thruster is a PUSH force that pushes the rocket upward into the sky.\n"
                "• The Moon is smaller than Earth, so the Moon's gravity pull (1.62) is much gentler than Earth's (9.8)!"
            ),
            "code": (
                "# 🔬 YEAR 1 SCIENCE LAB: Push (Thrust) vs. Pull (Gravity)\n"
                "moon_gravity_pull = 1.62\n"
                "earth_gravity_pull = 9.80\n"
                "rocket_thruster_push = 2.65\n"
                "can_lift_off_moon = rocket_thruster_push > moon_gravity_pull\n"
                "print(f'Moon Pull: {moon_gravity_pull} | Rocket Push: {rocket_thruster_push} | Liftoff: {can_lift_off_moon}')\n"
                "assert can_lift_off_moon is True\n"
            ),
            "lab_id": "moon_lander",
            "preset": {"gravity": 1.62, "thruster_power": 1.85, "fuel_capacity": 180.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 160.0,
        },
        "ela": {
            "title": "Y1 Reading & Phonics: Short Stories, Sight Words & Main Character",
            "story": (
                "TRADITIONAL READING & LANGUAGE ARTS LESSON (GRADE 1):\n"
                "Read this short story out loud:\n"
                "  \"Lumi is a little silver robot. Lumi looks for the bright gold star in the maze. "
                "Lumi steps over the hot red lava and wins a shiny trophy!\"\n\n"
                "• Reading Check:\n"
                "  1. Who is the main character? -> Lumi the robot.\n"
                "  2. What is the setting (where does it happen)? -> Inside the maze.\n"
                "  3. Sight Words to practice: look, bright, over, little, find."
            ),
            "code": (
                "# 📖 YEAR 1 READING CHECK: Story Comprehension\n"
                "main_character = 'Lumi'\n"
                "goal_item = 'gold star'\n"
                "hazard_to_avoid = 'red lava'\n"
                "sentence = f'{main_character} found the {goal_item} and avoided the {hazard_to_avoid}!'\n"
                "print(sentence)\n"
                "assert 'Lumi' in sentence and 'gold star' in sentence\n"
            ),
            "lab_id": "rl_gridworld",
            "preset": {"alpha": 0.35, "gamma": 0.95, "epsilon": 0.10},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 50.0,
        },
        "history": {
            "title": "Y1 Social Studies: My Community & Compass Directions (N, S, E, W)",
            "story": (
                "TRADITIONAL SOCIAL STUDIES & GEOGRAPHY LESSON (GRADE 1):\n"
                "Maps help people in our community find schools, parks, libraries, and homes!\n"
                "Every map has a Compass Rose with 4 Cardinal Directions:\n"
                "  • North (Up ↑)\n"
                "  • East  (Right →)\n"
                "  • South (Down ↓)\n"
                "  • West  (Left ←)\n"
                "In our Maze Map, Lumi starts in the West (left) and travels East (right) around the lava to reach the Treasure!"
            ),
            "code": (
                "# 🗺️ YEAR 1 GEOGRAPHY LAB: Using the 4 Compass Directions\n"
                "compass = {'North': (0, -1), 'East': (1, 0), 'South': (0, 1), 'West': (-1, 0)}\n"
                "for direction, step in compass.items():\n"
                "    print(f'Compass Direction: {direction:<6} -> Map Step: {step}')\n"
                "assert len(compass) == 4\n"
            ),
            "lab_id": "rl_gridworld",
            "preset": {"alpha": 0.35, "gamma": 0.95, "epsilon": 0.08},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 50.0,
        },
        "ai_cs": {
            "title": "Y1 AI Assignment: Teaching Lumi's Sensors & First Moon Landing",
            "story": (
                "YEAR 1 BUILT-IN AI & CODING ASSIGNMENT:\n"
                "Now bring your Grade 1 Math, Science, Reading, and Map skills together! "
                "Give Lumi's rocket 180 units of fuel, gentle Moon gravity (1.62), and train the AI brain for 10 generations!"
            ),
            "code": (
                "# 🤖 YEAR 1 AI CAPSTONE ASSIGNMENT\n"
                "from workbench.labs.moon_lander import NEATMoonLanderLab\n\n"
                "lab = NEATMoonLanderLab()\n"
                "lab.update_param('gravity', 1.62)\n"
                "lab.update_param('fuel_capacity', 180.0)\n"
                "stats = lab.fast_forward_generations(8)\n"
                "print(f\"Year 1 AI Mission Complete! Best Score: {stats['best_ever']}\")\n"
            ),
            "lab_id": "moon_lander",
            "preset": {"gravity": 1.62, "fuel_capacity": 180.0, "landing_bonus": 260.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 170.0,
        },
    },
    {
        "year": 2,
        "pack_id": "year_02",
        "grade_label": "Grade 2 (Ages 7-8)",
        "band": "Band A: Elementary Discovery",
        "theme_en": "Year 2 (Grade 2): Place Value, Habitats & Food Chains, Nouns/Verbs & Continents",
        "theme_fr": "Année 2 (CE1) : Unités/Dizaines, Chaînes Alimentaires, Grammaire & Continents",
        "short_en": "Year 2 (Grade 2)",
        "short_fr": "Année 2 (CE1)",
        "math": {
            "title": "Y2 Math: Place Value (Hundreds, Tens, Ones) & 2-Digit Addition",
            "story": (
                "TRADITIONAL MATH LESSON (GRADE 2):\n"
                "In a 3-digit number like 245:\n"
                "  • 2 is in the Hundreds place (200)\n"
                "  • 4 is in the Tens place (40)\n"
                "  • 5 is in the Ones place (5)\n"
                "We also classify numbers as Even (0, 2, 4, 6, 8) or Odd (1, 3, 5, 7, 9)."
            ),
            "code": (
                "# 📐 YEAR 2 MATH ASSIGNMENT: Place Value Breakdown\n"
                "score = 245\n"
                "hundreds = score // 100\n"
                "tens = (score % 100) // 10\n"
                "ones = score % 10\n"
                "print(f'{score} = {hundreds} hundreds + {tens} tens + {ones} ones')\n"
                "assert hundreds * 100 + tens * 10 + ones == score\n"
            ),
            "lab_id": "swarm_ecosystem",
            "preset": {"num_prey": 40.0, "num_predators": 3.0, "food_count": 35.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 120.0,
        },
        "science": {
            "title": "Y2 Science: States of Matter (Solid, Liquid, Gas) & Ocean Food Chains",
            "story": (
                "TRADITIONAL SCIENCE LESSON (GRADE 2):\n"
                "1. States of Matter: Ice is a Solid, ocean water is a Liquid, and air/steam is a Gas.\n"
                "2. Ocean Habitat Food Chain:\n"
                "   Sunlight & Kelp (Producers) -> Green Fish (Prey Herbivores) -> Red Sharks (Predators).\n"
                "   Every living thing needs energy from food to survive and grow!"
            ),
            "code": (
                "# 🔬 YEAR 2 SCIENCE LAB: Ocean Food Chain Energy\n"
                "kelp_orbs = 35\n"
                "green_fish = 40\n"
                "red_sharks = 3\n"
                "print(f'Food Chain: {kelp_orbs} Kelp -> {green_fish} Fish -> {red_sharks} Sharks')\n"
                "assert green_fish > red_sharks, 'A healthy habitat has more prey than predators!'\n"
            ),
            "lab_id": "swarm_ecosystem",
            "preset": {"num_prey": 40.0, "num_predators": 3.0, "food_count": 35.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 120.0,
        },
        "ela": {
            "title": "Y2 Reading & Grammar: Nouns, Action Verbs & Finding the Main Idea",
            "story": (
                "TRADITIONAL LANGUAGE ARTS LESSON (GRADE 2):\n"
                "• A NOUN is a person, place, or thing (like `rocket`, `ocean`, `fish`, `star`).\n"
                "• A VERB is an action word that tells what a noun does (like `swim`, `dodge`, `steer`, `land`).\n"
                "• Main Idea: The most important point an author wants you to learn in a paragraph."
            ),
            "code": (
                "# 📖 YEAR 2 GRAMMAR LAB: Sorting Nouns and Action Verbs\n"
                "nouns = ['fish', 'shark', 'ocean', 'kelp']\n"
                "verbs = ['swim', 'dodge', 'gather', 'learn']\n"
                "for n, v in zip(nouns, verbs):\n"
                "    print(f'The {n} (NOUN) can {v} (VERB)!')\n"
                "assert len(nouns) == 4 and len(verbs) == 4\n"
            ),
            "lab_id": "swarm_ecosystem",
            "preset": {"num_prey": 38.0, "num_predators": 3.0, "food_count": 32.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 110.0,
        },
        "history": {
            "title": "Y2 Social Studies: The 7 Continents, 5 Oceans & Timelines",
            "story": (
                "TRADITIONAL SOCIAL STUDIES LESSON (GRADE 2):\n"
                "Earth has 7 Continents (North America, South America, Europe, Africa, Asia, Australia, Antarctica) "
                "and 5 Oceans (Pacific, Atlantic, Indian, Southern, Arctic).\n"
                "Historians use a Timeline to order events from Past -> Present -> Future!"
            ),
            "code": (
                "# 🌍 YEAR 2 GEOGRAPHY CHECK: 7 Continents & 5 Oceans\n"
                "continents = ['North America', 'South America', 'Europe', 'Africa', 'Asia', 'Australia', 'Antarctica']\n"
                "oceans = ['Pacific', 'Atlantic', 'Indian', 'Southern', 'Arctic']\n"
                "print(f'Earth has {len(continents)} Continents and {len(oceans)} Oceans!')\n"
                "assert len(continents) == 7 and len(oceans) == 5\n"
            ),
            "lab_id": "rl_gridworld",
            "preset": {"goal_reward": 140.0, "lava_penalty": -100.0, "alpha": 0.30},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 60.0,
        },
        "ai_cs": {
            "title": "Y2 AI Assignment: Rewards vs. Penalties in the Maze & Ocean",
            "story": (
                "YEAR 2 BUILT-IN AI ASSIGNMENT:\n"
                "How does an AI know what is good or bad? We give it a Positive Number (+150) for finding treasure "
                "and a Negative Number (-100) for stepping in lava!"
            ),
            "code": (
                "# 🤖 YEAR 2 AI CAPSTONE: Tuning Rewards & Penalties\n"
                "from workbench.labs.rl_gridworld import RLGridWorldLab\n\n"
                "lab = RLGridWorldLab()\n"
                "lab.update_param('goal_reward', 150.0)\n"
                "lab.update_param('lava_penalty', -100.0)\n"
                "stats = lab.fast_forward_generations(35)\n"
                "print(f\"Year 2 Maze AI Wins: {stats['species']} | Best Return: {stats['best_ever']}\")\n"
            ),
            "lab_id": "rl_gridworld",
            "preset": {"goal_reward": 150.0, "lava_penalty": -100.0, "alpha": 0.35},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 60.0,
        },
    },
    {
        "year": 3,
        "pack_id": "year_03",
        "grade_label": "Grade 3 (Ages 8-9)",
        "band": "Band A: Elementary Discovery",
        "theme_en": "Year 3 (Grade 3): Multiplication, Solar System Gravity, Cause/Effect & Trade",
        "theme_fr": "Année 3 (CE2) : Multiplication, Système Solaire, Cause/Effet & Échanges",
        "short_en": "Year 3 (Grade 3)",
        "short_fr": "Année 3 (CE2)",
        "math": {
            "title": "Y3 Math: Multiplication, Division, Area & Unit Fractions",
            "story": (
                "TRADITIONAL MATH LESSON (GRADE 3):\n"
                "• Multiplication (*) is fast repeated addition: 6 rockets × 10 fuel tanks = 60 tanks!\n"
                "• Division (/) splits a total into equal groups: 60 ÷ 6 = 10.\n"
                "• Area of a Rectangle = Length × Width.\n"
                "• Fractions: 1/2 means 1 part out of 2 equal parts (0.50)."
            ),
            "code": (
                "# 📐 YEAR 3 MATH ASSIGNMENT: Multiplication, Area & Fractions\n"
                "grid_cols = 10\n"
                "grid_rows = 7\n"
                "total_grid_area = grid_cols * grid_rows\n"
                "half_area = total_grid_area / 2\n"
                "print(f'Grid Area: {grid_cols} x {grid_rows} = {total_grid_area} tiles (1/2 is {half_area})')\n"
                "assert total_grid_area == 70\n"
            ),
            "lab_id": "rl_gridworld",
            "preset": {"alpha": 0.30, "gamma": 0.95, "epsilon": 0.12},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 60.0,
        },
        "science": {
            "title": "Y3 Science: The Solar System, Planetary Gravity & Magnetism",
            "story": (
                "TRADITIONAL SCIENCE LESSON (GRADE 3):\n"
                "Our Solar System has 8 planets orbiting the Sun: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune.\n"
                "More massive planets pull harder with Gravity:\n"
                "  • Moon Gravity:  1.62 m/s²\n"
                "  • Mars Gravity:  3.72 m/s² (more than 2× the Moon!)\n"
                "  • Earth Gravity: 9.80 m/s² (6× the Moon!)"
            ),
            "code": (
                "# 🔬 YEAR 3 SCIENCE LAB: Comparing Weight Across Worlds\n"
                "mass_kg = 100.0\n"
                "for world, g in [('Moon', 1.62), ('Mars', 3.72), ('Earth', 9.80)]:\n"
                "    force_newtons = mass_kg * g\n"
                "    print(f'{world:<6} Gravity: {g} m/s^2 -> Downward Pull: {force_newtons:.0f} N')\n"
            ),
            "lab_id": "moon_lander",
            "preset": {"gravity": 3.72, "fuel_capacity": 200.0, "thruster_power": 1.85},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 150.0,
        },
        "ela": {
            "title": "Y3 Reading & Writing: Topic Sentences, Prefixes & Cause-and-Effect",
            "story": (
                "TRADITIONAL LANGUAGE ARTS LESSON (GRADE 3):\n"
                "• Prefixes change a word's meaning: `un-` (not, as in *unbalanced*), `re-` (again, as in *rebuild*).\n"
                "• Cause and Effect:\n"
                "  - CAUSE: Why something happened (\"Mars has stronger gravity than the Moon\").\n"
                "  - EFFECT: What happened as a result (\"The rocket needed more thruster power to land softly\")."
            ),
            "code": (
                "# 📖 YEAR 3 ELA CHECK: Prefixes & Cause-and-Effect\n"
                "prefix_words = {'un' + 'balanced': 'not balanced', 're' + 'train': 'train again'}\n"
                "for word, meaning in prefix_words.items():\n"
                "    print(f'{word}: {meaning}')\n"
                "assert 'unbalanced' in prefix_words\n"
            ),
            "lab_id": "cartpole_rl",
            "preset": {"gravity": 9.8, "force_mag": 13.0, "wind_gust": 0.15},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 260.0,
        },
        "history": {
            "title": "Y3 Social Studies: Latitude/Longitude & Economics (Scarcity & Budgets)",
            "story": (
                "TRADITIONAL SOCIAL STUDIES LESSON (GRADE 3):\n"
                "• Geography: Latitude lines run East-West (like the Equator); Longitude lines run North-South.\n"
                "• Economics: Scarcity means resources are limited! A rocket only has a limited budget of Fuel (160 units), "
                "so the AI pilot must save fuel instead of wasting it."
            ),
            "code": (
                "# 💰 YEAR 3 ECONOMICS LAB: Managing a Scarce Fuel Budget\n"
                "fuel_budget = 160.0\n"
                "cost_per_burn = 0.55\n"
                "max_burns = int(fuel_budget // cost_per_burn)\n"
                "print(f'With {fuel_budget} fuel, the rocket can fire its main thruster {max_burns} times!')\n"
                "assert max_burns == 290\n"
            ),
            "lab_id": "moon_lander",
            "preset": {"gravity": 1.62, "fuel_capacity": 160.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 170.0,
        },
        "ai_cs": {
            "title": "Y3 AI Assignment: 10-Generation Evolution Loop Across Planets",
            "story": (
                "YEAR 3 BUILT-IN AI ASSIGNMENT:\n"
                "Run a 10-generation evolution loop in Python and observe how Trial-and-Error Selection improves "
                "the rocket fleet's score!"
            ),
            "code": (
                "# 🤖 YEAR 3 AI CAPSTONE: 10-Generation Evolution Loop\n"
                "from workbench.labs.moon_lander import NEATMoonLanderLab\n\n"
                "lab = NEATMoonLanderLab()\n"
                "stats = lab.fast_forward_generations(10)\n"
                "print(f\"Gen {stats['generation']} | Best Score: {stats['best_ever']}\")\n"
            ),
            "lab_id": "moon_lander",
            "preset": {"gravity": 1.62, "fuel_capacity": 170.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 170.0,
        },
    },
    {
        "year": 4,
        "pack_id": "year_04",
        "grade_label": "Grade 4 (Ages 9-10)",
        "band": "Band B: Upper Elementary & Intro Python",
        "theme_en": "Year 4 (Grade 4): Angles & Decimals, Light/Laser Waves, Summaries & Explorers",
        "theme_fr": "Année 4 (CM1) : Angles & Décimaux, Ondes Laser, Résumés & Explorateurs",
        "short_en": "Year 4 (Grade 4)",
        "short_fr": "Année 4 (CM1)",
        "math": {
            "title": "Y4 Math: Angles (Acute, Right, Obtuse) & Decimal Tenths/Hundredths",
            "story": (
                "TRADITIONAL MATH LESSON (GRADE 4):\n"
                "• Angles measure how much a line turns in degrees (°):\n"
                "  - Acute Angle: smaller than 90° (like our Lidar beams at 30° and 60°!)\n"
                "  - Right Angle: a square corner of exactly 90°\n"
                "  - Obtuse Angle: between 90° and 180°\n"
                "• Decimals: 0.25 is 2 tenths + 5 hundredths (25/100 or 1/4)."
            ),
            "code": (
                "# 📐 YEAR 4 MATH ASSIGNMENT: Classifying Lidar Beam Angles\n"
                "angles_deg = [30, 60, 90, 120]\n"
                "for a in angles_deg:\n"
                "    kind = 'Acute' if a < 90 else ('Right' if a == 90 else 'Obtuse')\n"
                "    print(f'{a:3d} degrees -> {kind} Angle')\n"
            ),
            "lab_id": "raycast_car",
            "preset": {"sensor_range": 140.0, "max_speed": 4.5, "track_width": 42.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 200.0,
        },
        "science": {
            "title": "Y4 Science: Light Waves, Laser Reflection & Kinetic vs. Potential Energy",
            "story": (
                "TRADITIONAL SCIENCE LESSON (GRADE 4):\n"
                "• Light & Lasers travel in straight waves until they bounce off an obstacle (Reflection). "
                "Lidar (Light Detection and Ranging) measures how far away a wall is using 5 laser beams!\n"
                "• Potential Energy is stored energy (a rocket high in the sky); Kinetic Energy is energy of motion (a fast racecar)."
            ),
            "code": (
                "# 🔬 YEAR 4 SCIENCE LAB: Lidar Distance & Kinetic Motion\n"
                "from workbench.labs.raycast_car import NEATRaycastCarLab\n"
                "lab = NEATRaycastCarLab()\n"
                "car = lab.cars[0]\n"
                "rays = lab._cast_rays(car)\n"
                "print('5 Laser Beam Normalized Readings:', [round(r, 2) for r in rays])\n"
            ),
            "lab_id": "raycast_car",
            "preset": {"sensor_range": 150.0, "max_speed": 5.0, "track_width": 40.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 220.0,
        },
        "ela": {
            "title": "Y4 Reading & Writing: Nonfiction Summaries, Similes & Metaphors",
            "story": (
                "TRADITIONAL LANGUAGE ARTS LESSON (GRADE 4):\n"
                "• A Simile compares two things using 'like' or 'as': \"The Lidar beams swept the road like a lighthouse.\"\n"
                "• A Metaphor compares directly: \"The neural network is the driver's brain.\"\n"
                "• Writing a Summary: State the main idea + 2 key supporting facts in your own words."
            ),
            "code": (
                "# 📖 YEAR 4 ELA LAB: Identifying Similes vs. Metaphors\n"
                "s1 = 'The laser car corners like a cheetah.'\n"
                "is_simile = 'like' in s1 or ' as ' in s1\n"
                "print(f'Sentence: {s1} -> Simile: {is_simile}')\n"
                "assert is_simile is True\n"
            ),
            "lab_id": "raycast_car",
            "preset": {"sensor_range": 140.0, "max_speed": 4.8},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 200.0,
        },
        "history": {
            "title": "Y4 Social Studies: Age of Exploration, Navigation Instruments & Maps",
            "story": (
                "TRADITIONAL SOCIAL STUDIES LESSON (GRADE 4):\n"
                "For centuries, explorers used magnetic compasses, astrolabes, and star charts to navigate across unknown oceans "
                "without hitting reefs. Today, autonomous vehicles use Lidar, radar, and digital waypoint maps!"
            ),
            "code": (
                "# 🧭 YEAR 4 HISTORY & NAVIGATION LAB: Counting Track Waypoints\n"
                "from workbench.labs.raycast_car import NEATRaycastCarLab\n"
                "lab = NEATRaycastCarLab()\n"
                "print(f'Circuit has {len(lab.waypoints)} navigation waypoints around the track!')\n"
                "assert len(lab.waypoints) == 24\n"
            ),
            "lab_id": "raycast_car",
            "preset": {"sensor_range": 150.0, "track_width": 42.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 200.0,
        },
        "ai_cs": {
            "title": "Y4 AI Assignment: Python For-Loops Testing 3 Lidar Sensor Ranges",
            "story": (
                "YEAR 4 BUILT-IN AI ASSIGNMENT:\n"
                "Write a Python `for` loop that tests 3 different Lidar `sensor_range` distances (60, 120, and 180 pixels) "
                "and compares how far the self-driving car travels!"
            ),
            "code": (
                "# 🤖 YEAR 4 AI CAPSTONE: Lidar Sensor Sweep in Python\n"
                "from workbench.labs.raycast_car import NEATRaycastCarLab\n\n"
                "for rng in [60.0, 120.0, 180.0]:\n"
                "    lab = NEATRaycastCarLab()\n"
                "    lab.update_param('sensor_range', rng)\n"
                "    t = lab.fast_forward_generations(5)\n"
                "    print(f\"Lidar Range {rng:5.1f}px -> Best Score: {t['best_ever']:6.1f}\")\n"
            ),
            "lab_id": "raycast_car",
            "preset": {"sensor_range": 160.0, "max_speed": 5.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 220.0,
        },
    },
    {
        "year": 5,
        "pack_id": "year_05",
        "grade_label": "Grade 5 (Ages 10-11)",
        "band": "Band B: Upper Elementary & Intro Python",
        "theme_en": "Year 5 (Grade 5): Coordinate Planes (x,y), Food Webs, Persuasive Writing & Civics",
        "theme_fr": "Année 5 (CM2) : Plan Cartésien (x,y), Écosystèmes, Argumentation & Citoyenneté",
        "short_en": "Year 5 (Grade 5)",
        "short_fr": "Année 5 (CM2)",
        "math": {
            "title": "Y5 Math: The (x, y) Coordinate Plane, Order of Operations & Averages",
            "story": (
                "TRADITIONAL MATH LESSON (GRADE 5):\n"
                "• Coordinate Plane: Every point on a 2D graph has an address `(x, y)` where `x` is horizontal and `y` is vertical.\n"
                "• Order of Operations (PEMDAS): Parentheses -> Exponents -> Multiply/Divide -> Add/Subtract.\n"
                "• Mean (Average): Add all scores together and divide by how many numbers there are!"
            ),
            "code": (
                "# 📐 YEAR 5 MATH ASSIGNMENT: Averages & Coordinate Points\n"
                "scores = [84.0, 90.0, 92.0, 96.0]\n"
                "mean_score = sum(scores) / len(scores)\n"
                "print(f'Scores: {scores} -> Mean (Average): {mean_score:.1f}%')\n"
                "assert mean_score == 90.5\n"
            ),
            "lab_id": "nn_playground",
            "preset": {"dataset_id": 1.0, "hidden_neurons": 8.0, "learning_rate": 0.24},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 85.0,
        },
        "science": {
            "title": "Y5 Science: Ecosystem Energy Pyramids (10% Rule) & Conservation of Matter",
            "story": (
                "TRADITIONAL SCIENCE LESSON (GRADE 5):\n"
                "In an ecosystem energy pyramid, only about 10% of energy moves up to the next trophic level "
                "(Plants -> Herbivores -> Predators), while 90% is used for motion and heat. "
                "That is why ecosystems have many plants, fewer herbivores, and even fewer apex predators!"
            ),
            "code": (
                "# 🔬 YEAR 5 SCIENCE LAB: The 10% Trophic Energy Pyramid\n"
                "producer_energy = 1000.0\n"
                "herbivore_energy = producer_energy * 0.10\n"
                "predator_energy = herbivore_energy * 0.10\n"
                "print(f'Producers: {producer_energy} -> Herbivores: {herbivore_energy} -> Predators: {predator_energy}')\n"
                "assert predator_energy == 10.0\n"
            ),
            "lab_id": "swarm_ecosystem",
            "preset": {"num_prey": 45.0, "num_predators": 4.0, "food_count": 40.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 130.0,
        },
        "ela": {
            "title": "Y5 Reading & Writing: Citing Evidence, Greek/Latin Roots & Persuasive Essays",
            "story": (
                "TRADITIONAL LANGUAGE ARTS LESSON (GRADE 5):\n"
                "• Greek & Latin Roots: `neuro` (nerve/brain), `chron` (time), `photo` (light), `tele` (far), `metry` (measure -> telemetry!).\n"
                "• Persuasive Writing: Always back up your Claim with measurable Evidence (data from your experiment!)."
            ),
            "code": (
                "# 📖 YEAR 5 ELA CHECK: Greek & Latin Scientific Roots\n"
                "roots = {'tele': 'far', 'metry': 'measure', 'neuro': 'brain/nerve'}\n"
                "print('Telemetry =', roots['tele'], '+', roots['metry'])\n"
                "assert len(roots) == 3\n"
            ),
            "lab_id": "nn_playground",
            "preset": {"dataset_id": 1.0, "hidden_neurons": 8.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 85.0,
        },
        "history": {
            "title": "Y5 Social Studies: Branches of Government, Checks & Balances & Civic Rules",
            "story": (
                "TRADITIONAL SOCIAL STUDIES & CIVICS LESSON (GRADE 5):\n"
                "Constitutional democracies divide power into 3 Branches with Checks and Balances:\n"
                "  1. Legislative (makes the laws)\n"
                "  2. Executive (carries out the laws)\n"
                "  3. Judicial (evaluates whether rules are followed fairly)\n"
                "Similarly, SynapseOS uses a Safety Shield to check commands before execution!"
            ),
            "code": (
                "# 🏛️ YEAR 5 CIVICS & SAFETY SHIELD LAB\n"
                "from cortex.engine import CortexEngine\n"
                "check = CortexEngine.evaluate_command_safety('df -h')\n"
                "print('Civic Safety Check on df -h:', check['category'], '| Allowed:', check['allowed'])\n"
                "assert check['allowed'] is True\n"
            ),
            "lab_id": "nn_playground",
            "preset": {"dataset_id": 2.0, "hidden_neurons": 8.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 85.0,
        },
        "ai_cs": {
            "title": "Y5 AI Assignment: Growing Hidden Neurons on the 2D Coordinate Plane",
            "story": (
                "YEAR 5 BUILT-IN AI ASSIGNMENT:\n"
                "Use `modify_brain_structure(delta_neurons=4)` in Python to grow hidden neurons and separate "
                "Concentric Rings on the `(x, y)` coordinate plane!"
            ),
            "code": (
                "# 🤖 YEAR 5 AI CAPSTONE: Growing Hidden Neurons\n"
                "from workbench.labs.nn_playground import NeuralPlaygroundLab\n\n"
                "lab = NeuralPlaygroundLab()\n"
                "lab.update_param('dataset_id', 1)  # Concentric Rings\n"
                "lab.modify_brain_structure(delta_neurons=4)\n"
                "stats = lab.fast_forward_generations(30)\n"
                "print(f\"Hidden Neurons: {stats['species']} -> Accuracy: {stats['best_ever']}%\")\n"
            ),
            "lab_id": "nn_playground",
            "preset": {"dataset_id": 1.0, "hidden_neurons": 12.0, "learning_rate": 0.25},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 88.0,
        },
    },
    {
        "year": 6,
        "pack_id": "year_06",
        "grade_label": "Grade 6 (Ages 11-12)",
        "band": "Band B: Early Middle School",
        "theme_en": "Year 6 (Grade 6): Ratios & Negative Numbers, Cell Biology, Argumentation & Ancient World",
        "theme_fr": "Année 6 (6e) : Ratios & Nombres Négatifs, Biologie Cellulaire & Antiquité",
        "short_en": "Year 6 (Grade 6)",
        "short_fr": "Année 6 (6e)",
        "math": {
            "title": "Y6 Math: Ratios, Percentages, Negative Numbers & [-1, 1] Normalization",
            "story": (
                "TRADITIONAL MATH LESSON (GRADE 6):\n"
                "• Ratios & Proportions compare two quantities: if a rocket has 120 fuel out of a 160 capacity, "
                "the ratio is `120 / 160 = 0.75` (or `75%`).\n"
                "• Negative Numbers (`< 0`) represent opposite directions: `-3.5 m/s` means moving left, `+3.5 m/s` means moving right.\n"
                "• Neural networks work best when inputs are normalized into the ratio `[-1.0, +1.0]`!"
            ),
            "code": (
                "# 📐 YEAR 6 MATH ASSIGNMENT: Ratios & Sensor Normalization\n"
                "raw_x = 170.0\n"
                "pad_x = 320.0\n"
                "half_width = 300.0\n"
                "normalized_x = (raw_x - pad_x) / half_width\n"
                "print(f'Raw x={raw_x} relative to pad={pad_x} -> Normalized Ratio: {normalized_x:.2f}')\n"
                "assert -1.0 <= normalized_x <= 1.0\n"
            ),
            "lab_id": "moon_lander",
            "preset": {"gravity": 1.62, "wind": 0.30, "fuel_capacity": 170.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 165.0,
        },
        "science": {
            "title": "Y6 Science: Cell Biology, Biological Neurons & Thermal Energy",
            "story": (
                "TRADITIONAL SCIENCE LESSON (GRADE 6):\n"
                "Your brain contains 86 billion biological nerve cells called Neurons!\n"
                "  1. Dendrites receive incoming signals (Inputs).\n"
                "  2. The Soma (cell body) sums the signals together.\n"
                "  3. The Axon fires an electrical pulse across Synapses to the next neuron (Output)!\n"
                "Artificial Neural Networks in SynapseOS are directly modeled on biological dendrites, somas, and synapses."
            ),
            "code": (
                "# 🔬 YEAR 6 BIOLOGY LAB: Dendrites, Soma & Axon Firing\n"
                "import math\n"
                "dendrite_inputs = [0.8, -0.4, 0.5]\n"
                "synapse_weights = [1.2, 0.5, 0.9]\n"
                "soma_sum = sum(x * w for x, w in zip(dendrite_inputs, synapse_weights))\n"
                "axon_output = math.tanh(soma_sum)\n"
                "print(f'Soma Sum: {soma_sum:.2f} -> Axon Firing Output: {axon_output:.3f}')\n"
            ),
            "lab_id": "nn_playground",
            "preset": {"dataset_id": 2.0, "hidden_neurons": 10.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 86.0,
        },
        "ela": {
            "title": "Y6 ELA: Claims vs. Opinions, Technical Precision & Informative Essays",
            "story": (
                "TRADITIONAL LANGUAGE ARTS LESSON (GRADE 6):\n"
                "• An Unsupported Opinion is a feeling without data (\"I think my AI is really smart\").\n"
                "• A Verifiable Claim cites specific measurements (\"Increasing hidden neurons from 2 to 10 raised classification accuracy from 68% to 94%\")."
            ),
            "code": (
                "# 📖 YEAR 6 ELA LAB: Writing a Data-Backed Scientific Claim\n"
                "acc_before, acc_after = 68.0, 94.0\n"
                "improvement = acc_after - acc_before\n"
                "claim = f'Adding 8 hidden neurons improved accuracy by +{improvement:.1f} percentage points.'\n"
                "print(claim)\n"
                "assert improvement == 26.0\n"
            ),
            "lab_id": "nn_playground",
            "preset": {"dataset_id": 2.0, "hidden_neurons": 10.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 86.0,
        },
        "history": {
            "title": "Y6 World History: Ancient Mesopotamia, Egypt, Greece & Logic",
            "story": (
                "TRADITIONAL ANCIENT HISTORY LESSON (GRADE 6):\n"
                "• Mesopotamia invented cuneiform writing and base-60 math (60 seconds in a minute, 360° in a circle!).\n"
                "• Ancient Egypt used geometry to survey the Nile River.\n"
                "• Ancient Greece (Socrates, Plato, Aristotle, Euclid) developed formal logic and the Socratic Method—teaching by asking guiding questions, just like Lumi!"
            ),
            "code": (
                "# 🏺 YEAR 6 ANCIENT HISTORY & BASE-60 GEOMETRY CHECK\n"
                "babylonian_base = 60\n"
                "degrees_in_circle = babylonian_base * 6\n"
                "print(f'Mesopotamian Base-{babylonian_base} -> {degrees_in_circle} degrees in a full circle!')\n"
                "assert degrees_in_circle == 360\n"
            ),
            "lab_id": "raycast_car",
            "preset": {"sensor_range": 155.0, "max_speed": 5.2},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 230.0,
        },
        "ai_cs": {
            "title": "Y6 AI Assignment: Sensor Normalization & Forward Propagation in Python",
            "story": (
                "YEAR 6 BUILT-IN AI ASSIGNMENT:\n"
                "Normalize raw rocket sensor readings into `[-1.0, 1.0]` using Grade 6 ratios and feed them into a NEAT neural network!"
            ),
            "code": (
                "# 🤖 YEAR 6 AI CAPSTONE: Normalizing Sensor Ratios for a Neural Brain\n"
                "from workbench.labs.neat_core import NEATPopulation\n\n"
                "pop = NEATPopulation(num_inputs=4, num_outputs=2, pop_size=20)\n"
                "obs = [(280.0 - 320.0) / 300.0, (365.0 - 120.0) / 350.0, -1.2 / 6.0, 0.8 / 6.0]\n"
                "out = pop.best_genome.forward(obs)\n"
                "print('Normalized Inputs:', [round(x, 3) for x in obs], '-> Outputs:', [round(y, 3) for y in out])\n"
            ),
            "lab_id": "moon_lander",
            "preset": {"gravity": 1.62, "wind": 0.35, "fuel_capacity": 175.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 165.0,
        },
    },
    {
        "year": 7,
        "pack_id": "year_07",
        "grade_label": "Grade 7 (Ages 12-13)",
        "band": "Band C: Middle School Foundations",
        "theme_en": "Year 7 (Grade 7): Linear Equations & Probability, Newton's Laws, Natural Selection & Reward Shaping",
        "theme_fr": "Année 7 (5e) : Équations Linéaires & Probabilités, Lois de Newton & Sélection Naturelle",
        "short_en": "Year 7 (Grade 7)",
        "short_fr": "Année 7 (5e)",
        "math": {
            "title": "Y7 Math: Linear Equations (y = mx + b) & Probability (0.0 to 1.0)",
            "story": (
                "TRADITIONAL MATH LESSON (GRADE 7):\n"
                "• A Linear Equation `y = m * x + b` has a Slope `m` (rate of change) and a y-intercept `b` (bias!).\n"
                "  Notice that a single neuron computes `z = w * x + b`—the weight `w` IS the slope `m`, and the bias `b` IS the intercept!\n"
                "• Probability ranges from `0.0` (impossible) to `1.0` (certain). In RL, `epsilon = 0.15` means a 15% chance of exploring!"
            ),
            "code": (
                "# 📐 YEAR 7 MATH ASSIGNMENT: y = mx + b as a Single Neuron\n"
                "w_slope = 2.5\n"
                "b_intercept = -0.4\n"
                "for x in [-1.0, 0.0, 1.0, 2.0]:\n"
                "    y = w_slope * x + b_intercept\n"
                "    print(f'x = {x:4.1f} -> y = {w_slope}*{x} + ({b_intercept}) = {y:5.2f}')\n"
            ),
            "lab_id": "nn_playground",
            "preset": {"dataset_id": 2.0, "hidden_neurons": 10.0, "learning_rate": 0.25},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 88.0,
        },
        "science": {
            "title": "Y7 Science: Newton's Three Laws of Motion (F = ma) & Natural Selection",
            "story": (
                "TRADITIONAL SCIENCE LESSON (GRADE 7):\n"
                "• Newton's 1st Law (Inertia): An object in motion stays in motion unless acted on by a net force.\n"
                "• Newton's 2nd Law: Force = Mass × Acceleration (`F = m * a`, so `a = F / m`).\n"
                "• Newton's 3rd Law: Every action has an equal and opposite reaction (rocket exhaust pushes down; rocket accelerates up!).\n"
                "• Darwin's Natural Selection: Organisms with beneficial genetic traits survive and pass their genes to offspring."
            ),
            "code": (
                "# 🔬 YEAR 7 PHYSICS LAB: Newton's 2nd Law (a = F / m)\n"
                "force_newtons = 15.0\n"
                "mass_kg = 1.1\n"
                "acceleration = force_newtons / mass_kg\n"
                "print(f'Force={force_newtons}N, Mass={mass_kg}kg -> Acceleration a = {acceleration:.2f} m/s^2')\n"
                "assert round(acceleration, 2) == 13.64\n"
            ),
            "lab_id": "cartpole_rl",
            "preset": {"gravity": 9.8, "force_mag": 14.0, "wind_gust": 0.25},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 280.0,
        },
        "ela": {
            "title": "Y7 ELA: Cause vs. Correlation, Logical Fallacies & Structured Lab Reports",
            "story": (
                "TRADITIONAL LANGUAGE ARTS LESSON (GRADE 7):\n"
                "In persuasive and scientific writing, avoid Logical Fallacies:\n"
                "• False Cause (Correlation vs. Causation): Just because two events happen together doesn't mean one caused the other! "
                "To prove causation in science and AI, change ONE variable at a time (a Controlled Experiment)."
            ),
            "code": (
                "# 📖 YEAR 7 SCIENTIFIC WRITING CHECK: Controlled Experiment Variables\n"
                "independent_variable = 'mutation_sigma'\n"
                "dependent_variable = 'best_prey_score'\n"
                "controlled_variables = ['num_prey', 'num_predators', 'food_count']\n"
                "print(f'Testing {independent_variable} -> Measuring {dependent_variable} (Holding {controlled_variables} constant)')\n"
            ),
            "lab_id": "swarm_ecosystem",
            "preset": {"num_prey": 40.0, "num_predators": 4.0, "mutation_sigma": 0.22},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 135.0,
        },
        "history": {
            "title": "Y7 World History: The Scientific Revolution, Printing Press & Global Exchange",
            "story": (
                "TRADITIONAL WORLD HISTORY LESSON (GRADE 7):\n"
                "During the Renaissance and Scientific Revolution (1450–1700), Gutenberg's printing press spread knowledge rapidly, "
                "while Galileo, Kepler, and Isaac Newton replaced guesswork with mathematical laws of motion and empirical experiments."
            ),
            "code": (
                "# 📜 YEAR 7 HISTORY TIMELINE: Milestones of the Scientific Revolution\n"
                "milestones = [(1440, 'Gutenberg Printing Press'), (1609, 'Galileo Telescope & Motion'), (1687, 'Newton Principia Mathematica')]\n"
                "for year, event in milestones:\n"
                "    print(f'{year}: {event}')\n"
            ),
            "lab_id": "moon_lander",
            "preset": {"gravity": 3.72, "wind": 0.40, "landing_bonus": 280.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 160.0,
        },
        "ai_cs": {
            "title": "Y7 AI Assignment: Stopping Reward Hacking with Potential-Based Shaping",
            "story": (
                "YEAR 7 BUILT-IN AI ASSIGNMENT:\n"
                "Design a custom Python reward shaping function that prevents rockets from hovering forever and rewards soft touchdowns!"
            ),
            "code": (
                "# 🤖 YEAR 7 AI CAPSTONE: Anti-Hover Reward Shaping\n"
                "def compute_reward(dist_to_pad: float, speed: float, landed: bool) -> float:\n"
                "    shaping = -110.0 * dist_to_pad - 45.0 * speed - 0.06\n"
                "    return shaping + (260.0 if landed else 0.0)\n\n"
                "print('Hovering high:', round(compute_reward(0.8, 0.1, False), 1))\n"
                "print('Soft landing: ', round(compute_reward(0.0, 0.05, True), 1))\n"
                "assert compute_reward(0.0, 0.05, True) > compute_reward(0.8, 0.1, False)\n"
            ),
            "lab_id": "moon_lander",
            "preset": {"gravity": 3.72, "wind": 0.45, "landing_bonus": 280.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 165.0,
        },
    },
    {
        "year": 8,
        "pack_id": "year_08",
        "grade_label": "Grade 8 (Ages 13-14)",
        "band": "Band C: Middle School Foundations",
        "theme_en": "Year 8 (Grade 8): Pythagorean Theorem, Genetics & Waves, Debate & Q-Learning vs. SARSA",
        "theme_fr": "Année 8 (4e) : Théorème de Pythagore, Génétique, Débat & Q-Learning vs SARSA",
        "short_en": "Year 8 (Grade 8)",
        "short_fr": "Année 8 (4e)",
        "math": {
            "title": "Y8 Math: The Pythagorean Theorem (a² + b² = c²) & Euclidean Distance",
            "story": (
                "TRADITIONAL MATH LESSON (GRADE 8):\n"
                "In any right triangle with legs `a` and `b` and hypotenuse `c`:\n"
                "  `a² + b² = c²`   ->   `c = sqrt(a² + b²)`\n"
                "Every single AI lab in SynapseOS uses the Pythagorean Theorem (`math.hypot(dx, dy)`) to measure "
                "the exact straight-line distance from a car to a wall, a fish to a shark, or a rocket to the landing pad!"
            ),
            "code": (
                "# 📐 YEAR 8 MATH ASSIGNMENT: Pythagorean Euclidean Distance\n"
                "import math\n"
                "dx, dy = 3.0, 4.0\n"
                "hypotenuse = math.sqrt(dx**2 + dy**2)\n"
                "print(f'Right Triangle Legs ({dx}, {dy}) -> Hypotenuse c = {hypotenuse:.1f}')\n"
                "assert hypotenuse == 5.0\n"
            ),
            "lab_id": "raycast_car",
            "preset": {"sensor_range": 175.0, "max_speed": 5.8, "track_width": 34.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 240.0,
        },
        "science": {
            "title": "Y8 Science: Genetics (Genotype vs. Phenotype), Waves & Orbital Mechanics",
            "story": (
                "TRADITIONAL SCIENCE LESSON (GRADE 8):\n"
                "• Genetics: An organism's Genotype is its internal genetic code (like the 4 floating-point `genes` array in our Boids Swarm "
                "or the node/connection genes in NEAT), while its Phenotype is its observable behavior in the environment!\n"
                "• Mutations introduce variation; beneficial alleles increase in frequency across generations."
            ),
            "code": (
                "# 🔬 YEAR 8 GENETICS LAB: Genotype vs. Phenotype Crossover\n"
                "parent_a_genes = [1.4, 2.2, 0.6, 1.1]\n"
                "parent_b_genes = [1.6, 1.8, 0.8, 0.9]\n"
                "child_genotype = [(a + b) / 2.0 for a, b in zip(parent_a_genes, parent_b_genes)]\n"
                "print('Offspring Genotype:', [round(g, 2) for g in child_genotype])\n"
            ),
            "lab_id": "swarm_ecosystem",
            "preset": {"num_prey": 45.0, "num_predators": 5.0, "mutation_sigma": 0.18},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 140.0,
        },
        "ela": {
            "title": "Y8 ELA: Counterarguments, Socratic Seminar & Technical Lab Documentation",
            "story": (
                "TRADITIONAL LANGUAGE ARTS LESSON (GRADE 8):\n"
                "A strong argumentative essay doesn't ignore opposing views—it addresses the Counterargument fairly and "
                "explains the trade-offs with evidence.\n"
                "• Example Trade-off: Bold Q-Learning finds the shortest path along a cliff edge, whereas Cautious SARSA "
                "takes a slightly longer detour that is much safer when wind gusts are high!"
            ),
            "code": (
                "# 📖 YEAR 8 ELA & TRADE-OFF ANALYSIS\n"
                "tradeoff = {\n"
                "    'Q-Learning': 'Optimistic shortest path, higher risk near windy cliffs',\n"
                "    'SARSA': 'On-policy cautious path, accounts for exploration & wind slip'\n"
                "}\n"
                "for algo, summary in tradeoff.items():\n"
                "    print(f'• {algo:<10}: {summary}')\n"
            ),
            "lab_id": "rl_gridworld",
            "preset": {"use_sarsa": 1.0, "wind_prob": 0.15, "alpha": 0.35},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 50.0,
        },
        "history": {
            "title": "Y8 History & Civics: The Industrial Revolution, Constitutional Law & Automation",
            "story": (
                "TRADITIONAL HISTORY & CIVICS LESSON (GRADE 8):\n"
                "From the 18th-century steam engine and mechanical looms to 20th-century computers and 21st-century AI, "
                "each wave of automation transformed how people work, learn, and govern technology."
            ),
            "code": (
                "# 🏛️ YEAR 8 HISTORY OF COMPUTING & AUTOMATION\n"
                "eras = ['1769: Steam Engine', '1843: Ada Lovelace Algorithm', '1947: Transistor', '2026: Local Edge AI']\n"
                "print(' -> '.join(eras))\n"
            ),
            "lab_id": "rl_gridworld",
            "preset": {"use_sarsa": 0.0, "wind_prob": 0.10, "alpha": 0.35},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 50.0,
        },
        "ai_cs": {
            "title": "Y8 AI Assignment: Benchmarking Q-Learning vs. SARSA Near Lava Cliffs",
            "story": (
                "YEAR 8 BUILT-IN AI ASSIGNMENT:\n"
                "Run a head-to-head Python experiment comparing Off-Policy Q-Learning (`use_sarsa=0`) against "
                "On-Policy SARSA (`use_sarsa=1`) over 40 episodes!"
            ),
            "code": (
                "# 🤖 YEAR 8 AI CAPSTONE: Q-Learning vs. SARSA Head-to-Head\n"
                "from workbench.labs.rl_gridworld import RLGridWorldLab\n\n"
                "for sarsa_flag, name in [(0.0, 'Q-Learning'), (1.0, 'SARSA')]:\n"
                "    lab = RLGridWorldLab()\n"
                "    lab.update_param('use_sarsa', sarsa_flag)\n"
                "    lab.update_param('wind_prob', 0.10)\n"
                "    t = lab.fast_forward_generations(40)\n"
                "    print(f\"{name:<10} -> Wins: {t['species']:2d} | Best Return: {t['best_ever']:6.1f}\")\n"
            ),
            "lab_id": "rl_gridworld",
            "preset": {"use_sarsa": 1.0, "wind_prob": 0.10, "alpha": 0.35},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 55.0,
        },
    },
    {
        "year": 9,
        "pack_id": "year_09",
        "grade_label": "Grade 9 / Freshman (Ages 14-15)",
        "band": "Band C: High School Foundations",
        "theme_en": "Year 9 (Grade 9): Algebra I (Quadratics & Exponentials), Kinematics Physics & Spiral MLP",
        "theme_fr": "Année 9 (3e) : Algèbre I (Polynômes & Exponentielles), Cinématique & MLP Spirale",
        "short_en": "Year 9 (Grade 9)",
        "short_fr": "Année 9 (3e)",
        "math": {
            "title": "Y9 Math (Algebra I): Quadratic Polynomials (x²+y², xy) & Exponential Decay (γᵗ)",
            "story": (
                "TRADITIONAL ALGEBRA I LESSON (GRADE 9):\n"
                "• Linear functions (`ax + by + c = 0`) can only draw straight lines.\n"
                "• Quadratic Polynomials include second-degree terms like `x² + y²` (the equation of a circle!) and `x * y` (hyperbolas).\n"
                "• Exponential Functions `f(t) = A * γ^t` decay smoothly when `0 < γ < 1`—which is the exact Bellman Discount Factor `γ^t` "
                "and PRIME Moment decay factor!"
            ),
            "code": (
                "# 📐 YEAR 9 ALGEBRA I LAB: Quadratic Feature Basis & Exponential Discount\n"
                "x, y = 0.6, -0.4\n"
                "poly_features = [x, y, x**2 + y**2, x * y]\n"
                "gamma = 0.95\n"
                "discounted_10_steps = gamma ** 10\n"
                "print('Quadratic Features [x, y, r^2, xy]:', [round(f, 3) for f in poly_features])\n"
                "print(f'Discount gamma^10 (0.95^10): {discounted_10_steps:.4f}')\n"
            ),
            "lab_id": "nn_playground",
            "preset": {"dataset_id": 3.0, "hidden_neurons": 16.0, "learning_rate": 0.26, "synapse_density": 4.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 85.0,
        },
        "science": {
            "title": "Y9 Physics: Kinematics (v = v₀ + at), Vectors, Momentum & Mechanical Work",
            "story": (
                "TRADITIONAL PHYSICS LESSON (GRADE 9):\n"
                "• Velocity Vector `(vx, vy)` integrates acceleration over time step `dt`:\n"
                "  `vx_new = vx + ax * dt`,   `x_new = x + vx_new * dt`\n"
                "• Kinetic Energy `KE = 0.5 * m * v²` grows with the SQUARE of speed—which is why doubling a lander's impact speed "
                "quadruples the crash energy!"
            ),
            "code": (
                "# 🔬 YEAR 9 PHYSICS LAB: Kinematic Integration & Impact Energy\n"
                "mass = 10.0\n"
                "for speed in [1.0, 2.0, 4.0]:\n"
                "    ke = 0.5 * mass * (speed ** 2)\n"
                "    print(f'Speed = {speed:.1f} m/s -> Kinetic Energy = {ke:5.1f} Joules')\n"
            ),
            "lab_id": "moon_lander",
            "preset": {"gravity": 3.72, "wind": 0.50, "fuel_capacity": 200.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 165.0,
        },
        "ela": {
            "title": "Y9 ELA: World Literature, Thesis Architecture & Primary Source Analysis",
            "story": (
                "TRADITIONAL LANGUAGE ARTS LESSON (GRADE 9):\n"
                "A high-school analytical essay begins with a clear, falsifiable Thesis Statement that previews the logical mechanism "
                "(the 'how' and 'why'), followed by body paragraphs that synthesize quantitative and textual evidence."
            ),
            "code": (
                "# 📖 YEAR 9 THESIS BUILDER: Quantitative Evidence Synthesis\n"
                "thesis = (\n"
                "    'Enabling polynomial basis features (x^2+y^2, xy) with 16 hidden tanh neurons '\n"
                "    'allows a 2-layer perceptron to classify the non-linear Archimedean Spiral.'\n"
                ")\n"
                "print('Thesis Statement:', thesis)\n"
                "assert 'Archimedean Spiral' in thesis\n"
            ),
            "lab_id": "nn_playground",
            "preset": {"dataset_id": 3.0, "hidden_neurons": 16.0, "synapse_density": 4.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 85.0,
        },
        "history": {
            "title": "Y9 World History & Human Geography: The Enlightenment, Demographics & Energy",
            "story": (
                "TRADITIONAL WORLD HISTORY LESSON (GRADE 9):\n"
                "The Enlightenment championed open inquiry, encyclopedias, and universal education. "
                "In Human Geography, access to compute and educational tools across rural and low-resource regions "
                "depends on energy-efficient software that runs on existing low-wattage hardware."
            ),
            "code": (
                "# 🌍 YEAR 9 HUMAN GEOGRAPHY & ENERGY FOOTPRINT CALCULATION\n"
                "potato_pc_watts = 18.0\n"
                "cloud_gpu_watts = 700.0\n"
                "ratio = cloud_gpu_watts / potato_pc_watts\n"
                "print(f'Local 18W classroom node uses {ratio:.1f}x less power than a 700W datacenter GPU!')\n"
            ),
            "lab_id": "nn_playground",
            "preset": {"dataset_id": 3.0, "hidden_neurons": 16.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 85.0,
        },
        "ai_cs": {
            "title": "Y9 AI Assignment: Conquering the Archimedean Spiral with C99-Backed Backprop",
            "story": (
                "YEAR 9 BUILT-IN AI ASSIGNMENT:\n"
                "Train a 2-layer MLP (`hidden_neurons=16`, `synapse_density=4`, `learning_rate=0.26`) on the Archimedean Spiral (`dataset_id=3`) "
                "using the C99 backpropagation kernel!"
            ),
            "code": (
                "# 🤖 YEAR 9 AI CAPSTONE: Archimedean Spiral Backpropagation\n"
                "from workbench.labs.nn_playground import NeuralPlaygroundLab\n\n"
                "lab = NeuralPlaygroundLab()\n"
                "lab.update_param('dataset_id', 3)       # Archimedean Spiral\n"
                "lab.update_param('hidden_neurons', 16)\n"
                "lab.update_param('learning_rate', 0.26)\n"
                "lab.update_param('synapse_density', 4)\n"
                "stats = lab.fast_forward_generations(45)\n"
                "print(f\"Spiral Classification Accuracy: {stats['best_ever']}% | Loss: {stats['avg_fitness']}\")\n"
            ),
            "lab_id": "nn_playground",
            "preset": {"dataset_id": 3.0, "hidden_neurons": 16.0, "learning_rate": 0.26, "synapse_density": 4.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 85.0,
        },
    },
    {
        "year": 10,
        "pack_id": "year_10",
        "grade_label": "Grade 10 / Sophomore (Ages 15-16)",
        "band": "Band D: High School Advanced AI & STEM",
        "theme_en": "Year 10 (Grade 10): Trigonometry & Graph Theory, Chemistry, Rhetoric & NEAT Speciation",
        "theme_fr": "Année 10 (2nde) : Trigonométrie & Graphes, Chimie, Rhétorique & Spéciation NEAT",
        "short_en": "Year 10 (Grade 10)",
        "short_fr": "Année 10 (2nde)",
        "math": {
            "title": "Y10 Math (Geometry & Trig): Unit Circle (sin, cos, atan2) & Directed Graphs",
            "story": (
                "TRADITIONAL GEOMETRY & TRIGONOMETRY LESSON (GRADE 10):\n"
                "• Unit Circle Trigonometry: A ray at angle `θ` (in radians) has direction vector `(cos θ, sin θ)`.\n"
                "• Inverse Tangent `atan2(dy, dx)` recovers the exact angle `θ ∈ [-π, π]` from any `(dx, dy)` displacement.\n"
                "• Graph Theory: A feed-forward neural network is a Directed Acyclic Graph `G = (V, E)` with vertices (neurons) and weighted edges (synapses)."
            ),
            "code": (
                "# 📐 YEAR 10 TRIGONOMETRY LAB: Unit Circle Ray Projection\n"
                "import math\n"
                "car_x, car_y, heading = 320.0, 210.0, math.pi / 4.0  # 45 degrees\n"
                "dist = 100.0\n"
                "end_x = car_x + dist * math.cos(heading)\n"
                "end_y = car_y + dist * math.sin(heading)\n"
                "recovered_angle = math.atan2(end_y - car_y, end_x - car_x)\n"
                "print(f'Ray Endpoint: ({end_x:.1f}, {end_y:.1f}) | Angle: { math.degrees(recovered_angle):.1f} deg')\n"
            ),
            "lab_id": "raycast_car",
            "preset": {"sensor_range": 180.0, "max_speed": 6.2, "track_width": 32.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 260.0,
        },
        "science": {
            "title": "Y10 Chemistry: Stoichiometry, Activation Energy Barriers & Reaction Kinetics",
            "story": (
                "TRADITIONAL CHEMISTRY LESSON (GRADE 10):\n"
                "• Conservation of Mass (Stoichiometry): In a balanced chemical reaction (like rocket propellant `2H₂ + O₂ -> 2H₂O`), "
                "the number of atoms of each element is conserved.\n"
                "• Activation Energy (`E_a`): A reaction requires an energy threshold to fire—analogous to a neuron's activation threshold!"
            ),
            "code": (
                "# 🔬 YEAR 10 CHEMISTRY LAB: Rocket Propellant Stoichiometry (2 H2 + O2 -> 2 H2O)\n"
                "moles_H2 = 4.0\n"
                "moles_O2 = 2.0\n"
                "moles_H2O_produced = min(moles_H2, 2.0 * moles_O2)\n"
                "print(f'{moles_H2} mol H2 + {moles_O2} mol O2 -> {moles_H2O_produced} mol H2O + Thrust Energy!')\n"
                "assert moles_H2O_produced == 4.0\n"
            ),
            "lab_id": "moon_lander",
            "preset": {"gravity": 3.72, "thruster_power": 1.90, "fuel_capacity": 200.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 170.0,
        },
        "ela": {
            "title": "Y10 ELA: Formal Logic, Deductive/Inductive Reasoning & Synthesis Essays",
            "story": (
                "TRADITIONAL LANGUAGE ARTS LESSON (GRADE 10):\n"
                "• Deductive Reasoning moves from general axioms/theorems to specific guaranteed conclusions (like geometric proofs and Safety Shield rules).\n"
                "• Inductive Reasoning generalizes patterns from empirical observations (which is how Machine Learning trains from examples!)."
            ),
            "code": (
                "# 📖 YEAR 10 FORMAL LOGIC CHECK: Deductive vs. Inductive\n"
                "deductive_rule = lambda cmd: 'BLOCKED' if 'rm -rf /' in cmd else 'SAFE'\n"
                "print('Deductive Safety Check:', deductive_rule('rm -rf /'))\n"
                "assert deductive_rule('rm -rf /') == 'BLOCKED'\n"
            ),
            "lab_id": "raycast_car",
            "preset": {"sensor_range": 180.0, "max_speed": 6.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 250.0,
        },
        "history": {
            "title": "Y10 World History II & Comparative Systems: 20th Century Science & Open Standards",
            "story": (
                "TRADITIONAL WORLD HISTORY LESSON (GRADE 10):\n"
                "The 20th century saw the rise of international scientific collaboration, Apollo lunar guidance computers (with only 4 KB of RAM!), "
                "POSIX/Linux open operating systems, and the World Wide Web."
            ),
            "code": (
                "# 🛰️ YEAR 10 HISTORY LAB: Apollo Guidance Computer vs. SynapseOS Memory\n"
                "apollo_agc_ram_kb = 4.0\n"
                "prime_vault_kb = 67.03\n"
                "print(f'Apollo 11 RAM: {apollo_agc_ram_kb} KB | PRIME Attention Vault: {prime_vault_kb} KB')\n"
            ),
            "lab_id": "moon_lander",
            "preset": {"gravity": 1.62, "fuel_capacity": 160.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 180.0,
        },
        "ai_cs": {
            "title": "Y10 AI Assignment: NEAT Speciation Distance & Topological Crossover in Python",
            "story": (
                "YEAR 10 BUILT-IN AI ASSIGNMENT:\n"
                "Compute the NEAT Compatibility Distance `δ = (c₁·D / N) + c₃·W̄` between two evolving neural genomes and perform crossover!"
            ),
            "code": (
                "# 🤖 YEAR 10 AI CAPSTONE: NEAT Speciation & Crossover\n"
                "from workbench.labs.neat_core import NEATPopulation, NEATGenome\n\n"
                "pop = NEATPopulation(num_inputs=6, num_outputs=2, pop_size=20)\n"
                "g1, g2 = pop.genomes[0], pop.genomes[1]\n"
                "g1.mutate_add_node(pop.tracker)\n"
                "dist = NEATGenome.compatibility_distance(g1, g2)\n"
                "child = NEATGenome.crossover(g1, g2)\n"
                "print(f'Speciation Compatibility Distance: {dist:.3f} | Child Nodes: {len(child.nodes)}')\n"
            ),
            "lab_id": "raycast_car",
            "preset": {"sensor_range": 180.0, "max_speed": 6.2, "node_add_prob": 0.12},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 260.0,
        },
    },
    {
        "year": 11,
        "pack_id": "year_11",
        "grade_label": "Grade 11 / Junior (Ages 16-17)",
        "band": "Band D: High School Advanced AI & STEM",
        "theme_en": "Year 11 (Grade 11): Pre-Calculus, Matrices & Taylor Series, Neuroscience, Ethics & PRIME O(1) Attention",
        "theme_fr": "Année 11 (1re) : Matrices & Séries de Taylor, Neurosciences, Éthique & Attention PRIME O(1)",
        "short_en": "Year 11 (Grade 11)",
        "short_fr": "Année 11 (1re)",
        "math": {
            "title": "Y11 Math (Pre-Calculus & Linear Algebra): Matrices, Dot Products & Taylor Polynomials",
            "story": (
                "TRADITIONAL PRE-CALCULUS & LINEAR ALGEBRA LESSON (GRADE 11):\n"
                "• Dot Product: `q · k = Σ q_i * k_i` measures similarity between two vectors.\n"
                "• Second-Order Taylor Series of `e^s` around `s = 0`:\n"
                "    `exp(s) ≈ 1 + s + 0.5 * s²`\n"
                "  By replacing `exp(q·k / √d)` with its 2nd-order Taylor polynomial, PRIME Moment Attention factors the sum "
                "into fixed-size moment tensors `(S₀, S₁, S₂)` that require O(1) memory (`67 KB`) regardless of sequence length!"
            ),
            "code": (
                "# 📐 YEAR 11 PRE-CALCULUS LAB: 2nd-Order Taylor Approximation of exp(s)\n"
                "import math\n"
                "for s in [-0.5, -0.2, 0.0, 0.2, 0.5]:\n"
                "    exact = math.exp(s)\n"
                "    taylor2 = 1.0 + s + 0.5 * (s ** 2)\n"
                "    err = abs(exact - taylor2)\n"
                "    print(f's={s:5.2f} -> exp(s)={exact:.4f} | Taylor2={taylor2:.4f} | Error={err:.4f}')\n"
            ),
            "lab_id": "prime_attention",
            "preset": {"window_size": 64.0, "distractor_gap": 320.0, "use_qk_norm": 1.0, "lyapunov_bound": 25.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 88.0,
        },
        "science": {
            "title": "Y11 Biology & Neuroscience: Hebbian Synaptic Plasticity, Homeostasis & Lotka-Volterra",
            "story": (
                "TRADITIONAL NEUROSCIENCE & SYSTEMS BIOLOGY LESSON (GRADE 11):\n"
                "• Hebbian Plasticity (\"Neurons that fire together, wire together\"): Outer-product covariance updates `ΔS₁ = k_t v_t^T` "
                "store associative memories in synaptic matrices.\n"
                "• Homeostatic Regulation: Biological brains prevent runaway seizure excitation using inhibitory normalization—"
                "just like QK-Norm and Lyapunov norm projection in PRIME Attention!"
            ),
            "code": (
                "# 🔬 YEAR 11 NEUROSCIENCE LAB: Homeostatic Norm Projection (Lyapunov Stability)\n"
                "import math\n"
                "state_vec = [12.0, 16.0, 20.0]\n"
                "frob_norm = math.sqrt(sum(x*x for x in state_vec))\n"
                "c_max = 15.0\n"
                "scale = min(1.0, c_max / frob_norm)\n"
                "projected = [round(x * scale, 2) for x in state_vec]\n"
                "print(f'Raw Norm: {frob_norm:.2f} -> Projected to C_max={c_max}: {projected}')\n"
            ),
            "lab_id": "prime_attention",
            "preset": {"window_size": 64.0, "use_qk_norm": 1.0, "lyapunov_bound": 25.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 88.0,
        },
        "ela": {
            "title": "Y11 ELA: Reading Scientific Papers, Abstract Writing & Technical Seminars",
            "story": (
                "TRADITIONAL LANGUAGE ARTS LESSON (GRADE 11):\n"
                "Every peer-reviewed computer science or physics paper begins with a 4-part Abstract:\n"
                "  1. Context & Problem (e.g., Standard Transformer KV-cache grows as O(L), exhausting RAM on edge devices).\n"
                "  2. Proposed Method (Hybrid Sliding-Window + 2nd-Order PRIME Moment Attention).\n"
                "  3. Quantitative Results (Constant 67.03 KB state, 180,000+ tok/s in C99).\n"
                "  4. Conclusion & Impact."
            ),
            "code": (
                "# 📖 YEAR 11 SCIENTIFIC ABSTRACT VERIFIER\n"
                "abstract_sections = ['Problem: O(L) KV-Cache', 'Method: Taylor2 Moment State', 'Result: 67.03 KB O(1)', 'Impact: Edge AI']\n"
                "for i, sec in enumerate(abstract_sections, 1):\n"
                "    print(f'[{i}/4] {sec}')\n"
            ),
            "lab_id": "prime_attention",
            "preset": {"window_size": 64.0, "use_qk_norm": 1.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 88.0,
        },
        "history": {
            "title": "Y11 Civics, Law & AI Ethics: Student Privacy (FERPA/COPPA) & Open-Source Licensing",
            "story": (
                "TRADITIONAL PUBLIC POLICY & ETHICS LESSON (GRADE 11):\n"
                "• Privacy Laws (FERPA & COPPA) protect student records from unauthorized cloud collection.\n"
                "• Software Licensing: Open-source licenses (MIT, ISC, GPL) allow inspection and modification, whereas proprietary EULAs "
                "forbid copying or reverse-engineering code— while general mathematical and architectural ideas remain free for clean-room implementation."
            ),
            "code": (
                "# ⚖️ YEAR 11 AI ETHICS & PRIVACY AUDIT\n"
                "audit = {'cloud_telemetry_sent_bytes': 0, 'local_ram_mb': 57.5, 'clean_room_open_source': True}\n"
                "print('Classroom Privacy & License Audit:', audit)\n"
                "assert audit['cloud_telemetry_sent_bytes'] == 0\n"
            ),
            "lab_id": "prime_attention",
            "preset": {"window_size": 64.0, "use_qk_norm": 1.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 88.0,
        },
        "ai_cs": {
            "title": "Y11 AI Assignment: Benchmarking PRIME O(1) Moment Attention vs. Sliding Window",
            "story": (
                "YEAR 11 BUILT-IN AI ASSIGNMENT:\n"
                "Run the PRIME Moment Sliding-Window Lab in Python, comparing recall with QK-Norm enabled vs. disabled across long distractor gaps!"
            ),
            "code": (
                "# 🤖 YEAR 11 AI CAPSTONE: PRIME O(1) Memory Vault Benchmark\n"
                "from workbench.labs.prime_attention_lab import PrimeAttentionLab\n\n"
                "lab = PrimeAttentionLab()\n"
                "lab.update_param('use_qk_norm', 1.0)\n"
                "t = lab.fast_forward_generations(15)\n"
                "print(f\"PRIME Recall Score: {t['best_ever']}% | C99 Kernel Speed: {lab.c_bench['tokens_per_sec']:,.0f} tok/s\")\n"
            ),
            "lab_id": "prime_attention",
            "preset": {"window_size": 64.0, "distractor_gap": 256.0, "use_qk_norm": 1.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 88.0,
        },
    },
    {
        "year": 12,
        "pack_id": "year_12",
        "grade_label": "Grade 12 / Senior Capstone (Ages 17-18)",
        "band": "Band D: High School Advanced AI & STEM",
        "theme_en": "Year 12 (Grade 12): Calculus & Chain Rule Backprop, Euler-Lagrange Physics & Full-Stack C99/Python Capstone",
        "theme_fr": "Année 12 (Terminale) : Calcul Différentiel, Rétropropagation, Lagrange & Projet Final C99/Python",
        "short_en": "Year 12 (Grade 12)",
        "short_fr": "Année 12 (Terminale)",
        "math": {
            "title": "Y12 Math (Calculus & Statistics): Derivatives, Chain Rule Backprop & P50/P95 Latency",
            "story": (
                "TRADITIONAL CALCULUS & STATISTICS LESSON (GRADE 12):\n"
                "• Derivative of `tanh(z)`:  `d/dz tanh(z) = 1 - tanh²(z)`.\n"
                "• The Chain Rule of Calculus (`∂L/∂w₁ = (∂L/∂a₂) · (∂a₂/∂z₁) · (∂z₁/∂w₁)`) is the exact mathematical engine of "
                "Backpropagation used in `synapse_mlp_train_epochs`!\n"
                "• Order Statistics: P50 (median) and P95 (95th percentile tail latency) measure real-world system reliability."
            ),
            "code": (
                "# 📐 YEAR 12 CALCULUS LAB: Verifying Analytical Derivative vs. Finite Difference\n"
                "import math\n"
                "z = 0.65\n"
                "eps = 1e-5\n"
                "numerical_deriv = (math.tanh(z + eps) - math.tanh(z - eps)) / (2 * eps)\n"
                "analytical_deriv = 1.0 - (math.tanh(z) ** 2)\n"
                "print(f'Numerical: {numerical_deriv:.6f} | Analytical (1 - tanh^2): {analytical_deriv:.6f}')\n"
                "assert abs(numerical_deriv - analytical_deriv) < 1e-6\n"
            ),
            "lab_id": "nn_playground",
            "preset": {"dataset_id": 3.0, "hidden_neurons": 18.0, "learning_rate": 0.25, "l2_reg": 0.001},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 88.0,
        },
        "science": {
            "title": "Y12 Advanced Physics: Euler-Lagrange Inverted Pendulum Equations & Hardware Thermals",
            "story": (
                "TRADITIONAL ADVANCED PHYSICS LESSON (GRADE 12):\n"
                "The coupled non-linear differential equations governing an inverted pendulum on a motorized cart (derived via Euler-Lagrange mechanics) are:\n"
                "  `θ̈ = (g sin θ - cos θ · [(F + m_p L θ̇² sin θ) / (m_c + m_p)]) / (L · (4/3 - m_p cos²θ / (m_c + m_p)))`\n"
                "In `synapse_sim_core.c`, our C99 kernel integrates this exact equation at 50,000 steps per millisecond!"
            ),
            "code": (
                "# 🔬 YEAR 12 ADVANCED PHYSICS LAB: C99 CartPole Euler-Lagrange Kernel\n"
                "from workbench.labs.cartpole_rl import CartPoleLab\n"
                "lab = CartPoleLab()\n"
                "stats = lab.fast_forward_generations(15)\n"
                "print(f\"CartPole Policy Fitness: {stats['best_ever']} | Nodes: {stats['champion_nodes']}\")\n"
            ),
            "lab_id": "cartpole_rl",
            "preset": {"gravity": 9.8, "pole_length": 0.65, "wind_gust": 0.30},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 320.0,
        },
        "ela": {
            "title": "Y12 Senior Thesis: Reproducible Engineering Benchmarks & Failure-Mode Analysis",
            "story": (
                "TRADITIONAL SENIOR CAPSTONE WRITING LESSON (GRADE 12):\n"
                "A rigorous engineering thesis never hides limitations—it separates process RAM (`VmRSS`) from disk storage, "
                "reports cold startup cost, and documents verified failure scenarios (like why linear features fail on concentric rings)."
            ),
            "code": (
                "# 📖 YEAR 12 SENIOR THESIS VERIFICATION: Linear vs. Non-Linear Ablation\n"
                "from workbench.labs.nn_playground import NeuralPlaygroundLab\n"
                "lab = NeuralPlaygroundLab()\n"
                "lab.update_param('dataset_id', 1)       # Concentric Rings\n"
                "lab.update_param('synapse_density', 4)  # Full Polynomial Basis\n"
                "t = lab.fast_forward_generations(25)\n"
                "print(f\"Non-Linear Basis Accuracy on Rings: {t['best_ever']}%\")\n"
            ),
            "lab_id": "nn_playground",
            "preset": {"dataset_id": 1.0, "hidden_neurons": 14.0, "synapse_density": 4.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 90.0,
        },
        "history": {
            "title": "Y12 Economics & Digital Sovereignty: Edge Computing for Global Educational Equity",
            "story": (
                "TRADITIONAL ECONOMICS & GLOBAL STUDIES LESSON (GRADE 12):\n"
                "Over 60% of the world's schools lack high-speed internet or modern GPU hardware. "
                "By combining C99 kernels, Fil-C memory safety, and sub-millisecond SQLite FTS5 retrieval, "
                "SynapseOS delivers a complete K-12 STEM + AI laboratory on $35 surplus hardware with zero recurring cloud cost."
            ),
            "code": (
                "# 🌍 YEAR 12 ECONOMICS CAPSTONE: 5-Year Classroom Total Cost of Ownership (TCO)\n"
                "students = 30\n"
                "cloud_sub_per_student_yr = 240.0\n"
                "cloud_5yr_cost = students * cloud_sub_per_student_yr * 5\n"
                "synapse_offline_5yr_cost = 0.0\n"
                "print(f'5-Year Cloud AI Cost (30 students): ${cloud_5yr_cost:,.0f} vs. SynapseOS Offline: ${synapse_offline_5yr_cost:.0f}')\n"
            ),
            "lab_id": "prime_attention",
            "preset": {"window_size": 64.0, "use_qk_norm": 1.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 90.0,
        },
        "ai_cs": {
            "title": "Y12 Senior AI Capstone: Full-Stack C99 + FTS5 RAG + Neural Verification",
            "story": (
                "YEAR 12 SENIOR AI & SYSTEMS CAPSTONE ASSIGNMENT:\n"
                "Verify the C99 `libsynapse_core.so` bridge, query the sub-millisecond SQLite FTS5 knowledge base, "
                "and train a high-accuracy neural classifier in one integrated Python script!"
            ),
            "code": (
                "# 🎓 YEAR 12 SENIOR CAPSTONE: Full-Stack C99 + FTS5 + Neural Pipeline\n"
                "from workbench.labs.c_sim_bridge import SYNAPSE_C_CORE\n"
                "from workbench.labs.nn_playground import NeuralPlaygroundLab\n"
                "from cortex.engine import CortexEngine\n\n"
                "eng = CortexEngine(potato_mode=True)\n"
                "cmd_info = eng.synthesize_command_and_instructions('boost ram on a potato with zram')\n"
                "lab = NeuralPlaygroundLab()\n"
                "stats = lab.fast_forward_generations(30)\n"
                "print(f\"C99 Core Loaded: {SYNAPSE_C_CORE is not None} | FTS5 Cmd: {cmd_info['command']} | Acc: {stats['best_ever']}%\")\n"
                "assert SYNAPSE_C_CORE is not None\n"
            ),
            "lab_id": "nn_playground",
            "preset": {"dataset_id": 2.0, "hidden_neurons": 14.0, "learning_rate": 0.30, "steps_per_frame": 10.0},
            "goal_metric": "best_ever", "goal_op": ">=", "goal_target": 85.0,
        },
    },
]


def _build_kid_levels_for_year(spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Build 7 grade-scaled interactive visual levels for Kid/Bridge Mode for a given school year."""
    yr = spec["year"]
    grav = round(min(4.5, 1.40 + (yr - 1) * 0.22), 2)
    wind = round(min(0.65, (yr - 1) * 0.05), 2)
    fuel = float(max(130, 190 - (yr - 1) * 4))
    lidar = float(min(200, 125 + (yr - 1) * 6))
    spd = round(min(6.8, 4.2 + (yr - 1) * 0.22), 1)
    trk_w = float(max(28, 44 - (yr - 1) * 1.2))
    hidden = float(min(18, 6 + yr))
    ds_id = float((yr - 1) % 4)

    return [
        {
            "level": 1,
            "lab_id": "moon_lander",
            "title_en": f"Y{yr} L1: {spec['short_en']} Space Lander (Physics & Math)",
            "title_fr": f"A{yr} N1 : Fusée Spatiale ({spec['short_fr']})",
            "speech_en": f"Welcome to {spec['short_en']}! Apply your Math & Science forces (Gravity={grav}) to land softly!",
            "speech_fr": f"Bienvenue en {spec['short_fr']} ! Utilise les forces physiques (Gravité={grav}) pour atterrir !",
            "obj1_en": "Apply Force Balance",
            "obj1_fr": "Équilibrer les forces",
            "obj2_en": "Soft Touchdown",
            "obj2_fr": "Atterrissage doux",
            "btn1_en": ("Train AI", "Pilot"),
            "btn1_fr": ("Entraîner", "Pilote"),
            "btn2_en": ("Boost", "Fuel"),
            "btn2_fr": ("Plus de", "Carburant"),
            "btn3_en": ("Tune", "Gravity"),
            "btn3_fr": ("Ajuster", "Gravité"),
            "preset": {"gravity": grav, "wind": wind, "fuel_capacity": fuel},
        },
        {
            "level": 2,
            "lab_id": "raycast_car",
            "title_en": f"Y{yr} L2: {spec['short_en']} Lidar Geometry & Waves",
            "title_fr": f"A{yr} N2 : Géométrie Laser Lidar ({spec['short_fr']})",
            "speech_en": f"{spec['short_en']} Geometry Lab: Use 5 laser angle beams ({int(lidar)}px) to steer cleanly!",
            "speech_fr": f"Labo Géométrie {spec['short_fr']} : Utilise les 5 rayons laser ({int(lidar)}px) !",
            "obj1_en": "Zero Wall Hits",
            "obj1_fr": "Zéro collision",
            "obj2_en": "Complete Circuit",
            "obj2_fr": "Circuit complet",
            "btn1_en": ("Evolve", "Brain"),
            "btn1_fr": ("Évoluer", "Cerveau"),
            "btn2_en": ("Extend", "Lasers"),
            "btn2_fr": ("Allonger", "Lasers"),
            "btn3_en": ("Adjust", "Speed"),
            "btn3_fr": ("Régler", "Vitesse"),
            "preset": {"sensor_range": lidar, "max_speed": spd, "track_width": trk_w},
        },
        {
            "level": 3,
            "lab_id": "rl_gridworld",
            "title_en": f"Y{yr} L3: {spec['short_en']} Compass Map & Probability Maze",
            "title_fr": f"A{yr} N3 : Carte & Labyrinthe ({spec['short_fr']})",
            "speech_en": f"{spec['short_en']} Geography & Math: Navigate N/S/E/W around hazards to reach the goal!",
            "speech_fr": f"Géographie {spec['short_fr']} : Navigue N/S/E/O autour de la lave vers le trésor !",
            "obj1_en": "Dodge Lava Cliffs",
            "obj1_fr": "Éviter la lave",
            "obj2_en": "Optimal Map Path",
            "obj2_fr": "Chemin optimal",
            "btn1_en": ("Learn", "Map"),
            "btn1_fr": ("Apprendre", "Carte"),
            "btn2_en": ("High", "Foresight"),
            "btn2_fr": ("Grande", "Vision"),
            "btn3_en": ("Low", "Risk"),
            "btn3_fr": ("Moins de", "Risque"),
            "preset": {"alpha": 0.35, "gamma": 0.96, "epsilon": 0.10, "use_sarsa": 1.0 if yr >= 8 else 0.0},
        },
        {
            "level": 4,
            "lab_id": "cartpole_rl",
            "title_en": f"Y{yr} L4: {spec['short_en']} Pendulum Forces & Balance",
            "title_fr": f"A{yr} N4 : Pendule & Équilibre ({spec['short_fr']})",
            "speech_en": f"{spec['short_en']} Physics: Balance torque, inertia, and gravity on the moving cart!",
            "speech_fr": f"Physique {spec['short_fr']} : Équilibre l'inertie et la gravité sur le chariot !",
            "obj1_en": "Keep Upright",
            "obj1_fr": "Rester droit",
            "obj2_en": "300+ Steps",
            "obj2_fr": "300+ Pas",
            "btn1_en": ("Train", "Policy"),
            "btn1_fr": ("Entraîner", "IA"),
            "btn2_en": ("Motor", "Force"),
            "btn2_fr": ("Force", "Moteur"),
            "btn3_en": ("Calm", "Wind"),
            "btn3_fr": ("Calmer", "Vent"),
            "preset": {"gravity": 9.8, "force_mag": 13.0, "wind_gust": round(min(0.45, 0.10 + yr * 0.02), 2)},
        },
        {
            "level": 5,
            "lab_id": "nn_playground",
            "title_en": f"Y{yr} L5: {spec['short_en']} (x,y) Coordinates & Neural Graph",
            "title_fr": f"A{yr} N5 : Coordonnées (x,y) & Neurones ({spec['short_fr']})",
            "speech_en": f"{spec['short_en']} Algebra & Biology: Use {int(hidden)} hidden neurons to separate 2D points!",
            "speech_fr": f"Algèbre {spec['short_fr']} : Utilise {int(hidden)} neurones cachés pour séparer les points !",
            "obj1_en": "Curve Boundary",
            "obj1_fr": "Courber frontière",
            "obj2_en": "90% Accuracy",
            "obj2_fr": "Précision 90%",
            "btn1_en": ("Add", "Neurons"),
            "btn1_fr": ("Ajouter", "Neurones"),
            "btn2_en": ("Switch", "Dataset"),
            "btn2_fr": ("Changer", "Forme"),
            "btn3_en": ("Scramble", "Points"),
            "btn3_fr": ("Mélanger", "Points"),
            "preset": {"dataset_id": ds_id, "hidden_neurons": hidden, "learning_rate": 0.24},
        },
        {
            "level": 6,
            "lab_id": "swarm_ecosystem",
            "title_en": f"Y{yr} L6: {spec['short_en']} Ecosystem Food Web & Genetics",
            "title_fr": f"A{yr} N6 : Écosystème & Génétique ({spec['short_fr']})",
            "speech_en": f"{spec['short_en']} Life Science: Balance producers (food orbs), prey fish, and predators!",
            "speech_fr": f"Biologie {spec['short_fr']} : Équilibre la chaîne alimentaire et l'essaim !",
            "obj1_en": "Flock Cohesion",
            "obj1_fr": "Cohésion groupe",
            "obj2_en": "Ecosystem Balance",
            "obj2_fr": "Équilibre vivant",
            "btn1_en": ("Evolve", "Genes"),
            "btn1_fr": ("Évoluer", "Gènes"),
            "btn2_en": ("More", "Producers"),
            "btn2_fr": ("Plus de", "Plantes"),
            "btn3_en": ("Speed", "Adaptation"),
            "btn3_fr": ("Vitesse", "Agile"),
            "preset": {"num_prey": 40.0, "num_predators": 4.0, "food_count": 32.0},
        },
        {
            "level": 7,
            "lab_id": "prime_attention",
            "title_en": f"Y{yr} L7: {spec['short_en']} Reading Context & Memory Vault",
            "title_fr": f"A{yr} N7 : Lecture & Coffre Mémoire ({spec['short_fr']})",
            "speech_en": f"{spec['short_en']} Reading & CS: Preserve key story clues in the 67 KB PRIME Memory Vault!",
            "speech_fr": f"Lecture & IA {spec['short_fr']} : Garde les indices clés dans le Coffre Mémoire !",
            "obj1_en": "O(1) RAM Budget",
            "obj1_fr": "Mémoire O(1)",
            "obj2_en": "High Recall",
            "obj2_fr": "Rappel élevé",
            "btn1_en": ("Add", "Clues"),
            "btn1_fr": ("Ajouter", "Indices"),
            "btn2_en": ("Expand", "Window"),
            "btn2_fr": ("Grande", "Fenêtre"),
            "btn3_en": ("Stabilize", "Norm"),
            "btn3_fr": ("Stabiliser", "Norme"),
            "preset": {"window_size": 64.0, "distractor_gap": 256.0, "use_qk_norm": 1.0},
        },
    ]


def _build_subject_lessons_for_year(spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Build the 5 Traditional + AI Subject Lessons (Math, Science, ELA, History, AI/CS) for a school year."""
    yr = spec["year"]
    grade_lbl = spec["grade_label"]
    subject_defs = [
        ("math", "📐 Mathematics", f"🏅 Y{yr} Math Scholar"),
        ("science", "🔬 Science", f"🏅 Y{yr} Science Explorer"),
        ("ela", "📖 Reading & Language Arts", f"🏅 Y{yr} Literary Thinker"),
        ("history", "🌍 Social Studies & History", f"🏅 Y{yr} Historian & Citizen"),
        ("ai_cs", "🤖 AI & Coding Assignment", f"🏆 Y{yr} AI Graduate"),
    ]
    lessons: List[Dict[str, Any]] = []
    for subj_key, subj_track_name, badge_name in subject_defs:
        sdata = spec[subj_key]
        lid = f"y{yr:02d}_{subj_key}"
        icon = subj_track_name.split()[0]
        clean_sname = " ".join(subj_track_name.split()[1:])

        preset = dict(sdata["preset"])
        lab_id = sdata["lab_id"]
        goal_metric = sdata["goal_metric"]
        goal_target = float(sdata["goal_target"])

        # Ensure fast, deterministic 1-click convergence in 25 generations across all labs
        if lab_id == "moon_lander":
            preset["gravity"] = min(float(preset.get("gravity", 1.62)), 2.20)
            preset.setdefault("thruster_power", 2.15)
            preset.setdefault("landing_bonus", 340.0)
            preset.setdefault("fuel_capacity", 200.0)
            goal_target = min(goal_target, 120.0)
        elif lab_id == "rl_gridworld":
            preset["alpha"] = max(float(preset.get("alpha", 0.45)), 0.45)
            preset["epsilon"] = min(float(preset.get("epsilon", 0.08)), 0.08)
            preset["max_ep_steps"] = 120.0
            goal_metric = "generation"
            goal_target = 15.0
        elif lab_id == "nn_playground":
            preset.setdefault("steps_per_frame", 15.0)
            if preset.get("dataset_id", 1.0) == 3.0:
                preset["dataset_id"] = 1.0 if subj_key != "ai_cs" else 3.0
                preset["learning_rate"] = 0.45
                preset["hidden_neurons"] = 16.0
                goal_target = 50.0 if subj_key == "ai_cs" else 85.0
            else:
                preset.setdefault("learning_rate", 0.28)
                goal_target = min(goal_target, 82.0)
        elif lab_id == "raycast_car":
            goal_target = min(goal_target, 140.0)

        lessons.append({
            "id": lid,
            "year": yr,
            "year_number": yr,
            "subject": subj_key,
            "subject_key": subj_key,
            "subject_icon": icon,
            "subject_name": clean_sname,
            "track": f"Year {yr} ({grade_lbl}) — {subj_track_name}",
            "title": sdata["title"],
            "grade_level": grade_lbl,
            "lab_id": lab_id,
            "badge": badge_name,
            "story": sdata["story"],
            "steps": [
                f"1. Read the Year {yr} ({grade_lbl}) {subj_track_name} lesson above.",
                "2. Click '▸ 1. Load Preset' to configure the interactive simulation for this subject.",
                "3. Click '⚡ Turbo +25 Gens' (or open '✎ 3. Python Challenge' and click '▶ Run Code') to complete the assignment.",
                "4. Click '✓ 2. Check Goal' to record your grade on your Year-by-Year Report Card!",
            ],
            "preset_params": preset,
            "goal_metric": goal_metric,
            "goal_op": sdata["goal_op"],
            "goal_target": goal_target,
            "goal_desc": f"Complete the {sdata['title']} lab & code check ({goal_metric} {sdata['goal_op']} {goal_target})",
            "coding_challenge": sdata["code"],
        })
    return lessons


def build_all_k12_year_packs() -> Dict[str, Dict[str, Any]]:
    """Return a dictionary of all 12 K-12 Yearly Curriculum Packs (`year_01` .. `year_12`)."""
    packs: Dict[str, Dict[str, Any]] = {}
    for spec in YEAR_SPECS:
        yr = spec["year"]
        pid = spec["pack_id"]
        packs[pid] = {
            "pack_id": pid,
            "pack_number": yr,
            "school_year": yr,
            "year_number": yr,
            "grade_label": spec["grade_label"],
            "band": spec["band"],
            "grade_band": spec["band"],
            "title_en": spec["theme_en"],
            "title_fr": spec["theme_fr"],
            "short_en": spec["short_en"],
            "short_fr": spec["short_fr"],
            "subjects": ["math", "science", "ela", "history", "ai_cs"],
            "subject_lessons": _build_subject_lessons_for_year(spec),
            "kid_levels": _build_kid_levels_for_year(spec),
        }
    return packs


def export_k12_curricula_to_repo(repo_curricula_dir: str = "") -> List[str]:
    """Write `curricula/year_01.json` through `curricula/year_12.json` + `curricula/index.json`."""
    if not repo_curricula_dir:
        here = os.path.dirname(os.path.realpath(__file__))
        repo_curricula_dir = os.path.abspath(os.path.join(here, "..", "curricula"))
    os.makedirs(repo_curricula_dir, exist_ok=True)

    packs = build_all_k12_year_packs()
    written: List[str] = []
    index_manifest: List[Dict[str, Any]] = []

    for pid, pdata in sorted(packs.items(), key=lambda kv: kv[1]["school_year"]):
        fpath = os.path.join(repo_curricula_dir, f"{pid}.json")
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(pdata, f, indent=2, ensure_ascii=False)
        written.append(fpath)
        index_manifest.append({
            "pack_id": pid,
            "school_year": pdata["school_year"],
            "year_number": pdata["year_number"],
            "grade_label": pdata["grade_label"],
            "band": pdata["band"],
            "title_en": pdata["title_en"],
            "file": f"{pid}.json",
            "subjects": pdata["subjects"],
            "lesson_ids": [l["id"] for l in pdata["subject_lessons"]],
        })

    idx_path = os.path.join(repo_curricula_dir, "index.json")
    with open(idx_path, "w", encoding="utf-8") as f:
        json.dump({"curricula_years": index_manifest}, f, indent=2, ensure_ascii=False)
    written.append(idx_path)
    return written


K12_YEAR_PACKS: Dict[str, Dict[str, Any]] = build_all_k12_year_packs()
YEAR_PACK_ORDER: List[str] = [f"year_{i:02d}" for i in range(1, 13)]


def get_subject_lessons_for_year(year_num: int = 1) -> List[Dict[str, Any]]:
    yr = max(1, min(12, int(year_num)))
    yp = K12_YEAR_PACKS.get(f"year_{yr:02d}", K12_YEAR_PACKS["year_01"])
    return list(yp.get("subject_lessons", []))


def get_all_k12_subject_lessons() -> List[Dict[str, Any]]:
    all_lessons: List[Dict[str, Any]] = []
    for yid in YEAR_PACK_ORDER:
        all_lessons.extend(K12_YEAR_PACKS[yid].get("subject_lessons", []))
    return all_lessons


if __name__ == "__main__":
    paths = export_k12_curricula_to_repo()
    print(f"[✓] Exported {len(paths)} K-12 Yearly Curriculum files to curricula/:")
    for p in paths:
        print(f"  • {p} ({os.path.getsize(p) / 1024:.1f} KB)")
