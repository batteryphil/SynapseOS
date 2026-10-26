#!/usr/bin/env python3
"""
Synapse Kids — Full-Screen Gamified AI Arcade View for Classrooms & Young Learners
Matches the "Synapse Kids" design:
  - Top bar: [🚀 Synapse Kids]  [⭐ Level 1: Space Moon Landing]  [⚙ Teacher Mode] [🇫🇷/🇬🇧] [Badges 🏆]
  - Left: Large SIMULATION viewport with cute cartoon rocket, 3D moon craters & starry sky
  - Right Top: Animated cute Robot Mascot + Speech Bubble (powered by Cortex-Phi3)
  - Right Bottom: 🎯 Objective card with live checkboxes ([ ] Don't explode, [✓] Soft landing +100 pts)
  - Bottom Deck: 🕹️ Simple Controls + Score: ⭐⭐⭐ (3/3) + 4 chunky icon pill buttons:
      1. 🧠 Make Smarter (Rendre plus intelligent)
      2. ⛽ More Fuel (Plus de carburant)
      3. 🌙 Light Gravity (Gravité Légère)
      4. ▶ Run Test! (Relancer le test)
"""

import math
import time
import threading
from typing import Dict, Any, List, Tuple, Optional, Callable

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib
import cairo

from workbench.pack_manager import (
    PLAYER_AVATARS,
    TROPHY_SHOP_ITEMS,
    ALL_TROPHY_PEDESTALS,
    WORLD_MAP_ZONES,
)


LEVEL_DATA: List[Dict[str, Any]] = [
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
    },
    {
        "level": 2,
        "lab_id": "raycast_car",
        "title_en": "Level 2: Cyber Self-Driving Car",
        "title_fr": "Niveau 2 : Voiture autonome laser",
        "speech_en": "Hi! Help the racecar steer around corners by making its brain smarter or boosting laser range!",
        "speech_fr": "Salut ! Aide la voiture à tourner sans toucher les murs avec un cerveau plus intelligent !",
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
    },
]


class SynapseKidsView(Gtk.DrawingArea):
    """Full-screen Cairo interactive view matching the Synapse Kids mockup."""

    def __init__(
        self,
        studio_win: Any,
        on_switch_to_teacher: Callable[[], None],
    ) -> None:
        super().__init__()
        self.studio = studio_win
        self.on_switch_to_teacher = on_switch_to_teacher

        # Default to English ("en"), with instant 1-click FR/EN toggle in top right
        self.lang: str = "en"
        self.level_idx: int = 0
        self.hovered_id: Optional[str] = None
        self.hitboxes: Dict[str, Tuple[float, float, float, float]] = {}

        # Viewport Mode: "sim" (Live AI Lab), "map" (2D World Map), "trophies" (Trophy Room & Coin Shop), "pin" (Teacher PIN Gate)
        self.view_mode: str = "sim"
        self.pin_buffer: str = ""

        # Lumi Virtual Pet reactive emotional state: "happy", "cheering", "thinking", "dizzy", "sleepy"
        self.pet_mood: str = "happy"
        self.pet_mood_timer: int = 0
        self.last_interaction_ts: float = time.monotonic()
        self._tick_counter: int = 0

        # Gamified kid state for Level 1 Moon Lander hero simulation
        self.smart_boost: int = 1
        self.fuel_boost: bool = True
        self.light_grav: bool = True

        self.rocket_x: float = 0.31
        self.rocket_y: float = 0.15
        self.rocket_vx: float = 0.0025
        self.rocket_vy: float = 0.0048
        self.rocket_angle: float = -0.14
        self.rocket_fuel: float = 100.0
        self.rocket_thrusting: bool = False
        self.rocket_state: str = "flying"  # "flying", "landed", "crashed"
        self.landed_timer: int = 0

        self.obj1_done: bool = True
        self.obj2_done: bool = True
        self.stars_score: int = 3
        self.custom_speech: Optional[str] = None
        self.asking_ai: bool = False

        self.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.LEAVE_NOTIFY_MASK
        )
        self.connect("draw", self._on_draw)
        self.connect("button-press-event", self._on_button_press)
        self.connect("motion-notify-event", self._on_motion)

    @property
    def cur_level(self) -> Dict[str, Any]:
        return LEVEL_DATA[self.level_idx % len(LEVEL_DATA)]

    def set_pet_mood(self, mood: str, duration_ticks: int = 130) -> None:
        """Set Lumi's Virtual Pet emotional state (cheering, thinking, dizzy, happy, sleepy)."""
        self.pet_mood = mood
        self.pet_mood_timer = duration_ticks
        self.last_interaction_ts = time.monotonic()

    def reset_rocket_test(self) -> None:
        """Launch a fresh test run of the hero Moon Lander rocket from high in space."""
        self.rocket_x = 0.31
        self.rocket_y = 0.15
        self.rocket_vx = 0.0025
        self.rocket_vy = 0.0048
        self.rocket_angle = -0.14
        self.rocket_fuel = 100.0 if self.fuel_boost else 38.0
        self.rocket_state = "flying"
        self.rocket_thrusting = False
        self.landed_timer = 0

    def step_kid_simulation(self) -> None:
        """Step the playful hero rocket physics, Lumi Virtual Pet mood timer, and lab engagement counter."""
        self._tick_counter += 1
        # Track time spent in active lab once every ~55 ticks (1 second) for the Teacher/Parent Dashboard
        if self._tick_counter % 55 == 0 and hasattr(self.studio, "pack_mgr"):
            self.studio.pack_mgr.record_lab_activity(self.cur_level["lab_id"], seconds_delta=1)

        if self.pet_mood_timer > 0:
            self.pet_mood_timer -= 1
            if self.pet_mood_timer == 0 and not self.asking_ai:
                self.pet_mood = "happy"
        elif not self.asking_ai and (time.monotonic() - self.last_interaction_ts) > 25.0:
            self.pet_mood = "sleepy"

        if self.cur_level["lab_id"] != "moon_lander":
            return

        if self.rocket_state != "flying":
            self.landed_timer += 1
            # After 2.8 seconds parked on the Moon (or crashed), launch a fresh test flight
            if self.landed_timer > 155:
                self.reset_rocket_test()
            return

        grav = 0.00018 if self.light_grav else 0.00042
        thrust_acc = 0.00046 if self.fuel_boost else 0.00020

        # Free-fall in upper space (y < 0.32), then AI fires retro-thrusters in braking zone (y >= 0.32)
        target_vy = 0.0026 if self.smart_boost >= 1 else 0.0075
        in_braking_zone = self.rocket_y >= 0.32
        need_brake = in_braking_zone and (self.rocket_vy > target_vy or self.rocket_y > 0.48)

        if need_brake and self.rocket_fuel > 0.0:
            self.rocket_thrusting = True
            self.rocket_vy = max(0.0018, self.rocket_vy - thrust_acc)
            self.rocket_fuel = max(0.0, self.rocket_fuel - (0.65 if self.fuel_boost else 1.65))
            self.rocket_angle *= 0.88
            self.rocket_vx *= 0.92
        else:
            self.rocket_thrusting = False
            self.rocket_vy += grav
            self.rocket_angle = min(0.22, self.rocket_angle + 0.004)

        # Gentle horizontal steering toward the landing pad at x = 0.31
        self.rocket_x += (0.31 - self.rocket_x) * 0.06 + math.sin(self.rocket_y * 12.0) * 0.0015
        self.rocket_y += self.rocket_vy

        # Touchdown when footpads reach the lunar landing pad at rocket_y = 0.615
        if self.rocket_y >= 0.615:
            self.rocket_y = 0.615
            self.rocket_thrusting = False  # Shut off engines on touchdown so it sits on the Moon!
            if self.rocket_vy <= 0.0052 and (self.fuel_boost or self.light_grav or self.smart_boost >= 1):
                self.rocket_state = "landed"
                self.rocket_vy = 0.0
                self.rocket_vx = 0.0
                self.rocket_angle = 0.0
                self.obj1_done = True
                self.obj2_done = True
                self.stars_score = 3
                self.set_pet_mood("cheering", 140)
                if hasattr(self.studio, "award_kid_level_trophy"):
                    self.studio.award_kid_level_trophy(self.cur_level.get("level", 1))
                else:
                    self.studio.earned_badges.add("m1_moon_gravity")
                    self.studio._update_badge_header()
            else:
                self.rocket_state = "crashed"
                self.rocket_vy = 0.0
                self.rocket_vx = 0.0
                self.rocket_angle = 0.42
                self.obj1_done = False
                self.obj2_done = False
                self.stars_score = 1
                self.set_pet_mood("dizzy", 140)

    # ==========================================================================
    # CAIRO GEOMETRY & VECTOR ICON HELPERS
    # ==========================================================================
    @staticmethod
    def _rounded_rect(cr: cairo.Context, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        cr.new_sub_path()
        cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
        cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
        cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
        cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
        cr.close_path()

    def _draw_pill(
        self,
        cr: cairo.Context,
        x: float,
        y: float,
        w: float,
        h: float,
        c1: Tuple[float, float, float],
        c2: Tuple[float, float, float],
        border_c: Tuple[float, float, float],
        radius: Optional[float] = None,
        hover: bool = False,
        glow: bool = False,
    ) -> None:
        r = radius if radius is not None else h * 0.46
        # Drop shadow
        self._rounded_rect(cr, x + 1, y + 3, w, h, r)
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.42)
        cr.fill()

        # Main vertical gradient
        pat = cairo.LinearGradient(x, y, x, y + h)
        boost = 0.07 if hover else 0.0
        pat.add_color_stop_rgb(0.0, min(1.0, c1[0] + boost), min(1.0, c1[1] + boost), min(1.0, c1[2] + boost))
        pat.add_color_stop_rgb(1.0, min(1.0, c2[0] + boost), min(1.0, c2[1] + boost), min(1.0, c2[2] + boost))
        self._rounded_rect(cr, x, y, w, h, r)
        cr.set_source(pat)
        cr.fill_preserve()

        # Border
        cr.set_source_rgba(border_c[0], border_c[1], border_c[2], 0.95 if (hover or glow) else 0.75)
        cr.set_line_width(2.4 if (hover or glow) else 1.8)
        cr.stroke()

        # Subtle top glossy highlight
        self._rounded_rect(cr, x + 3, y + 2, w - 6, h * 0.42, r * 0.8)
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.11 if hover else 0.07)
        cr.fill()

    @staticmethod
    def _draw_star(
        cr: cairo.Context,
        cx: float,
        cy: float,
        outer_r: float,
        inner_r: float,
        filled: bool = True,
    ) -> None:
        cr.new_path()
        for i in range(10):
            ang = -math.pi / 2 + i * (math.pi / 5)
            rad = outer_r if i % 2 == 0 else inner_r
            px = cx + math.cos(ang) * rad
            py = cy + math.sin(ang) * rad
            if i == 0:
                cr.move_to(px, py)
            else:
                cr.line_to(px, py)
        cr.close_path()
        if filled:
            cr.set_source_rgb(0.99, 0.80, 0.15)
            cr.fill_preserve()
            cr.set_source_rgb(0.75, 0.48, 0.05)
            cr.set_line_width(1.3)
            cr.stroke()
        else:
            cr.set_source_rgba(0.30, 0.38, 0.52, 0.7)
            cr.fill_preserve()
            cr.set_source_rgba(0.45, 0.55, 0.70, 0.8)
            cr.set_line_width(1.2)
            cr.stroke()

    @staticmethod
    def _draw_cute_rocket(
        cr: cairo.Context,
        cx: float,
        cy: float,
        scale: float = 1.0,
        angle: float = 0.0,
        thrusting: bool = True,
        anim_phase: float = 0.0,
    ) -> None:
        """Draws the exact white/red/blue cartoon rocket with flickering flame from the screenshot."""
        cr.save()
        cr.translate(cx, cy)
        cr.rotate(angle)
        cr.scale(scale, scale)

        # 1. Flickering exhaust flame underneath
        if thrusting:
            flick = 1.0 + 0.18 * math.sin(anim_phase * 3.2)
            # Outer orange flame
            cr.set_source_rgba(0.98, 0.45, 0.10, 0.95)
            cr.move_to(-10, 22)
            cr.curve_to(-13, 34 * flick, -4, 44 * flick, 0, 48 * flick)
            cr.curve_to(4, 44 * flick, 13, 34 * flick, 10, 22)
            cr.close_path()
            cr.fill()

            # Inner yellow/white flame
            cr.set_source_rgba(0.99, 0.88, 0.22, 0.98)
            cr.move_to(-6, 22)
            cr.curve_to(-7, 30 * flick, -2, 37 * flick, 0, 40 * flick)
            cr.curve_to(2, 37 * flick, 7, 30 * flick, 6, 22)
            cr.close_path()
            cr.fill()

        # 2. Left & Right Red Side Fins
        cr.set_source_rgb(0.92, 0.22, 0.18)
        # Left fin
        cr.move_to(-13, 4)
        cr.curve_to(-25, 10, -26, 22, -22, 28)
        cr.curve_to(-17, 24, -14, 18, -10, 18)
        cr.close_path()
        cr.fill_preserve()
        cr.set_source_rgb(0.12, 0.16, 0.24)
        cr.set_line_width(1.6)
        cr.stroke()

        # Right fin
        cr.set_source_rgb(0.92, 0.22, 0.18)
        cr.move_to(13, 4)
        cr.curve_to(25, 10, 26, 22, 22, 28)
        cr.curve_to(17, 24, 14, 18, 10, 18)
        cr.close_path()
        cr.fill_preserve()
        cr.set_source_rgb(0.12, 0.16, 0.24)
        cr.set_line_width(1.6)
        cr.stroke()

        # 3. Dark nozzle base
        cr.set_source_rgb(0.25, 0.30, 0.38)
        cr.rectangle(-9, 17, 18, 6)
        cr.fill()

        # 4. Main White Fuselage Body (egg-capsule curve)
        cr.move_to(0, -34)
        cr.curve_to(16, -20, 18, 4, 12, 18)
        cr.line_to(-12, 18)
        cr.curve_to(-18, 4, -16, -20, 0, -34)
        cr.close_path()
        cr.set_source_rgb(0.96, 0.98, 1.0)
        cr.fill_preserve()
        cr.set_source_rgb(0.12, 0.16, 0.24)
        cr.set_line_width(2.0)
        cr.stroke()

        # Subtle right-side 3D shading on fuselage
        cr.move_to(0, -33)
        cr.curve_to(15, -19, 17, 4, 11, 17)
        cr.line_to(3, 17)
        cr.curve_to(7, 2, 6, -16, 0, -33)
        cr.close_path()
        cr.set_source_rgba(0.75, 0.82, 0.92, 0.55)
        cr.fill()

        # 5. Red Nose Cone at top
        cr.move_to(0, -34)
        cr.curve_to(9, -26, 13, -17, 14, -12)
        cr.curve_to(5, -10, -5, -10, -14, -12)
        cr.curve_to(-13, -17, -9, -26, 0, -34)
        cr.close_path()
        cr.set_source_rgb(0.92, 0.22, 0.18)
        cr.fill_preserve()
        cr.set_source_rgb(0.12, 0.16, 0.24)
        cr.set_line_width(1.6)
        cr.stroke()

        # 6. Center Red Fin strip
        cr.set_source_rgb(0.92, 0.22, 0.18)
        cr.move_to(0, 6)
        cr.line_to(-3, 21)
        cr.line_to(3, 21)
        cr.close_path()
        cr.fill()

        # 7. Circular Blue Porthole Window
        cr.set_source_rgb(0.20, 0.26, 0.36)
        cr.arc(0, -1, 8.2, 0, 2 * math.pi)
        cr.fill()

        cr.set_source_rgb(0.22, 0.76, 0.98)
        cr.arc(0, -1, 6.2, 0, 2 * math.pi)
        cr.fill()

        # Window glass highlight
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.75)
        cr.arc(-2.2, -3.2, 2.0, 0, 2 * math.pi)
        cr.fill()

        cr.restore()

    def _draw_robot_mascot(
        self,
        cr: cairo.Context,
        cx: float,
        cy: float,
        scale: float,
        anim_phase: float,
    ) -> None:
        """Draws Lumi the Virtual Pet & Socratic AI Companion with reactive emotional expressions & unlockable Crown."""
        mood = "thinking" if self.asking_ai else self.pet_mood
        unlocked: List[str] = []
        if hasattr(self.studio, "pack_mgr"):
            unlocked = list(self.studio.pack_mgr.profile.get("unlocked_decorations", []))

        cr.save()
        if mood == "cheering":
            bob = -abs(math.sin(anim_phase * 3.8)) * 7.5
        elif mood == "sleepy":
            bob = math.sin(anim_phase * 0.45) * 1.5
        else:
            bob = math.sin(anim_phase * 0.9) * 2.5
        cr.translate(cx, cy + bob)
        if mood == "dizzy":
            cr.rotate(math.sin(anim_phase * 4.5) * 0.14)
        cr.scale(scale, scale)

        # Optional Champion Star Aura ("neon_banner" decoration) or "cheering" mood stars
        if mood == "cheering" or "neon_banner" in unlocked:
            for s_i in range(3):
                ang = anim_phase * 2.2 + s_i * (2.0 * math.pi / 3.0)
                sx_o = math.cos(ang) * 42.0
                sy_o = -8.0 + math.sin(ang) * 28.0
                self._draw_star(cr, sx_o, sy_o, outer_r=6.0, inner_r=2.8, filled=True)

        # Antenna
        cr.set_source_rgb(0.55, 0.72, 0.90)
        cr.set_line_width(3.0)
        cr.move_to(0, -34)
        cr.line_to(0, -46)
        cr.stroke()
        ant_col = (0.98, 0.78, 0.18) if mood == "cheering" else ((0.98, 0.32, 0.25) if mood == "dizzy" else (0.22, 0.85, 0.98))
        cr.set_source_rgb(*ant_col)
        cr.arc(0, -48, 4.5, 0, 2 * math.pi)
        cr.fill()

        # Thinking sonar rings around antenna
        if mood == "thinking":
            for r_i in range(2):
                rad_s = 7.0 + ((anim_phase * 14.0 + r_i * 9.0) % 18.0)
                alpha_s = max(0.0, 0.85 - rad_s / 24.0)
                cr.set_source_rgba(0.28, 0.92, 1.0, alpha_s)
                cr.set_line_width(1.6)
                cr.arc(0, -48, rad_s, 0, 2 * math.pi)
                cr.stroke()

        # Unlockable Royal Golden Crown ("pet_crown" decoration from Trophy Room Shop!)
        if "pet_crown" in unlocked:
            cr.save()
            cr.move_to(-18, -33)
            cr.line_to(-21, -48)
            cr.line_to(-9, -40)
            cr.line_to(0, -52)
            cr.line_to(9, -40)
            cr.line_to(21, -48)
            cr.line_to(18, -33)
            cr.close_path()
            cr.set_source_rgb(0.99, 0.82, 0.16)
            cr.fill_preserve()
            cr.set_source_rgb(0.78, 0.52, 0.05)
            cr.set_line_width(1.6)
            cr.stroke()
            # Crown ruby gem
            cr.set_source_rgb(0.96, 0.20, 0.32)
            cr.arc(0, -39, 2.6, 0, 2 * math.pi)
            cr.fill()
            cr.restore()

        # Ear pods
        cr.set_source_rgb(0.16, 0.52, 0.88)
        self._rounded_rect(cr, -34, -22, 8, 16, 3)
        cr.fill()
        self._rounded_rect(cr, 26, -22, 8, 16, 3)
        cr.fill()

        # Robot Head (rounded white/light-blue metallic)
        self._rounded_rect(cr, -28, -34, 56, 40, 14)
        cr.set_source_rgb(0.88, 0.94, 1.0)
        cr.fill_preserve()
        cr.set_source_rgb(0.20, 0.45, 0.78)
        cr.set_line_width(2.2)
        cr.stroke()

        # Dark Visor Face Screen
        self._rounded_rect(cr, -21, -27, 42, 26, 9)
        cr.set_source_rgb(0.06, 0.12, 0.24)
        cr.fill()

        # Reactive Virtual Pet Eyes & Mouth
        if mood == "cheering":
            # Happy ^ ^ chevron eyes + big open smile
            cr.set_source_rgb(0.35, 0.98, 0.65)
            cr.set_line_width(2.6)
            for ex_c in (-9.0, 9.0):
                cr.move_to(ex_c - 4.5, -13)
                cr.line_to(ex_c, -18.5)
                cr.line_to(ex_c + 4.5, -13)
                cr.stroke()
            cr.set_source_rgb(0.99, 0.85, 0.28)
            cr.arc(0, -10, 6.8, 0.10 * math.pi, 0.90 * math.pi)
            cr.fill()
        elif mood == "dizzy":
            # X / Oops eyes + wavy mouth
            cr.set_source_rgb(0.99, 0.45, 0.22)
            cr.set_line_width(2.4)
            for ex_c in (-9.0, 9.0):
                cr.move_to(ex_c - 3.8, -18.5)
                cr.line_to(ex_c + 3.8, -11.5)
                cr.stroke()
                cr.move_to(ex_c + 3.8, -18.5)
                cr.line_to(ex_c - 3.8, -11.5)
                cr.stroke()
            cr.arc(0, -6.5, 4.5, 1.15 * math.pi, 1.85 * math.pi)
            cr.stroke()
        elif mood == "sleepy":
            # Closed sleepy U-eyes + floating Zzz
            cr.set_source_rgb(0.55, 0.82, 0.98)
            cr.set_line_width(2.2)
            for ex_c in (-9.0, 9.0):
                cr.arc(ex_c, -15, 4.0, 0.1 * math.pi, 0.9 * math.pi)
                cr.stroke()
            cr.arc(0, -8, 2.5, 0, 2 * math.pi)
            cr.stroke()
            cr.select_font_face("Sans", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(10.0)
            cr.set_source_rgba(0.75, 0.92, 1.0, 0.88)
            cr.move_to(24, -34 - (anim_phase * 6.0) % 10.0)
            cr.show_text("Zzz")
        else:
            # Default Happy / Thinking Glowing Cyan Eyes
            cr.set_source_rgb(0.25, 0.88, 1.0)
            cr.arc(-9, -15, 4.2, 0, 2 * math.pi)
            cr.fill()
            cr.arc(9, -15, 4.2, 0, 2 * math.pi)
            cr.fill()
            cr.set_source_rgb(1.0, 1.0, 1.0)
            cr.arc(-10.2, -16.5, 1.4, 0, 2 * math.pi)
            cr.fill()
            cr.arc(7.8, -16.5, 1.4, 0, 2 * math.pi)
            cr.fill()
            cr.set_source_rgb(0.25, 0.88, 1.0)
            cr.set_line_width(2.2)
            cr.arc(0, -10, 6.0, 0.15 * math.pi, 0.85 * math.pi)
            cr.stroke()

        # Robot Torso
        self._rounded_rect(cr, -20, 8, 40, 28, 11)
        cr.set_source_rgb(0.85, 0.92, 1.0)
        cr.fill_preserve()
        cr.set_source_rgb(0.20, 0.45, 0.78)
        cr.set_line_width(2.0)
        cr.stroke()

        # Blue belly plate with pulsing heart/core
        self._rounded_rect(cr, -13, 13, 26, 16, 6)
        cr.set_source_rgb(0.18, 0.56, 0.92)
        cr.fill()

        # Left Arm (cheers up when cheering!)
        cr.set_source_rgb(0.78, 0.88, 0.98)
        cr.set_line_width(6.5)
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.move_to(-22, 14)
        if mood == "cheering":
            cr.line_to(-32, 0)
        else:
            cr.line_to(-30, 25)
        cr.stroke()

        # Right Arm (waving hello!)
        wave = math.sin(anim_phase * (4.0 if mood == "cheering" else 2.2)) * 0.25
        cr.save()
        cr.translate(22, 14)
        cr.rotate(-0.6 + wave)
        cr.move_to(0, 0)
        cr.line_to(14, -8)
        cr.stroke()
        cr.restore()

        # Feet
        cr.set_source_rgb(0.20, 0.35, 0.58)
        self._rounded_rect(cr, -15, 35, 11, 7, 3)
        cr.fill()
        self._rounded_rect(cr, 4, 35, 11, 7, 3)
        cr.fill()

        cr.restore()

    def _draw_avatar_badge(
        self,
        cr: cairo.Context,
        cx: float,
        cy: float,
        r: float,
        avatar_id: str,
    ) -> None:
        """Draws a procedural vector Cadet Avatar face inside a circular medallion."""
        cr.save()
        cr.translate(cx, cy)
        # Medallion background
        colors = {
            "astro_kid": (0.18, 0.58, 0.96),
            "cyber_bot": (0.14, 0.78, 0.68),
            "star_fox": (0.94, 0.52, 0.16),
            "code_wizard": (0.58, 0.32, 0.92),
            "astro_cat": (0.92, 0.36, 0.62),
            "neon_ninja": (0.18, 0.82, 0.42),
        }
        r_c, g_c, b_c = colors.get(avatar_id, (0.18, 0.58, 0.96))
        cr.arc(0, 0, r, 0, 2 * math.pi)
        cr.set_source_rgb(r_c, g_c, b_c)
        cr.fill_preserve()
        cr.set_source_rgb(0.98, 0.88, 0.38)
        cr.set_line_width(2.0)
        cr.stroke()

        # Pointed ears for star_fox / astro_cat / wizard hat for code_wizard
        if avatar_id in ("star_fox", "astro_cat"):
            cr.set_source_rgb(0.98, 0.72, 0.28 if avatar_id == "star_fox" else 0.78)
            for s_e in (-1, 1):
                cr.move_to(s_e * r * 0.25, -r * 0.45)
                cr.line_to(s_e * r * 0.65, -r * 0.85)
                cr.line_to(s_e * r * 0.70, -r * 0.20)
                cr.close_path()
                cr.fill()
        elif avatar_id == "code_wizard":
            cr.set_source_rgb(0.98, 0.82, 0.22)
            cr.move_to(-r * 0.6, -r * 0.35)
            cr.line_to(0, -r * 0.95)
            cr.line_to(r * 0.6, -r * 0.35)
            cr.close_path()
            cr.fill()

        # Visor / Face
        cr.arc(0, r * 0.08, r * 0.58, 0, 2 * math.pi)
        cr.set_source_rgb(0.08, 0.14, 0.26 if avatar_id != "neon_ninja" else 0.10)
        cr.fill()

        # Glowing Eyes
        cr.set_source_rgb(0.35, 0.96, 1.0 if avatar_id != "neon_ninja" else 0.45)
        cr.arc(-r * 0.22, r * 0.04, r * 0.13, 0, 2 * math.pi)
        cr.fill()
        cr.arc(r * 0.22, r * 0.04, r * 0.13, 0, 2 * math.pi)
        cr.fill()

        # Smile (or ninja headband)
        if avatar_id == "neon_ninja":
            cr.set_source_rgb(0.98, 0.28, 0.32)
            cr.set_line_width(2.2)
            cr.move_to(-r * 0.55, -r * 0.18)
            cr.line_to(r * 0.55, -r * 0.18)
            cr.stroke()
        else:
            cr.set_source_rgb(0.95, 0.98, 1.0)
            cr.set_line_width(1.6)
            cr.arc(0, r * 0.16, r * 0.22, 0.15 * math.pi, 0.85 * math.pi)
            cr.stroke()
        cr.restore()

    def _draw_trophy_icon(self, cr: cairo.Context, cx: float, cy: float, s: float) -> None:
        cr.save()
        cr.translate(cx, cy)
        cr.scale(s, s)
        # Handles
        cr.set_source_rgb(0.98, 0.78, 0.15)
        cr.set_line_width(2.2)
        cr.new_path()
        cr.arc(-7, -3, 4.5, math.pi * 0.5, math.pi * 1.5)
        cr.stroke()
        cr.new_path()
        cr.arc(7, -3, 4.5, -math.pi * 0.5, math.pi * 0.5)
        cr.stroke()
        # Cup body
        cr.new_path()
        cr.move_to(-8, -9)
        cr.line_to(8, -9)
        cr.curve_to(8, 2, 4, 5, 0, 5)
        cr.curve_to(-4, 5, -8, 2, -8, -9)
        cr.close_path()
        cr.fill()
        # Stem & Base
        cr.rectangle(-2, 4, 4, 5)
        cr.fill()
        cr.rectangle(-6, 8, 12, 3)
        cr.fill()
        cr.restore()

    def _draw_brain_icon(self, cr: cairo.Context, cx: float, cy: float, s: float) -> None:
        cr.save()
        cr.translate(cx, cy)
        cr.scale(s, s)
        cr.set_source_rgb(0.98, 0.62, 0.72)
        # Left & right hemisphere puffs
        for ox, oy, rad in [
            (-6, -5, 6.5), (-8, 2, 6.0), (-5, 7, 5.5),
            (6, -5, 6.5), (8, 2, 6.0), (5, 7, 5.5),
            (-3, -8, 5.5), (3, -8, 5.5),
        ]:
            cr.new_path()
            cr.arc(ox, oy, rad, 0, 2 * math.pi)
            cr.fill()
        # Sulci lines
        cr.set_source_rgba(0.68, 0.22, 0.38, 0.85)
        cr.set_line_width(1.6)
        cr.new_path()
        cr.move_to(0, -11)
        cr.line_to(0, 11)
        cr.stroke()
        cr.new_path()
        cr.arc(-5, -2, 3.5, 0, math.pi)
        cr.stroke()
        cr.new_path()
        cr.arc(5, 2, 3.5, math.pi, 2 * math.pi)
        cr.stroke()
        cr.restore()

    def _draw_fuel_icon(self, cr: cairo.Context, cx: float, cy: float, s: float) -> None:
        cr.save()
        cr.translate(cx, cy)
        cr.scale(s, s)
        cr.new_path()
        # Pump body
        self._rounded_rect(cr, -9, -11, 15, 22, 2.5)
        cr.set_source_rgb(0.95, 0.26, 0.18)
        cr.fill()
        # Screen window
        self._rounded_rect(cr, -6, -8, 9, 6, 1.5)
        cr.set_source_rgb(0.99, 0.88, 0.35)
        cr.fill()
        # Hose on right
        cr.set_source_rgb(0.99, 0.82, 0.25)
        cr.set_line_width(2.4)
        cr.new_path()
        cr.move_to(6, -4)
        cr.curve_to(12, -4, 12, 8, 8, 8)
        cr.line_to(6, 2)
        cr.stroke()
        cr.restore()

    def _draw_moon_icon(self, cr: cairo.Context, cx: float, cy: float, s: float) -> None:
        cr.save()
        cr.translate(cx, cy)
        cr.scale(s, s)
        cr.new_path()
        cr.set_source_rgb(0.99, 0.82, 0.20)
        cr.arc(0, 0, 10.5, 0.25 * math.pi, 1.75 * math.pi)
        cr.arc_negative(4.5, -2.0, 8.5, 1.65 * math.pi, 0.35 * math.pi)
        cr.close_path()
        cr.fill()
        cr.restore()

    def _draw_target_icon(self, cr: cairo.Context, cx: float, cy: float, r: float) -> None:
        for rad, col in [
            (r, (0.92, 0.22, 0.22)),
            (r * 0.68, (0.98, 0.98, 1.0)),
            (r * 0.38, (0.92, 0.22, 0.22)),
        ]:
            cr.new_path()
            cr.set_source_rgb(*col)
            cr.arc(cx, cy, rad, 0, 2 * math.pi)
            cr.fill()

    @staticmethod
    def _wrap_text(cr: cairo.Context, text: str, max_w: float) -> List[str]:
        words = text.split()
        lines: List[str] = []
        cur = ""
        for w in words:
            test = f"{cur} {w}".strip()
            ext = cr.text_extents(test)
            if ext.width <= max_w or not cur:
                cur = test
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    # ==========================================================================
    # MAIN 60 FPS FULL-SCREEN SYNAPSE KIDS RENDERER
    # ==========================================================================
    def _on_draw(self, widget: Gtk.DrawingArea, cr: cairo.Context) -> bool:
        alloc = widget.get_allocation()
        W, H = float(alloc.width), float(alloc.height)
        self.hitboxes.clear()
        phase = self.studio._anim_phase
        lv = self.cur_level
        is_fr = (self.lang == "fr")

        # 1. Outer Dark Navy Background & Frame
        cr.set_source_rgb(0.03, 0.06, 0.12)
        cr.paint()

        pad_x, pad_y = W * 0.015, H * 0.018
        self._rounded_rect(cr, pad_x, pad_y, W - 2 * pad_x, H - 2 * pad_y, 20)
        pat_bg = cairo.LinearGradient(0, pad_y, 0, H - pad_y)
        pat_bg.add_color_stop_rgb(0.0, 0.06, 0.12, 0.23)
        pat_bg.add_color_stop_rgb(1.0, 0.04, 0.09, 0.18)
        cr.set_source(pat_bg)
        cr.fill_preserve()
        cr.set_source_rgba(0.20, 0.42, 0.72, 0.55)
        cr.set_line_width(2.0)
        cr.stroke()

        # ======================================================================
        # TOP HEADER BAR
        # ======================================================================
        # A1. [🚀 Synapse Kids] Pill (Left)
        bx, by, bw, bh = W * 0.032, H * 0.042, W * 0.138, H * 0.082
        self.hitboxes["synapse_kids_logo"] = (bx, by, bw, bh)
        self._draw_pill(
            cr, bx, by, bw, bh,
            (0.14, 0.48, 0.92), (0.08, 0.30, 0.68), (0.38, 0.75, 0.98),
            hover=(self.hovered_id == "synapse_kids_logo"),
        )
        self._draw_cute_rocket(cr, bx + bw * 0.20, by + bh * 0.52, scale=min(W, H) / 1600.0, angle=0.65, thrusting=True, anim_phase=phase)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(max(12.0, H * 0.022))
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.move_to(bx + bw * 0.34, by + bh * 0.63)
        cr.show_text("Synapse")

        # A2. [🧑‍🚀 Cadet Avatar & Student Roster] Pill (Clickable to switch Classroom Student Profile)
        avx, avy, avw, avh = W * 0.175, H * 0.042, W * 0.112, H * 0.082
        self.hitboxes["avatar_btn"] = (avx, avy, avw, avh)
        av_idx = 0
        av_name = "Cadet Nova"
        if hasattr(self.studio, "pack_mgr"):
            av_idx = int(self.studio.pack_mgr.profile.get("avatar_idx", 0)) % len(PLAYER_AVATARS)
            av = PLAYER_AVATARS[av_idx]
            av_name = self.studio.pack_mgr.profile.get("player_name", av["name_fr"] if is_fr else av["name_en"])
        self._draw_pill(
            cr, avx, avy, avw, avh,
            (0.22, 0.30, 0.54), (0.12, 0.18, 0.36), (0.52, 0.72, 0.98),
            hover=(self.hovered_id == "avatar_btn"),
        )
        self._draw_avatar_badge(cr, avx + avh * 0.46, avy + avh * 0.50, avh * 0.36, av_idx)
        cr.set_font_size(max(10.0, H * 0.017))
        cr.set_source_rgb(0.98, 0.95, 0.82)
        cr.move_to(avx + avh * 0.88, avy + avh * 0.46)
        cr.show_text(av_name[:11])
        cr.set_font_size(max(8.5, H * 0.013))
        cr.set_source_rgba(0.65, 0.88, 1.0, 0.92)
        cr.move_to(avx + avh * 0.88, avy + avh * 0.76)
        cr.show_text("↻ Student" if not is_fr else "↻ Élève")

        # B1. [◀ ⭐ Level 1: Space Moon Landing ▶] Orange Banner Pill (Center)
        lx, ly, lw, lh = W * 0.293, H * 0.042, W * 0.332, H * 0.082
        self.hitboxes["prev_level"] = (lx, ly, lw * 0.14, lh)
        self.hitboxes["cycle_level"] = (lx + lw * 0.14, ly, lw * 0.86, lh)
        self._draw_pill(
            cr, lx, ly, lw, lh,
            (0.94, 0.46, 0.14), (0.78, 0.29, 0.06), (0.99, 0.68, 0.28),
            hover=(self.hovered_id in ("cycle_level", "prev_level")),
        )
        # Left '◀' arrow for previous level
        cr.set_font_size(max(12.0, H * 0.022))
        cr.set_source_rgba(1.0, 0.95, 0.80, 0.92)
        cr.move_to(lx + 11, ly + lh * 0.63)
        cr.show_text("◂")
        self._draw_star(cr, lx + lw * 0.10, ly + lh * 0.50, lh * 0.24, lh * 0.11, filled=True)
        lv_title = lv["title_fr"] if is_fr else lv["title_en"]
        cr.set_font_size(max(12.0, H * 0.022))
        cr.set_source_rgb(1.0, 1.0, 1.0)
        ext = cr.text_extents(lv_title)
        cr.move_to(lx + (lw - ext.width) * 0.54, ly + lh * 0.63)
        cr.show_text(lv_title)
        # Right '▸' arrow for next level
        cr.set_font_size(max(12.0, H * 0.022))
        cr.set_source_rgba(1.0, 0.95, 0.80, 0.92)
        cr.move_to(lx + lw - 20, ly + lh * 0.63)
        cr.show_text("▸")

        # B2. [🗺️ World Map / Carte] Interactive 2D World Map Toggle Pill
        mx, my, mw, mh = W * 0.631, H * 0.042, W * 0.105, H * 0.082
        self.hitboxes["map_btn"] = (mx, my, mw, mh)
        is_map = (self.view_mode == "map")
        self._draw_pill(
            cr, mx, my, mw, mh,
            (0.56, 0.24, 0.88) if not is_map else (0.16, 0.76, 0.52),
            (0.34, 0.12, 0.62) if not is_map else (0.08, 0.48, 0.32),
            (0.82, 0.58, 1.0) if not is_map else (0.52, 0.98, 0.75),
            hover=(self.hovered_id == "map_btn"),
            glow=is_map,
        )
        cr.set_font_size(max(11.5, H * 0.020))
        cr.set_source_rgb(1.0, 1.0, 1.0)
        map_lbl = ("▶ Labo" if is_fr else "▶ Sim Lab") if is_map else ("❖ Carte" if is_fr else "❖ World Map")
        ext_mp = cr.text_extents(map_lbl)
        cr.move_to(mx + (mw - ext_mp.width) * 0.5, my + mh * 0.63)
        cr.show_text(map_lbl)

        # C. [⚙ Mode Professeur / Teacher Mode] Small Top-Right Pill + [FR/EN] Toggle
        tx, ty, tw, th = W * 0.742, H * 0.026, W * 0.156, H * 0.040
        self.hitboxes["teacher_mode"] = (tx, ty, tw, th)
        self._draw_pill(
            cr, tx, ty, tw, th,
            (0.16, 0.22, 0.34), (0.10, 0.14, 0.22), (0.45, 0.58, 0.78),
            hover=(self.hovered_id == "teacher_mode"),
        )
        pin_locked = bool(self.studio.pack_mgr.profile.get("pin_lock_enabled", False)) if hasattr(self.studio, "pack_mgr") else False
        lock_ic = "[PIN] " if pin_locked else "⚙ "
        t_label = f"{lock_ic}Mode Professeur" if is_fr else f"{lock_ic}Teacher / School"
        cr.set_font_size(max(10.5, H * 0.017))
        cr.set_source_rgb(0.92, 0.96, 1.0)
        ext_t = cr.text_extents(t_label)
        cr.move_to(tx + (tw - ext_t.width) * 0.5, ty + th * 0.67)
        cr.show_text(t_label)

        # Language toggle pill [FR / EN] right next to Teacher Mode
        lgx, lgy, lgw, lgh = W * 0.904, H * 0.026, W * 0.064, H * 0.040
        self.hitboxes["toggle_lang"] = (lgx, lgy, lgw, lgh)
        self._draw_pill(
            cr, lgx, lgy, lgw, lgh,
            (0.20, 0.32, 0.52), (0.12, 0.20, 0.36), (0.48, 0.72, 0.98),
            hover=(self.hovered_id == "toggle_lang"),
        )
        lang_txt = "FR ▸ EN" if is_fr else "EN ▸ FR"
        cr.set_font_size(max(10.0, H * 0.016))
        cr.set_source_rgb(0.98, 0.90, 0.45)
        ext_lg = cr.text_extents(lang_txt)
        cr.move_to(lgx + (lgw - ext_lg.width) * 0.5, lgy + lgh * 0.67)
        cr.show_text(lang_txt)

        # D1. [Trophies & Shop] Blue/Gold Pill + D2. [★ Year N ↻] Emerald School Year Pill
        bgx, bgy, bgw, bgh = W * 0.742, H * 0.073, W * 0.110, H * 0.064
        self.hitboxes["badges_btn"] = (bgx, bgy, bgw, bgh)
        is_tr = (self.view_mode == "trophies")
        self._draw_pill(
            cr, bgx, bgy, bgw, bgh,
            (0.88, 0.56, 0.12) if is_tr else (0.14, 0.48, 0.92),
            (0.62, 0.36, 0.05) if is_tr else (0.08, 0.30, 0.68),
            (1.0, 0.84, 0.35) if is_tr else (0.38, 0.75, 0.98),
            hover=(self.hovered_id == "badges_btn"),
            glow=is_tr,
        )
        cr.set_font_size(max(10.5, H * 0.018))
        cr.set_source_rgb(1.0, 1.0, 1.0)
        earned_cnt = max(1, len(self.studio.earned_badges))
        b_txt = f"Boutique ({earned_cnt})" if is_fr else f"Shop ({earned_cnt})"
        cr.move_to(bgx + 12, bgy + bgh * 0.63)
        cr.show_text(b_txt)
        self._draw_trophy_icon(cr, bgx + bgw - 17, bgy + bgh * 0.52, min(W, H) / 880.0)

        # D2. [★ Year K..12 ↻] Emerald-Gold K-12 Grade Advancement Pill
        upx, upy, upw, uph = W * 0.858, H * 0.073, W * 0.110, H * 0.064
        self.hitboxes["upgrade_pack"] = (upx, upy, upw, uph)
        self._draw_pill(
            cr, upx, upy, upw, uph,
            (0.14, 0.74, 0.42), (0.07, 0.48, 0.26), (0.45, 0.96, 0.68),
            hover=(self.hovered_id == "upgrade_pack"),
            glow=True,
        )
        yr_lbl = "1"
        if hasattr(self.studio, "pack_mgr"):
            cur_yr = self.studio.pack_mgr.get_current_school_year()
            yr_lbl = "K" if cur_yr == 0 else str(cur_yr)
        up_txt = f"★ An {yr_lbl} ↻" if is_fr else f"★ Year {yr_lbl} ↻"
        cr.set_font_size(max(11.5, H * 0.020))
        cr.set_source_rgb(1.0, 0.98, 0.85)
        ext_up = cr.text_extents(up_txt)
        cr.move_to(upx + (upw - ext_up.width) * 0.5, upy + uph * 0.64)
        cr.show_text(up_txt)

        # ======================================================================
        # LEFT MAIN BOX: SIMULATION / WORLD MAP / TROPHY ROOM & SHOP / PIN GATE
        # ======================================================================
        sx, sy, sw, sh = W * 0.032, H * 0.145, W * 0.562, H * 0.585
        self.hitboxes["sim_box"] = (sx, sy, sw, sh)
        self._rounded_rect(cr, sx, sy, sw, sh, 16)
        pat_sim = cairo.LinearGradient(sx, sy, sx, sy + sh)
        pat_sim.add_color_stop_rgb(0.0, 0.02, 0.04, 0.09)
        pat_sim.add_color_stop_rgb(1.0, 0.05, 0.10, 0.20)
        cr.set_source(pat_sim)
        cr.fill_preserve()

        # Clip viewport contents inside rounded rect
        cr.save()
        cr.clip()

        if self.view_mode == "map":
            self._draw_world_map_viewport(cr, sx, sy, sw, sh, phase, is_fr)
        elif self.view_mode == "trophies":
            self._draw_trophy_room_viewport(cr, sx, sy, sw, sh, phase, is_fr)
        elif self.view_mode == "pin":
            self._draw_pin_gate_viewport(cr, sx, sy, sw, sh, phase, is_fr)
        else:
            if lv["lab_id"] == "moon_lander":
                self._draw_kid_moon_simulation(cr, sx, sy, sw, sh, phase, is_fr)
            else:
                # Render the selected level's live simulation cleanly below the 34px SIMULATION header bar
                sub_h = max(80.0, sh - 34.0)
                cr.save()
                cr.translate(sx, sy + 34.0)
                lid = lv["lab_id"]
                if lid == "raycast_car":
                    self.studio._render_raycast_car(cr, sw, sub_h)
                elif lid == "rl_gridworld":
                    self.studio._render_rl_gridworld(cr, sw, sub_h)
                elif lid == "cartpole_rl":
                    self.studio._render_cartpole(cr, sw, sub_h)
                elif lid == "nn_playground":
                    self.studio._render_nn_playground(cr, sw, sub_h)
                elif lid == "swarm_ecosystem":
                    self.studio._render_swarm(cr, sw, sub_h)
                elif lid == "prime_attention":
                    self.studio._render_prime_attention(cr, sw, sub_h)
                cr.restore()

            # Top-Left "SIMULATION" title + 7 One-Click Level Buttons + Click Hint
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(max(13.0, H * 0.023))
            cr.set_source_rgba(0.95, 0.98, 1.0, 0.95)
            cr.move_to(sx + 14, sy + 23)
            cr.show_text("SIMULATION")

            # 7 Quick-Jump Level Pills so kids can pick any level in the active pack in 1 click
            pill_start_x = sx + 138
            pill_w, pill_h = 30.0, 20.0
            for idx_l in range(len(LEVEL_DATA)):
                px_l = pill_start_x + idx_l * (pill_w + 4.5)
                py_l = sy + 7.0
                hid_l = f"level_jump_{idx_l}"
                self.hitboxes[hid_l] = (px_l, py_l, pill_w, pill_h)
                is_cur = (idx_l == (self.level_idx % len(LEVEL_DATA)))
                is_hov = (self.hovered_id == hid_l)
                self._rounded_rect(cr, px_l, py_l, pill_w, pill_h, 6)
                if is_cur:
                    cr.set_source_rgb(0.95, 0.52, 0.14)
                elif is_hov:
                    cr.set_source_rgb(0.24, 0.56, 0.92)
                else:
                    cr.set_source_rgba(0.12, 0.24, 0.42, 0.85)
                cr.fill_preserve()
                cr.set_source_rgba(0.55, 0.82, 1.0, 0.95 if is_cur else 0.55)
                cr.set_line_width(1.4 if is_cur else 1.0)
                cr.stroke()
                cr.set_font_size(9.5)
                cr.set_source_rgb(1.0, 1.0, 1.0)
                lv_num = LEVEL_DATA[idx_l].get("level", idx_l + 1)
                lbl_l = f"L{lv_num}"
                ext_l = cr.text_extents(lbl_l)
                cr.move_to(px_l + (pill_w - ext_l.width) * 0.5, py_l + 14.0)
                cr.show_text(lbl_l)

            cr.set_font_size(max(9.5, H * 0.015))
            cr.set_source_rgba(0.45, 0.88, 1.0, 0.90)
            hint_t = "★ Clique dans l'écran pour interagir !" if is_fr else "★ Click inside screen to interact!"
            ext_h = cr.text_extents(hint_t)
            cr.move_to(sx + sw - ext_h.width - 12, sy + 21)
            cr.show_text(hint_t)

        cr.restore()

        # Glowing Blue Border around Left Main Viewport
        self._rounded_rect(cr, sx, sy, sw, sh, 16)
        cr.set_source_rgba(0.24, 0.72, 0.98, 0.95)
        cr.set_line_width(2.6)
        cr.stroke()

        # ======================================================================
        # RIGHT TOP CARD: 'LUMI' SOCRATIC AI COMPANION + REACTIVE MOOD + BUBBLE
        # ======================================================================
        rx, ry, rw, rh = W * 0.612, H * 0.165, W * 0.356, H * 0.285
        self.hitboxes["ask_robot"] = (rx, ry, rw, rh)
        self._rounded_rect(cr, rx, ry, rw, rh, 16)
        pat_rob = cairo.LinearGradient(rx, ry, rx, ry + rh)
        pat_rob.add_color_stop_rgb(0.0, 0.09, 0.19, 0.36)
        pat_rob.add_color_stop_rgb(1.0, 0.07, 0.14, 0.27)
        cr.set_source(pat_rob)
        cr.fill_preserve()
        cr.set_source_rgba(0.24, 0.58, 0.92, 0.85)
        cr.set_line_width(2.0)
        cr.stroke()

        # Draw Lumi Robot Mascot on left of card
        rob_cx = rx + rw * 0.18
        rob_cy = ry + rh * 0.56
        self._draw_robot_mascot(cr, rob_cx, rob_cy, scale=min(W, H) / 680.0, anim_phase=phase)

        # Mini Lumi Name + Reactive Mood Pill under/above mascot
        mood_labels = {
            "happy": ("LUMI • CONTENT" if is_fr else "LUMI • HAPPY", (0.20, 0.82, 0.95)),
            "cheering": ("LUMI • BRAVO !" if is_fr else "LUMI • CHEERING!", (0.98, 0.82, 0.18)),
            "thinking": ("LUMI • RÉFLÉCHIT" if is_fr else "LUMI • THINKING", (0.65, 0.45, 0.98)),
            "dizzy": ("LUMI • OUPS !" if is_fr else "LUMI • OOPS!", (0.98, 0.38, 0.28)),
            "sleepy": ("LUMI • ZZZ..." if is_fr else "LUMI • SLEEPY", (0.55, 0.72, 0.95)),
        }
        m_txt, m_col = mood_labels.get(self.pet_mood, mood_labels["happy"])
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(max(8.5, H * 0.013))
        cr.set_source_rgb(*m_col)
        ext_m = cr.text_extents(m_txt)
        cr.move_to(rob_cx - ext_m.width * 0.5, ry + rh - 8)
        cr.show_text(m_txt)

        # Cream Speech Bubble on right of card
        sb_x = rx + rw * 0.35
        sb_y = ry + rh * 0.10
        sb_w = rw * 0.61
        sb_h = rh * 0.80
        self._rounded_rect(cr, sb_x, sb_y, sb_w, sb_h, 14)
        cr.set_source_rgb(0.99, 0.97, 0.92)
        cr.fill_preserve()
        cr.set_source_rgb(0.75, 0.82, 0.90)
        cr.set_line_width(1.6)
        cr.stroke()

        # Speech bubble pointer triangle pointing to Lumi
        cr.move_to(sb_x + 1, sb_y + sb_h * 0.42)
        cr.line_to(sb_x - 13, sb_y + sb_h * 0.52)
        cr.line_to(sb_x + 1, sb_y + sb_h * 0.62)
        cr.close_path()
        cr.set_source_rgb(0.99, 0.97, 0.92)
        cr.fill()

        # Speech bubble text
        speech_txt = self.custom_speech or (lv["speech_fr"] if is_fr else lv["speech_en"])
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        font_sz = max(11.5, H * 0.0195)
        cr.set_font_size(font_sz)
        cr.set_source_rgb(0.08, 0.12, 0.20)
        wrapped = self._wrap_text(cr, speech_txt, sb_w - 20)
        line_h = font_sz * 1.28
        start_ty = sb_y + (sb_h - len(wrapped[:5]) * line_h) * 0.5 + font_sz * 0.82
        for i, line in enumerate(wrapped[:5]):
            cr.move_to(sb_x + 11, start_ty + i * line_h)
            cr.show_text(line)

        # Small "[Click Lumi for Read-Aloud & Socratic Hint!]" footer inside speech bubble
        cr.set_font_size(max(8.5, H * 0.013))
        cr.set_source_rgb(0.22, 0.48, 0.82)
        hint_lumi = "♪ Clique Lumi : Lecture vocale + Indice IA !" if is_fr else "♪ Click Lumi: Read Aloud + AI Hint (+Coins)!"
        cr.move_to(sb_x + 11, sb_y + sb_h - 6)
        cr.show_text(hint_lumi)

        # ======================================================================
        # RIGHT BOTTOM CARD: 🎯 LEVEL OBJECTIVES + ⚡ DAILY MISSIONS (+COINS)
        # ======================================================================
        ox, oy, ow, oh = W * 0.612, H * 0.465, W * 0.356, H * 0.268
        self._rounded_rect(cr, ox, oy, ow, oh, 16)
        pat_obj = cairo.LinearGradient(ox, oy, ox, oy + oh)
        pat_obj.add_color_stop_rgb(0.0, 0.07, 0.14, 0.27)
        pat_obj.add_color_stop_rgb(1.0, 0.05, 0.10, 0.20)
        cr.set_source(pat_obj)
        cr.fill_preserve()
        cr.set_source_rgba(0.18, 0.36, 0.60, 0.80)
        cr.set_line_width(1.8)
        cr.stroke()

        # Header: 🎯 Objectif + ⚡ Missions du Jour
        self._draw_target_icon(cr, ox + 22, oy + oh * 0.13, max(7.5, H * 0.013))
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(max(12.0, H * 0.020))
        cr.set_source_rgb(0.96, 0.98, 1.0)
        cr.move_to(ox + 36, oy + oh * 0.16)
        cr.show_text("Objectifs & Missions du Jour" if is_fr else "Level Goals & Daily Missions")

        # Level Checkboxes 1 & 2 (Compact rows)
        cb_size = max(14.0, H * 0.023)
        cb1_x, cb1_y = ox + 16, oy + oh * 0.23
        self._rounded_rect(cr, cb1_x, cb1_y, cb_size, cb_size, 4)
        cr.set_source_rgba(0.25, 0.14, 0.12, 0.7)
        cr.fill_preserve()
        cr.set_source_rgb(0.92, 0.45, 0.20)
        cr.set_line_width(1.8)
        cr.stroke()
        if self.obj1_done:
            cr.set_source_rgb(0.98, 0.75, 0.25)
            cr.set_line_width(2.0)
            cr.move_to(cb1_x + 3, cb1_y + cb_size * 0.52)
            cr.line_to(cb1_x + cb_size * 0.42, cb1_y + cb_size - 3)
            cr.line_to(cb1_x + cb_size - 3, cb1_y + 3)
            cr.stroke()

        cr.set_font_size(max(11.0, H * 0.018))
        cr.set_source_rgb(0.94, 0.97, 1.0)
        cr.move_to(cb1_x + cb_size + 8, cb1_y + cb_size * 0.80)
        cr.show_text(lv["obj1_fr"] if is_fr else lv["obj1_en"])

        cb2_x, cb2_y = ox + 16, oy + oh * 0.39
        self._rounded_rect(cr, cb2_x, cb2_y, cb_size, cb_size, 4)
        cr.set_source_rgba(0.08, 0.28, 0.18, 0.8)
        cr.fill_preserve()
        cr.set_source_rgb(0.18, 0.82, 0.48)
        cr.set_line_width(1.8)
        cr.stroke()
        if self.obj2_done:
            cr.set_source_rgb(0.25, 0.95, 0.55)
            cr.set_line_width(2.0)
            cr.move_to(cb2_x + 3, cb2_y + cb_size * 0.52)
            cr.line_to(cb2_x + cb_size * 0.42, cb2_y + cb_size - 3)
            cr.line_to(cb2_x + cb_size - 3, cb2_y + 3)
            cr.stroke()

        obj2_txt = lv["obj2_fr"] if is_fr else lv["obj2_en"]
        cr.set_source_rgb(0.94, 0.97, 1.0)
        cr.move_to(cb2_x + cb_size + 8, cb2_y + cb_size * 0.80)
        cr.show_text(obj2_txt)
        ext2 = cr.text_extents(obj2_txt)
        cr.set_source_rgb(0.28, 0.92, 0.52)
        cr.move_to(cb2_x + cb_size + 14 + ext2.width, cb2_y + cb_size * 0.80)
        cr.show_text("+100 pts")

        # Divider line before Daily Missions
        cr.set_source_rgba(0.32, 0.58, 0.88, 0.38)
        cr.set_line_width(1.0)
        cr.move_to(ox + 14, oy + oh * 0.53)
        cr.line_to(ox + ow - 14, oy + oh * 0.53)
        cr.stroke()

        # 3 Daily Missions with live progress & +Coin rewards
        missions = []
        if hasattr(self.studio, "pack_mgr"):
            missions = self.studio.pack_mgr.profile.get("daily_missions", [])
        for m_i, m in enumerate(missions[:3]):
            my_row = oy + oh * (0.63 + m_i * 0.13)
            m_done = bool(m.get("completed", False) or m.get("done", False))
            m_prog = int(m.get("progress", 0))
            m_targ = int(m.get("target", 1))
            m_rew = int(m.get("reward_coins", 50))
            m_title = m.get("title_fr" if is_fr else "title_en", "")
            cr.set_font_size(max(10.0, H * 0.016))
            if m_done:
                cr.set_source_rgb(0.32, 0.96, 0.58)
                prefix = "✓ "
            else:
                cr.set_source_rgb(0.82, 0.90, 1.0)
                prefix = "⚡ "
            cr.move_to(ox + 16, my_row)
            cr.show_text(f"{prefix}{m_title} ({m_prog}/{m_targ})")

            # Coin reward pill on right of mission row
            cr.set_source_rgb(0.99, 0.84, 0.25 if not m_done else 0.55)
            rew_str = "✓ REÇU" if (m_done and is_fr) else ("✓ CLAIMED" if m_done else f"+{m_rew} ★")
            ext_r = cr.text_extents(rew_str)
            cr.move_to(ox + ow - ext_r.width - 14, my_row)
            cr.show_text(rew_str)

        # ======================================================================
        # BOTTOM BAR: 🕹️ COMMANDES SIMPLES + COINS + SCORE ⭐⭐⭐ + 4 BIG BUTTONS
        # ======================================================================
        dx, dy, dw, dh = W * 0.032, H * 0.752, W * 0.936, H * 0.212
        self._rounded_rect(cr, dx, dy, dw, dh, 16)
        pat_dk = cairo.LinearGradient(dx, dy, dx, dy + dh)
        pat_dk.add_color_stop_rgb(0.0, 0.07, 0.15, 0.29)
        pat_dk.add_color_stop_rgb(1.0, 0.05, 0.11, 0.22)
        cr.set_source(pat_dk)
        cr.fill_preserve()
        cr.set_source_rgba(0.18, 0.38, 0.65, 0.75)
        cr.set_line_width(1.8)
        cr.stroke()

        # Joystick icon + "Commandes simples" / "Simple Controls"
        jx, jy = dx + 24, dy + dh * 0.23
        cr.set_source_rgb(0.45, 0.55, 0.68)
        self._rounded_rect(cr, jx - 9, jy + 3, 18, 6, 2)
        cr.fill()
        cr.set_line_width(2.5)
        cr.move_to(jx, jy + 3)
        cr.line_to(jx, jy - 5)
        cr.stroke()
        cr.set_source_rgb(0.95, 0.25, 0.22)
        cr.arc(jx, jy - 7, 4.8, 0, 2 * math.pi)
        cr.fill()

        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(max(14.0, H * 0.024))
        cr.set_source_rgb(0.96, 0.98, 1.0)
        cr.move_to(jx + 18, jy + 5)
        cr.show_text("Commandes simples" if is_fr else "Simple Controls")

        # Persistent Coins + Lifetime Score + Level Stars: 250 Coins | ★ 1,200 pts | Score: ⭐⭐⭐ (3/3)
        lifetime_pts = 300
        coins_val = 250
        if hasattr(self.studio, "pack_mgr"):
            lifetime_pts = int(self.studio.pack_mgr.profile.get("lifetime_points", 300))
            coins_val = int(self.studio.pack_mgr.profile.get("coins", 250))

        coin_x = dx + dw * 0.32
        pts_x = dx + dw * 0.50
        sc_x = dx + dw * 0.71
        sc_y = dy + dh * 0.24

        # Gold Coin icon + counter
        cr.new_path()
        cr.set_source_rgb(0.99, 0.82, 0.18)
        cr.arc(coin_x, sc_y - 2, 8.5, 0, 2 * math.pi)
        cr.fill_preserve()
        cr.set_source_rgb(0.75, 0.52, 0.06)
        cr.set_line_width(1.5)
        cr.stroke()
        cr.set_font_size(max(12.5, H * 0.021))
        cr.set_source_rgb(1.0, 0.92, 0.42)
        cr.move_to(coin_x + 13, sc_y + 4)
        cr.show_text(f"{coins_val} {'Pièces' if is_fr else 'Coins'}")

        cr.set_font_size(max(12.5, H * 0.021))
        cr.set_source_rgb(0.55, 0.92, 1.0)
        pts_lbl = f"★ Total: {lifetime_pts} pts"
        cr.move_to(pts_x, sc_y + 4)
        cr.show_text(pts_lbl)

        cr.set_font_size(max(14.0, H * 0.024))
        cr.set_source_rgb(0.96, 0.98, 1.0)
        cr.move_to(sc_x, sc_y + 4)
        cr.show_text("Score:")
        for s_idx in range(3):
            self._draw_star(
                cr,
                sc_x + 72 + s_idx * 26,
                sc_y - 2,
                outer_r=10.5,
                inner_r=4.8,
                filled=(s_idx < self.stars_score),
            )
        cr.set_source_rgb(0.96, 0.98, 1.0)
        cr.move_to(sc_x + 156, sc_y + 4)
        cr.show_text(f"({self.stars_score}/3)")

        # 4 Gamified Pill Buttons across the bottom
        btn_y = dy + dh * 0.40
        btn_h = dh * 0.49
        gap = dw * 0.018
        btn_w = (dw - 36 - 3 * gap) / 4.0
        start_bx = dx + 18
        icon_scale = min(W, H) / 680.0

        # Button 1: 🧠 Rendre plus intelligent / Make Smarter
        b1x = start_bx
        self.hitboxes["btn_smarter"] = (b1x, btn_y, btn_w, btn_h)
        self._draw_pill(
            cr, b1x, btn_y, btn_w, btn_h,
            (0.08, 0.72, 0.62), (0.04, 0.52, 0.45), (0.35, 0.94, 0.82),
            hover=(self.hovered_id == "btn_smarter"),
            glow=(self.smart_boost > 0),
        )
        self._draw_brain_icon(cr, b1x + btn_w * 0.19, btn_y + btn_h * 0.50, icon_scale)
        l1_a, l1_b = lv["btn1_fr"] if is_fr else lv["btn1_en"]
        self._draw_two_line_btn_label(cr, b1x + btn_w * 0.34, btn_y, btn_h, l1_a, l1_b, H)

        # Button 2: ⛽ Plus de carburant / More Fuel
        b2x = start_bx + (btn_w + gap)
        self.hitboxes["btn_fuel"] = (b2x, btn_y, btn_w, btn_h)
        self._draw_pill(
            cr, b2x, btn_y, btn_w, btn_h,
            (0.92, 0.48, 0.12), (0.76, 0.32, 0.06), (0.99, 0.76, 0.32),
            hover=(self.hovered_id == "btn_fuel"),
            glow=self.fuel_boost,
        )
        self._draw_fuel_icon(cr, b2x + btn_w * 0.19, btn_y + btn_h * 0.50, icon_scale)
        l2_a, l2_b = lv["btn2_fr"] if is_fr else lv["btn2_en"]
        self._draw_two_line_btn_label(cr, b2x + btn_w * 0.34, btn_y, btn_h, l2_a, l2_b, H)

        # Button 3: 🌙 Gravité Légère / Light Gravity
        b3x = start_bx + 2 * (btn_w + gap)
        self.hitboxes["btn_gravity"] = (b3x, btn_y, btn_w, btn_h)
        self._draw_pill(
            cr, b3x, btn_y, btn_w, btn_h,
            (0.14, 0.48, 0.92), (0.08, 0.32, 0.72), (0.42, 0.76, 0.99),
            hover=(self.hovered_id == "btn_gravity"),
            glow=self.light_grav,
        )
        self._draw_moon_icon(cr, b3x + btn_w * 0.19, btn_y + btn_h * 0.50, icon_scale)
        l3_a, l3_b = lv["btn3_fr"] if is_fr else lv["btn3_en"]
        self._draw_two_line_btn_label(cr, b3x + btn_w * 0.34, btn_y, btn_h, l3_a, l3_b, H)

        # Button 4: ▶ Relancer le test / Run Test!
        b4x = start_bx + 3 * (btn_w + gap)
        self.hitboxes["btn_relaunch"] = (b4x, btn_y, btn_w, btn_h)
        self._draw_pill(
            cr, b4x, btn_y, btn_w, btn_h,
            (0.18, 0.80, 0.36), (0.10, 0.60, 0.24), (0.52, 0.96, 0.65),
            hover=(self.hovered_id == "btn_relaunch"),
            glow=True,
        )
        # Play triangle icon
        px_c = b4x + btn_w * 0.16
        py_c = btn_y + btn_h * 0.50
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.move_to(px_c - 6, py_c - 9)
        cr.line_to(px_c + 9, py_c)
        cr.line_to(px_c - 6, py_c + 9)
        cr.close_path()
        cr.fill()

        run_lbl = "Relancer le test" if is_fr else "Run Test!"
        cr.set_font_size(max(14.0, H * 0.024))
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.move_to(b4x + btn_w * 0.26, btn_y + btn_h * 0.58)
        cr.show_text(run_lbl)

        return False

    # ==========================================================================
    # INTERACTIVE 2D WORLD MAP VIEWPORT ("map" mode)
    # ==========================================================================
    def _draw_world_map_viewport(
        self,
        cr: cairo.Context,
        sx: float,
        sy: float,
        sw: float,
        sh: float,
        phase: float,
        is_fr: bool,
    ) -> None:
        """Draws the 2D Interactive Star-Island World Map with 7 clickable AI Lab Zones."""
        # 1. Deep space nebula backdrop
        pat = cairo.RadialGradient(sx + sw * 0.5, sy + sh * 0.5, 20, sx + sw * 0.5, sy + sh * 0.5, sw * 0.65)
        pat.add_color_stop_rgba(0.0, 0.16, 0.10, 0.38, 0.95)
        pat.add_color_stop_rgba(0.6, 0.06, 0.12, 0.28, 0.95)
        pat.add_color_stop_rgba(1.0, 0.02, 0.05, 0.12, 1.0)
        cr.set_source(pat)
        cr.rectangle(sx, sy, sw, sh)
        cr.fill()

        # Header banner
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(max(14.0, sh * 0.042))
        cr.set_source_rgb(0.98, 0.92, 0.45)
        title = "❖ CARTE DU MONDE SYNAPSE — CLIQUE SUR UNE ÎLE IA !" if is_fr else "❖ SYNAPSE WORLD MAP — CLICK ANY AI ISLAND TO FLY THERE!"
        cr.move_to(sx + 16, sy + 28)
        cr.show_text(title)

        # 2. Animated flight paths connecting the 7 islands
        pts = [(sx + sw * z["x"], sy + sh * z["y"]) for z in WORLD_MAP_ZONES]
        cr.save()
        cr.set_source_rgba(0.38, 0.82, 0.98, 0.55)
        cr.set_line_width(2.5)
        cr.set_dash([8.0, 6.0], -phase * 10.0)
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)
        cr.stroke()
        cr.restore()

        # 3. Draw each of the 7 Star-Island Nodes
        cur_idx = self.level_idx % len(WORLD_MAP_ZONES)
        runs_map = {}
        if hasattr(self.studio, "pack_mgr"):
            runs_map = self.studio.pack_mgr.profile.get("lab_runs_count", {})

        for idx, z in enumerate(WORLD_MAP_ZONES):
            zx, zy = pts[idx]
            rc, gc, bc = z["color"]
            hid = f"map_zone_{idx}"
            rad = min(sw, sh) * 0.088
            self.hitboxes[hid] = (zx - rad * 1.25, zy - rad * 1.1, rad * 2.5, rad * 2.3)
            is_cur = (idx == cur_idx)
            is_hov = (self.hovered_id == hid)

            # Pulsing outer ring for active or hovered island
            if is_cur or is_hov:
                pulse_r = rad * (1.28 + 0.08 * math.sin(phase * 3.0))
                cr.new_path()
                cr.set_source_rgba(rc, gc, bc, 0.35)
                cr.arc(zx, zy, pulse_r, 0, 2 * math.pi)
                cr.fill()

            # Floating island base disc
            cr.save()
            cr.translate(zx, zy + rad * 0.32)
            cr.scale(1.22, 0.52)
            cr.new_path()
            cr.set_source_rgba(rc * 0.5, gc * 0.5, bc * 0.5, 0.9)
            cr.arc(0, 0, rad, 0, 2 * math.pi)
            cr.fill()
            cr.restore()

            # Main glowing dome
            cr.new_path()
            cr.set_source_rgb(rc, gc, bc)
            cr.arc(zx, zy, rad * 0.85, 0, 2 * math.pi)
            cr.fill_preserve()
            cr.set_source_rgb(1.0, 1.0, 1.0 if is_cur else 0.85)
            cr.set_line_width(3.0 if is_cur else 1.8)
            cr.stroke()

            # Zone number & icon inside dome
            cr.set_font_size(max(13.0, rad * 0.52))
            cr.set_source_rgb(1.0, 1.0, 1.0)
            num_str = f"L{idx + 1}"
            ext_n = cr.text_extents(num_str)
            cr.move_to(zx - ext_n.width * 0.5, zy + ext_n.height * 0.36)
            cr.show_text(num_str)

            # 3 mini stars above island
            for s_i in range(3):
                self._draw_star(
                    cr,
                    zx - 14 + s_i * 14,
                    zy - rad * 1.02,
                    outer_r=5.5,
                    inner_r=2.5,
                    filled=True,
                )

            # Island name pill below dome
            z_name = z["name_fr"] if is_fr else z["name_en"]
            cr.set_font_size(max(10.0, sh * 0.025))
            ext_z = cr.text_extents(z_name)
            pw = ext_z.width + 16
            ph = 20.0
            self._rounded_rect(cr, zx - pw * 0.5, zy + rad * 0.88, pw, ph, 6)
            cr.set_source_rgba(0.05, 0.10, 0.22, 0.88)
            cr.fill_preserve()
            cr.set_source_rgba(rc, gc, bc, 0.85)
            cr.set_line_width(1.2)
            cr.stroke()
            cr.set_source_rgb(0.95, 0.98, 1.0)
            cr.move_to(zx - ext_z.width * 0.5, zy + rad * 0.88 + 14)
            cr.show_text(z_name)

            # Runs badge
            runs_cnt = int(runs_map.get(z["lab_id"], 1))
            cr.set_font_size(max(8.5, sh * 0.020))
            cr.set_source_rgb(0.65, 0.90, 1.0)
            r_str = f"★ {runs_cnt} {'vols' if is_fr else 'runs'}"
            ext_r = cr.text_extents(r_str)
            cr.move_to(zx - ext_r.width * 0.5, zy + rad * 0.88 + 31)
            cr.show_text(r_str)

            # Draw cute player rocket hovering over the active island!
            if is_cur:
                self._draw_cute_rocket(
                    cr,
                    zx + rad * 0.95,
                    zy - rad * 0.55 + math.sin(phase * 3.0) * 4.0,
                    scale=min(sw, sh) / 950.0,
                    angle=0.45,
                    thrusting=True,
                    anim_phase=phase,
                )

    # ==========================================================================
    # TROPHY ROOM & COIN SHOP VIEWPORT ("trophies" mode)
    # ==========================================================================
    def _draw_trophy_room_viewport(
        self,
        cr: cairo.Context,
        sx: float,
        sy: float,
        sw: float,
        sh: float,
        phase: float,
        is_fr: bool,
    ) -> None:
        """Draws the 12 Trophy Pedestals + the Interactive Coin Shop where kids unlock visual upgrades."""
        # Header
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(max(13.5, sh * 0.038))
        cr.set_source_rgb(1.0, 0.86, 0.28)
        coins_val = int(self.studio.pack_mgr.profile.get("coins", 250)) if hasattr(self.studio, "pack_mgr") else 250
        hdr = (
            f"★ SALLE DES TROPHÉES & BOUTIQUE  —  ★ {coins_val} PIÈCES DISPONIBLES"
            if is_fr
            else f"★ TROPHY VAULT & COIN SHOP  —  ★ {coins_val} COINS AVAILABLE"
        )
        cr.move_to(sx + 16, sy + 26)
        cr.show_text(hdr)

        # Back to Simulation button in top-right of viewport
        bk_w, bk_h = 115.0, 24.0
        bk_x, bk_y = sx + sw - bk_w - 12, sy + 7
        self.hitboxes["back_to_sim"] = (bk_x, bk_y, bk_w, bk_h)
        self._rounded_rect(cr, bk_x, bk_y, bk_w, bk_h, 7)
        cr.set_source_rgb(0.18, 0.68, 0.42)
        cr.fill()
        cr.set_font_size(10.5)
        cr.set_source_rgb(1.0, 1.0, 1.0)
        bk_lbl = "▶ Retour Labo" if is_fr else "▶ Back to Lab"
        ext_b = cr.text_extents(bk_lbl)
        cr.move_to(bk_x + (bk_w - ext_b.width) * 0.5, bk_y + 16)
        cr.show_text(bk_lbl)

        # SECTION 1: 12 Trophy Pedestals (2 rows x 6 columns)
        earned_set = set(self.studio.earned_badges)
        cols = 6
        cell_w = (sw - 28) / cols
        cell_h = sh * 0.162
        for idx, ped in enumerate(ALL_TROPHY_PEDESTALS[:12]):
            r_i = idx // cols
            c_i = idx % cols
            px = sx + 14 + c_i * cell_w
            py = sy + 36 + r_i * (cell_h + 6)
            unlocked = (ped["id"] in earned_set) or (idx < len(earned_set))

            self._rounded_rect(cr, px + 3, py, cell_w - 6, cell_h, 8)
            if unlocked:
                cr.set_source_rgba(0.24, 0.20, 0.08, 0.88)
            else:
                cr.set_source_rgba(0.08, 0.12, 0.20, 0.70)
            cr.fill_preserve()
            cr.set_source_rgba(0.98, 0.80, 0.22, 0.90 if unlocked else 0.25)
            cr.set_line_width(1.6 if unlocked else 1.0)
            cr.stroke()

            # Trophy icon on pedestal
            if unlocked:
                self._draw_trophy_icon(cr, px + cell_w * 0.5, py + cell_h * 0.36, min(sw, sh) / 960.0)
            else:
                cr.set_font_size(13.0)
                cr.set_source_rgba(0.55, 0.65, 0.78, 0.55)
                cr.move_to(px + cell_w * 0.5 - 4, py + cell_h * 0.44)
                cr.show_text("?")

            cr.set_font_size(max(8.0, sh * 0.018))
            cr.set_source_rgb(0.98, 0.92, 0.65 if unlocked else 0.45)
            p_name = ped["name_fr"] if is_fr else ped["name_en"]
            ext_p = cr.text_extents(p_name[:12])
            cr.move_to(px + (cell_w - ext_p.width) * 0.5, py + cell_h - 6)
            cr.show_text(p_name[:12])

        # SECTION 2: Interactive Coin Shop (4 Unlockable Decorations)
        shop_y = sy + sh * 0.505
        cr.set_font_size(max(12.0, sh * 0.030))
        cr.set_source_rgb(0.45, 0.90, 1.0)
        shop_hdr = (
            "❖ BOUTIQUE DE DÉCORATIONS (CLIQUE POUR ACHETER OU ÉQUIPER !)"
            if is_fr
            else "❖ VISUAL UPGRADE SHOP (CLICK ANY ITEM TO BUY OR EQUIP!)"
        )
        cr.move_to(sx + 16, shop_y)
        cr.show_text(shop_hdr)

        unlocked_decos = set()
        if hasattr(self.studio, "pack_mgr"):
            unlocked_decos = set(self.studio.pack_mgr.profile.get("unlocked_decorations", []))

        card_w = (sw - 36) / 2.0
        card_h = sh * 0.205
        for s_idx, item in enumerate(TROPHY_SHOP_ITEMS[:4]):
            sr = s_idx // 2
            sc = s_idx % 2
            cx_i = sx + 14 + sc * (card_w + 8)
            cy_i = shop_y + 10 + sr * (card_h + 8)
            iid = item["id"]
            hid_s = f"shop_buy_{iid}"
            self.hitboxes[hid_s] = (cx_i, cy_i, card_w, card_h)
            owned = iid in unlocked_decos
            hov = (self.hovered_id == hid_s)

            self._rounded_rect(cr, cx_i, cy_i, card_w, card_h, 10)
            if owned:
                cr.set_source_rgba(0.10, 0.34, 0.24, 0.92)
            elif hov:
                cr.set_source_rgba(0.18, 0.30, 0.52, 0.92)
            else:
                cr.set_source_rgba(0.08, 0.16, 0.30, 0.88)
            cr.fill_preserve()
            cr.set_source_rgba(0.35, 0.95, 0.62 if owned else 0.98, 0.90)
            cr.set_line_width(2.0 if (owned or hov) else 1.2)
            cr.stroke()

            # Item Title & Description
            cr.set_font_size(max(11.0, sh * 0.025))
            cr.set_source_rgb(1.0, 0.95, 0.75)
            inm = item["name_fr"] if is_fr else item["name_en"]
            cr.move_to(cx_i + 12, cy_i + 22)
            cr.show_text(inm)

            cr.set_font_size(max(8.5, sh * 0.0195))
            cr.set_source_rgb(0.75, 0.88, 1.0)
            idsc = item["desc_fr"] if is_fr else item["desc_en"]
            cr.move_to(cx_i + 12, cy_i + 41)
            cr.show_text(idsc[:32])

            # Price / Equipped Pill on right of card
            bw_p, bh_p = 84.0, 24.0
            bx_p = cx_i + card_w - bw_p - 10
            by_p = cy_i + (card_h - bh_p) * 0.5
            self._rounded_rect(cr, bx_p, by_p, bw_p, bh_p, 7)
            if owned:
                cr.set_source_rgb(0.16, 0.78, 0.44)
                lbl_p = "✓ ÉQUIPÉ" if is_fr else "✓ EQUIPPED"
            else:
                cr.set_source_rgb(0.92, 0.56, 0.12)
                lbl_p = f"★ {item['cost']}"
            cr.fill()
            cr.set_font_size(10.0)
            cr.set_source_rgb(1.0, 1.0, 1.0)
            ext_lp = cr.text_extents(lbl_p)
            cr.move_to(bx_p + (bw_p - ext_lp.width) * 0.5, by_p + 16)
            cr.show_text(lbl_p)

    # ==========================================================================
    # PIN-PROTECTED TEACHER GATE VIEWPORT ("pin" mode)
    # ==========================================================================
    def _draw_pin_gate_viewport(
        self,
        cr: cairo.Context,
        sx: float,
        sy: float,
        sw: float,
        sh: float,
        phase: float,
        is_fr: bool,
    ) -> None:
        """Draws the PIN-Protected Teacher / Parent Gate so kids don't accidentally enter Teacher Mode."""
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(max(15.0, sh * 0.044))
        cr.set_source_rgb(0.98, 0.86, 0.32)
        hdr = "◈ ACCÈS PROFESSEUR / PARENT (CODE PIN : 1234)" if is_fr else "◈ TEACHER & PARENT GATE (DEFAULT PIN: 1234)"
        ext_h = cr.text_extents(hdr)
        cr.move_to(sx + (sw - ext_h.width) * 0.5, sy + sh * 0.14)
        cr.show_text(hdr)

        # PIN display box
        disp_w, disp_h = 180.0, 40.0
        disp_x, disp_y = sx + (sw - disp_w) * 0.5, sy + sh * 0.20
        self._rounded_rect(cr, disp_x, disp_y, disp_w, disp_h, 10)
        cr.set_source_rgba(0.05, 0.10, 0.20, 0.95)
        cr.fill_preserve()
        cr.set_source_rgb(0.38, 0.78, 0.98)
        cr.set_line_width(2.0)
        cr.stroke()

        masked = " ".join("●" for _ in self.pin_buffer) or ("_ _ _ _")
        cr.set_font_size(18.0)
        cr.set_source_rgb(1.0, 1.0, 1.0)
        ext_m = cr.text_extents(masked)
        cr.move_to(disp_x + (disp_w - ext_m.width) * 0.5, disp_y + 27)
        cr.show_text(masked)

        # 3x4 Keypad
        keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "CLR", "0", "OK"]
        kw, kh = 68.0, 38.0
        grid_w = 3 * kw + 2 * 10.0
        start_kx = sx + (sw - grid_w) * 0.5
        start_ky = sy + sh * 0.34
        for idx, k in enumerate(keys):
            r_i = idx // 3
            c_i = idx % 3
            kx = start_kx + c_i * (kw + 10.0)
            ky = start_ky + r_i * (kh + 8.0)
            hid_k = f"pin_key_{k}"
            self.hitboxes[hid_k] = (kx, ky, kw, kh)
            self._rounded_rect(cr, kx, ky, kw, kh, 8)
            if k == "OK":
                cr.set_source_rgb(0.16, 0.76, 0.42)
            elif k == "CLR":
                cr.set_source_rgb(0.78, 0.28, 0.24)
            else:
                cr.set_source_rgb(0.14, 0.28, 0.50)
            cr.fill_preserve()
            cr.set_source_rgba(0.55, 0.82, 1.0, 0.85)
            cr.set_line_width(1.5)
            cr.stroke()
            cr.set_font_size(14.0)
            cr.set_source_rgb(1.0, 1.0, 1.0)
            ext_k = cr.text_extents(k)
            cr.move_to(kx + (kw - ext_k.width) * 0.5, ky + 24)
            cr.show_text(k)

        # Cancel / Back button
        bk_w, bk_h = 150.0, 32.0
        bk_x, bk_y = sx + (sw - bk_w) * 0.5, sy + sh * 0.86
        self.hitboxes["back_to_sim"] = (bk_x, bk_y, bk_w, bk_h)
        self._rounded_rect(cr, bk_x, bk_y, bk_w, bk_h, 8)
        cr.set_source_rgb(0.24, 0.38, 0.62)
        cr.fill()
        cr.set_font_size(12.0)
        cr.set_source_rgb(1.0, 1.0, 1.0)
        lbl_b = "◂ Retour Mode Enfant" if is_fr else "◂ Back to Kid Mode"
        ext_b = cr.text_extents(lbl_b)
        cr.move_to(bk_x + (bk_w - ext_b.width) * 0.5, bk_y + 21)
        cr.show_text(lbl_b)

    @staticmethod
    def _draw_two_line_btn_label(
        cr: cairo.Context,
        tx: float,
        by: float,
        bh: float,
        line1: str,
        line2: str,
        H: float,
    ) -> None:
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(max(13.0, H * 0.022))
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.move_to(tx, by + bh * 0.43)
        cr.show_text(line1)
        cr.move_to(tx, by + bh * 0.76)
        cr.show_text(line2)

    def _draw_kid_moon_simulation(
        self,
        cr: cairo.Context,
        sx: float,
        sy: float,
        sw: float,
        sh: float,
        phase: float,
        is_fr: bool,
    ) -> None:
        """Draws the NEAT Moon Lander with Solar Panels, Callouts, Constellations & Connected Live AI Brain."""
        # 1. Twinkling Stars & Constellation Lines in Space
        stars_pts: List[Tuple[float, float]] = []
        for i in range(44):
            st_x = sx + ((i * 137 + 29) % int(max(10, sw - 20))) + 10
            st_y = sy + ((i * 73 + 17) % int(max(10, sh * 0.64))) + 10
            stars_pts.append((st_x, st_y))
            twinkle = 0.40 + 0.50 * math.sin(phase * 1.5 + i * 0.9)
            rad = 1.7 if i % 5 == 0 else 1.0
            cr.new_path()
            cr.set_source_rgba(0.90, 0.96, 1.0, twinkle)
            cr.arc(st_x, st_y, rad, 0, 2 * math.pi)
            cr.fill()

        # Subtle constellation lines in top-right and top-left sky
        cr.set_source_rgba(0.25, 0.65, 0.95, 0.22)
        cr.set_line_width(1.0)
        constellation_pairs = [(2, 7), (7, 12), (12, 19), (5, 11), (11, 18), (24, 31), (31, 37)]
        for a, b in constellation_pairs:
            ax, ay = stars_pts[a]
            bx, by = stars_pts[b]
            if math.hypot(ax - bx, ay - by) < sw * 0.26:
                cr.move_to(ax, ay)
                cr.line_to(bx, by)
                cr.stroke()

        # Little orbiting satellite icon in upper-left space
        sat_x, sat_y = sx + sw * 0.12, sy + sh * 0.18
        cr.save()
        cr.translate(sat_x, sat_y)
        cr.rotate(-0.45)
        cr.set_source_rgba(0.38, 0.72, 0.96, 0.55)
        cr.rectangle(-12, -3, 7, 6)
        cr.rectangle(5, -3, 7, 6)
        cr.fill()
        cr.set_source_rgba(0.75, 0.85, 0.96, 0.70)
        cr.rectangle(-4, -4, 8, 8)
        cr.fill()
        cr.restore()

        # Unlockable 3D Hologram Planet ("holo_globe") in the upper-left sky!
        unlocked_decos = set()
        if hasattr(self.studio, "pack_mgr"):
            unlocked_decos = set(self.studio.pack_mgr.profile.get("unlocked_decorations", []))
        if "holo_globe" in unlocked_decos:
            gx, gy = sx + sw * 0.14, sy + sh * 0.28
            gr = min(sw, sh) * 0.065
            cr.save()
            cr.new_path()
            cr.set_source_rgba(0.18, 0.78, 0.98, 0.28)
            cr.arc(gx, gy, gr, 0, 2 * math.pi)
            cr.fill_preserve()
            cr.set_source_rgba(0.45, 0.95, 1.0, 0.75)
            cr.set_line_width(1.4)
            cr.stroke()
            # Spinning Saturn ring
            cr.translate(gx, gy)
            cr.rotate(0.32)
            cr.scale(1.65, 0.42)
            cr.new_path()
            cr.set_source_rgba(0.98, 0.82, 0.28, 0.75)
            cr.arc(0, 0, gr, 0, 2 * math.pi)
            cr.stroke()
            cr.restore()

        # 2. Lunar Horizon & Blue-Tinted 3D Cratered Surface (bottom 30% of simulation frame)
        moon_y = sy + sh * 0.70
        cr.new_path()
        cr.move_to(sx, sy + sh)
        cr.line_to(sx, moon_y + 14)
        cr.curve_to(sx + sw * 0.25, moon_y - 18, sx + sw * 0.55, moon_y - 18, sx + sw, moon_y + 12)
        cr.line_to(sx + sw, sy + sh)
        cr.close_path()

        pat_moon = cairo.LinearGradient(sx, moon_y - 18, sx, sy + sh)
        pat_moon.add_color_stop_rgb(0.0, 0.34, 0.56, 0.74)
        pat_moon.add_color_stop_rgb(0.45, 0.24, 0.42, 0.60)
        pat_moon.add_color_stop_rgb(1.0, 0.15, 0.28, 0.44)
        cr.set_source(pat_moon)
        cr.fill_preserve()
        cr.set_source_rgba(0.52, 0.80, 0.98, 0.75)
        cr.set_line_width(2.0)
        cr.stroke()

        # 3D Lunar Craters
        craters = [
            (0.15, 0.85, 0.080, 0.030),
            (0.32, 0.77, 0.065, 0.025),
            (0.46, 0.89, 0.070, 0.026),
            (0.66, 0.76, 0.060, 0.024),
            (0.82, 0.86, 0.085, 0.032),
        ]
        for cx_f, cy_f, rx_f, ry_f in craters:
            self._draw_lunar_crater(cr, sx + sw * cx_f, sy + sh * cy_f, sw * rx_f, sh * ry_f)

        # 2b. Glowing Lunar Landing Pad on the Moon surface directly under target x = 0.31
        pad_cx = sx + sw * 0.31
        pad_cy = sy + sh * 0.705
        pad_w = sw * 0.20
        pad_h = sh * 0.026
        self._rounded_rect(cr, pad_cx - pad_w * 0.5, pad_cy - pad_h * 0.5, pad_w, pad_h, 6)
        if self.rocket_state == "landed":
            cr.set_source_rgba(0.15, 0.95, 0.50, 0.88)
        elif self.rocket_state == "crashed":
            cr.set_source_rgba(0.98, 0.25, 0.22, 0.88)
        else:
            cr.set_source_rgba(0.18, 0.82, 0.55, 0.45 + 0.25 * math.sin(phase * 3.0))
        cr.fill_preserve()
        cr.set_source_rgba(0.55, 1.0, 0.78, 0.95)
        cr.set_line_width(2.0)
        cr.stroke()

        # Landing pad beacon lights + "LANDING PAD" label
        for side_b in (-1, 1):
            cr.new_path()
            cr.set_source_rgb(0.25, 1.0, 0.65)
            cr.arc(pad_cx + side_b * (pad_w * 0.44), pad_cy, 3.5, 0, 2 * math.pi)
            cr.fill()
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(max(8.5, sh * 0.022))
        cr.set_source_rgba(0.88, 1.0, 0.92, 0.92)
        pad_lbl = "ZONE D'ALUNISSAGE" if is_fr else "LUNAR LANDING PAD"
        ext_p = cr.text_extents(pad_lbl)
        cr.move_to(pad_cx - ext_p.width * 0.5, pad_cy + pad_h + 12)
        cr.show_text(pad_lbl)

        # 3. NEAT Moon Lander Position — maps directly to self.rocket_x / self.rocket_y so it descends all the way to the pad!
        rx_pos = sx + sw * self.rocket_x
        ry_pos = sy + sh * self.rocket_y
        r_scale = min(sw, sh) / 300.0

        # Vertical descent guide beam from lander to landing pad while flying
        if self.rocket_state == "flying":
            cr.save()
            cr.set_source_rgba(0.28, 0.92, 0.65, 0.35)
            cr.set_line_width(1.5)
            cr.set_dash([5.0, 5.0], -phase * 6.0)
            cr.move_to(rx_pos, ry_pos + 36 * r_scale)
            cr.line_to(pad_cx, pad_cy - pad_h * 0.5)
            cr.stroke()
            cr.restore()

        # Subtle concentric HUD telemetry rings around the Lander
        cr.new_path()
        cr.set_source_rgba(0.22, 0.65, 0.95, 0.14)
        cr.set_line_width(1.0)
        cr.arc(rx_pos, ry_pos, 58 * r_scale, 0, 2 * math.pi)
        cr.stroke()
        cr.set_dash([4.0, 4.0])
        cr.arc(rx_pos, ry_pos, 76 * r_scale, 0, 2 * math.pi)
        cr.stroke()
        cr.set_dash([])

        # 4. Connected Live Neural Network ("NEURAL NETWORK" / "AI BRAIN") on the Right Side of Sky
        nn_cx = sx + sw * 0.76
        nn_cy = sy + sh * 0.39
        self._draw_sky_neural_network(
            cr,
            lander_x=rx_pos + 22 * r_scale,
            lander_y=ry_pos + 4 * r_scale,
            nn_cx=nn_cx,
            nn_cy=nn_cy,
            scale=r_scale,
            phase=phase,
            is_fr=is_fr,
        )

        # 5. Draw Detailed NEAT Moon Lander with Solar Panels, Legs, Thrusters & Callouts
        self._draw_neat_moon_lander_craft(
            cr,
            cx=rx_pos,
            cy=ry_pos,
            scale=r_scale,
            angle=self.rocket_angle * 0.5,
            thrusting=self.rocket_thrusting,
            phase=phase,
            is_fr=is_fr,
        )

        # 6. Live Flight Telemetry Pill & Touchdown / Crash Celebration Banner
        alt_m = max(0, int((0.615 - self.rocket_y) * 260))
        spd_ms = abs(self.rocket_vy) * 1200.0
        hud_x, hud_y = sx + 14, sy + 38
        self._rounded_rect(cr, hud_x, hud_y, sw * 0.44, 24, 7)
        cr.set_source_rgba(0.05, 0.12, 0.24, 0.82)
        cr.fill()
        cr.set_font_size(max(9.5, sh * 0.025))
        cr.set_source_rgb(0.55, 0.90, 1.0)
        cr.move_to(hud_x + 8, hud_y + 16)
        cr.show_text(f"ALT: {alt_m:3d}m  |  SPD: {spd_ms:3.1f} m/s  |  FUEL: {int(self.rocket_fuel)}%")

        if self.rocket_state == "landed":
            bw, bh = sw * 0.50, 34
            bx, by = rx_pos - bw * 0.5, max(sy + 68, ry_pos - 78 * r_scale)
            self._rounded_rect(cr, bx, by, bw, bh, 10)
            cr.set_source_rgba(0.10, 0.78, 0.42, 0.94)
            cr.fill_preserve()
            cr.set_source_rgb(0.65, 1.0, 0.80)
            cr.set_line_width(2.0)
            cr.stroke()
            cr.set_font_size(max(11.5, sh * 0.032))
            cr.set_source_rgb(1.0, 1.0, 1.0)
            msg = "★ ALUNISSAGE RÉUSSI ! +100 PTS !" if is_fr else "★ TOUCHDOWN! +100 PTS!"
            ext_m = cr.text_extents(msg)
            cr.move_to(bx + (bw - ext_m.width) * 0.5, by + 22)
            cr.show_text(msg)
        elif self.rocket_state == "crashed":
            bw, bh = sw * 0.54, 34
            bx, by = rx_pos - bw * 0.5, max(sy + 68, ry_pos - 78 * r_scale)
            self._rounded_rect(cr, bx, by, bw, bh, 10)
            cr.set_source_rgba(0.88, 0.22, 0.18, 0.94)
            cr.fill_preserve()
            cr.set_source_rgb(1.0, 0.75, 0.45)
            cr.set_line_width(2.0)
            cr.stroke()
            cr.set_font_size(max(11.0, sh * 0.030))
            cr.set_source_rgb(1.0, 1.0, 1.0)
            msg = "⚠ TROP VITE ! AJOUTE DU CARBURANT !" if is_fr else "⚠ TOO FAST! CLICK MORE FUEL!"
            ext_m = cr.text_extents(msg)
            cr.move_to(bx + (bw - ext_m.width) * 0.5, by + 22)
            cr.show_text(msg)

    def _draw_neat_moon_lander_craft(
        self,
        cr: cairo.Context,
        cx: float,
        cy: float,
        scale: float,
        angle: float,
        thrusting: bool,
        phase: float,
        is_fr: bool,
    ) -> None:
        """Draws the detailed NEAT Moon Lander with Solar Panels, Sensors, Legs, Thrusters & Callouts."""
        cr.save()
        cr.translate(cx, cy)
        cr.rotate(angle)
        cr.scale(scale, scale)

        # A. Left & Right Solar Panel Wings (tilted blue photovoltaic grids)
        for side in (-1, 1):
            cr.save()
            cr.translate(side * 26, -6)
            cr.rotate(side * -0.18)
            # Strut bar
            cr.set_source_rgb(0.65, 0.75, 0.88)
            cr.set_line_width(2.5)
            cr.move_to(-side * 6, 0)
            cr.line_to(side * 4, 0)
            cr.stroke()
            # Panel frame
            px = 2 if side > 0 else -30
            self._rounded_rect(cr, px, -11, 28, 22, 3)
            cr.set_source_rgb(0.10, 0.38, 0.72)
            cr.fill_preserve()
            cr.set_source_rgb(0.55, 0.82, 0.98)
            cr.set_line_width(1.5)
            cr.stroke()
            # Solar grid lines
            cr.set_source_rgba(0.65, 0.88, 1.0, 0.65)
            cr.set_line_width(0.9)
            for gx in range(1, 3):
                cr.move_to(px + gx * 9.3, -11)
                cr.line_to(px + gx * 9.3, 11)
            cr.move_to(px, 0)
            cr.line_to(px + 28, 0)
            cr.stroke()
            cr.restore()

        # B. 3 Articulated Landing Legs with Footpads
        cr.set_line_width(3.0)
        cr.set_source_rgb(0.78, 0.84, 0.92)
        for lx_top, lx_bot, ly_bot in [(-18, -30, 36), (0, 0, 38), (18, 30, 36)]:
            cr.move_to(lx_top, 18)
            cr.line_to(lx_bot, ly_bot)
            cr.stroke()
            # Footpad disc
            self._rounded_rect(cr, lx_bot - 6, ly_bot - 2, 12, 4, 2)
            cr.set_source_rgb(0.58, 0.68, 0.82)
            cr.fill()
            cr.set_source_rgb(0.78, 0.84, 0.92)

        # C. Triple Thruster Exhaust Plumes underneath
        if thrusting:
            flick = 1.0 + 0.20 * math.sin(phase * 3.4)
            for tx_off, t_scale in [(-13, 0.78), (0, 1.05), (13, 0.78)]:
                # Outer orange/gold plume
                cr.new_path()
                cr.set_source_rgba(0.98, 0.48, 0.12, 0.92)
                cr.move_to(tx_off - 6 * t_scale, 22)
                cr.curve_to(tx_off - 8 * t_scale, 34 * flick, tx_off - 2, 46 * flick * t_scale, tx_off, 50 * flick * t_scale)
                cr.curve_to(tx_off + 2, 46 * flick * t_scale, tx_off + 8 * t_scale, 34 * flick, tx_off + 6 * t_scale, 22)
                cr.close_path()
                cr.fill()
                # Inner cyan/yellow hot core
                cr.new_path()
                cr.set_source_rgba(0.99, 0.92, 0.35, 0.96)
                cr.move_to(tx_off - 3.5 * t_scale, 22)
                cr.line_to(tx_off, 38 * flick * t_scale)
                cr.line_to(tx_off + 3.5 * t_scale, 22)
                cr.close_path()
                cr.fill()

        # D. Main Lander Capsule Hull (White/Silver or Unlockable Golden Rocket Hull!)
        gold_hull = False
        if hasattr(self.studio, "pack_mgr"):
            gold_hull = "gold_hull" in self.studio.pack_mgr.profile.get("unlocked_decorations", [])
        self._rounded_rect(cr, -24, -22, 48, 40, 12)
        pat_hull = cairo.LinearGradient(0, -22, 0, 18)
        if gold_hull:
            pat_hull.add_color_stop_rgb(0.0, 1.0, 0.92, 0.42)
            pat_hull.add_color_stop_rgb(0.68, 0.95, 0.74, 0.15)
            pat_hull.add_color_stop_rgb(0.69, 0.78, 0.48, 0.06)
            pat_hull.add_color_stop_rgb(1.0, 0.62, 0.36, 0.04)
        else:
            pat_hull.add_color_stop_rgb(0.0, 0.96, 0.98, 1.0)
            pat_hull.add_color_stop_rgb(0.68, 0.86, 0.92, 0.98)
            pat_hull.add_color_stop_rgb(0.69, 0.18, 0.68, 0.88)
            pat_hull.add_color_stop_rgb(1.0, 0.12, 0.50, 0.72)
        cr.set_source(pat_hull)
        cr.fill_preserve()
        cr.set_source_rgb(0.18, 0.28, 0.44)
        cr.set_line_width(2.0)
        cr.stroke()

        # Orange trim stripe on lower hull
        self._rounded_rect(cr, -23, 11, 46, 6, 2)
        cr.set_source_rgb(0.96, 0.54, 0.14)
        cr.fill()

        # E. "NEAT / MOON LANDER" Text Badge on Hull
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(9.5)
        cr.set_source_rgb(0.10, 0.16, 0.26)
        ext_n = cr.text_extents("NEAT")
        cr.move_to(-ext_n.width * 0.5, -5)
        cr.show_text("NEAT")

        cr.set_font_size(4.8)
        cr.set_source_rgb(0.22, 0.32, 0.48)
        ext_m = cr.text_extents("MOON LANDER")
        cr.move_to(-ext_m.width * 0.5, 2)
        cr.show_text("MOON LANDER")

        # F. Top Sensor Dome, Radar Dish & Antenna
        cr.new_path()
        cr.set_source_rgb(0.96, 0.62, 0.14)
        cr.arc(0, -22, 13, math.pi, 2 * math.pi)
        cr.fill_preserve()
        cr.set_source_rgb(0.20, 0.30, 0.45)
        cr.set_line_width(1.6)
        cr.stroke()

        # Glowing sensor dots on dome
        for sx_d in (-7, 0, 7):
            cr.new_path()
            cr.set_source_rgb(0.25, 0.92, 1.0)
            cr.arc(sx_d, -26, 2.0, 0, 2 * math.pi)
            cr.fill()

        # Center antenna mast
        cr.set_source_rgb(0.78, 0.86, 0.96)
        cr.set_line_width(2.0)
        cr.move_to(0, -35)
        cr.line_to(0, -45)
        cr.stroke()
        cr.new_path()
        cr.set_source_rgb(0.28, 0.90, 1.0)
        cr.arc(0, -46, 3.0, 0, 2 * math.pi)
        cr.fill()

        # G. Callout Leader Labels (SENSORS, SOLAR PANELS, AI ENGINE, THRUSTERS)
        cr.set_font_size(6.5)
        callouts = [
            (8, -38, 34, -44, "CAPTEURS" if is_fr else "SENSORS"),
            (46, -14, 62, -22, "PANNEAUX SOLAIRES" if is_fr else "SOLAR PANELS"),
            (24, 2, 48, 2, "MOTEUR IA" if is_fr else "AI ENGINE"),
            (18, 34, 44, 42, "PROPULSEURS" if is_fr else "THRUSTERS"),
        ]
        for x0, y0, x1, y1, lbl in callouts:
            cr.set_source_rgba(0.38, 0.78, 0.98, 0.75)
            cr.set_line_width(1.0)
            cr.move_to(x0, y0)
            cr.line_to(x1, y1)
            cr.stroke()
            cr.new_path()
            cr.arc(x0, y0, 1.8, 0, 2 * math.pi)
            cr.fill()
            cr.set_source_rgba(0.85, 0.94, 1.0, 0.90)
            cr.move_to(x1 + 3, y1 + 2)
            cr.show_text(lbl)

        cr.restore()

    def _draw_sky_neural_network(
        self,
        cr: cairo.Context,
        lander_x: float,
        lander_y: float,
        nn_cx: float,
        nn_cy: float,
        scale: float,
        phase: float,
        is_fr: bool,
    ) -> None:
        """Draws the glowing Neural Network in the right sky connected to the lander's AI Engine."""
        cr.save()
        # 1. Glowing dashed data cable from Lander AI Engine to Neural Network
        in_x = nn_cx - 52 * scale
        cr.set_source_rgba(0.25, 0.85, 0.98, 0.75)
        cr.set_line_width(1.6)
        cr.set_dash([5.0, 4.0], -phase * 8.0)
        cr.move_to(lander_x, lander_y)
        cr.curve_to(
            (lander_x + in_x) * 0.5,
            lander_y + 18 * scale,
            (lander_x + in_x) * 0.5,
            nn_cy,
            in_x,
            nn_cy,
        )
        cr.stroke()
        cr.set_dash([])

        # 2. Define 3-Layer Node Positions (Inputs: Orange, Hidden: Cyan, Outputs: White/Green)
        layer_x = [
            nn_cx - 48 * scale,
            nn_cx,
            nn_cx + 48 * scale,
        ]
        layer_counts = [4, 5, 3]
        nodes: List[List[Tuple[float, float]]] = []
        for l_idx, cnt in enumerate(layer_counts):
            col_nodes: List[Tuple[float, float]] = []
            span = (cnt - 1) * 24.0 * scale
            for i in range(cnt):
                ny = nn_cy - span * 0.5 + i * 24.0 * scale
                col_nodes.append((layer_x[l_idx], ny))
            nodes.append(col_nodes)

        # 3. Draw Glowing Synapses & Travelling Signal Pulses
        for l_idx in range(2):
            for i, (x1, y1) in enumerate(nodes[l_idx]):
                for j, (x2, y2) in enumerate(nodes[l_idx + 1]):
                    wave = 0.5 + 0.5 * math.sin(phase * 2.4 + i * 1.1 + j * 0.7 + l_idx)
                    if (i + j) % 2 == 0:
                        cr.set_source_rgba(0.98, 0.55, 0.18, 0.25 + 0.45 * wave)
                    else:
                        cr.set_source_rgba(0.20, 0.85, 0.98, 0.25 + 0.45 * wave)
                    cr.set_line_width(1.2 + 0.8 * wave)
                    cr.move_to(x1, y1)
                    cr.line_to(x2, y2)
                    cr.stroke()

                    # Animated pulse dot on active synapses
                    if (i + j + l_idx) % 3 == 0:
                        t_p = (phase * 0.65 + i * 0.23 + j * 0.17) % 1.0
                        px = x1 + (x2 - x1) * t_p
                        py = y1 + (y2 - y1) * t_p
                        cr.new_path()
                        cr.set_source_rgba(1.0, 0.95, 0.55, 0.90)
                        cr.arc(px, py, 2.2 * scale, 0, 2 * math.pi)
                        cr.fill()

        # 4. Draw Glowing Neuron Nodes
        layer_colors = [
            (0.98, 0.56, 0.16),  # Input layer: glowing orange
            (0.18, 0.86, 0.98),  # Hidden layer: glowing cyan
            (0.92, 0.98, 1.00),  # Output layer: glowing white-cyan
        ]
        for l_idx, col_nodes in enumerate(nodes):
            r_col, g_col, b_col = layer_colors[l_idx]
            for i, (nx, ny) in enumerate(col_nodes):
                pulse = 1.0 + 0.15 * math.sin(phase * 2.5 + i + l_idx)
                # Outer halo glow
                cr.new_path()
                cr.set_source_rgba(r_col, g_col, b_col, 0.28)
                cr.arc(nx, ny, 9.5 * scale * pulse, 0, 2 * math.pi)
                cr.fill()
                # Core node
                cr.new_path()
                cr.set_source_rgb(r_col, g_col, b_col)
                cr.arc(nx, ny, 5.2 * scale, 0, 2 * math.pi)
                cr.fill_preserve()
                cr.set_source_rgb(1.0, 1.0, 1.0)
                cr.set_line_width(1.2)
                cr.stroke()

        # 5. Callout labels for NEURAL NETWORK & AI BRAIN
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(max(8.5, 7.2 * scale))
        cr.set_source_rgba(0.85, 0.95, 1.0, 0.92)
        top_nx, top_ny = nodes[1][0]
        cr.move_to(top_nx + 10 * scale, top_ny - 10 * scale)
        cr.show_text("RÉSEAU NEURONAL" if is_fr else "NEURAL NETWORK")

        bot_nx, bot_ny = nodes[1][-1]
        cr.set_source_rgba(0.38, 0.88, 0.98, 0.92)
        cr.move_to(bot_nx + 10 * scale, bot_ny + 14 * scale)
        cr.show_text("CERVEAU IA" if is_fr else "AI BRAIN")
        cr.restore()

    @staticmethod
    def _draw_lunar_crater(cr: cairo.Context, cx: float, cy: float, rx: float, ry: float) -> None:
        # Outer raised rim
        cr.save()
        cr.new_path()
        cr.translate(cx, cy)
        cr.scale(rx, ry)
        cr.arc(0, 0, 1.0, 0, 2 * math.pi)
        cr.restore()
        cr.set_source_rgb(0.45, 0.68, 0.86)
        cr.fill_preserve()
        cr.set_source_rgb(0.22, 0.40, 0.58)
        cr.set_line_width(1.6)
        cr.stroke()

        # Recessed dark inner crater floor
        cr.save()
        cr.new_path()
        cr.translate(cx, cy + ry * 0.10)
        cr.scale(rx * 0.78, ry * 0.68)
        cr.arc(0, 0, 1.0, 0, 2 * math.pi)
        cr.restore()
        cr.set_source_rgb(0.16, 0.30, 0.46)
        cr.fill()

    # ==========================================================================
    # MOUSE HOVER & CLICK INTERACTION
    # ==========================================================================
    def _on_motion(self, _widget: Gtk.Widget, event: Gdk.EventMotion) -> bool:
        ex, ey = event.x, event.y
        found: Optional[str] = None
        for hid, (hx, hy, hw, hh) in self.hitboxes.items():
            if hx <= ex <= hx + hw and hy <= ey <= hy + hh:
                found = hid
                break
        if found != self.hovered_id:
            self.hovered_id = found
            self.queue_draw()
        return False

    def _switch_to_level(self, new_idx: int) -> None:
        self.view_mode = "sim"
        self.level_idx = new_idx % len(LEVEL_DATA)
        new_lid = self.cur_level["lab_id"]
        self.studio.active_lab_id = new_lid
        self.studio.lab_combo.set_active_id(new_lid)
        if hasattr(self.studio, "pack_mgr"):
            self.studio.pack_mgr.record_lab_activity(new_lid, add_run=True)
        # Apply pack-specific presets if present on this level
        presets = self.cur_level.get("presets") or self.cur_level.get("preset") or {}
        if presets:
            lab = self.studio.active_lab
            for pk, pv in presets.items():
                if pk in lab.params:
                    lab.update_param(pk, float(pv))
        self.studio._populate_examples_dropdown()
        self.studio._populate_sliders()
        self.custom_speech = None
        self.set_pet_mood("happy")
        if new_lid == "moon_lander":
            self.reset_rocket_test()
        self.queue_draw()

    def _on_button_press(self, _widget: Gtk.Widget, event: Gdk.EventButton) -> bool:
        if event.type != Gdk.EventType.BUTTON_PRESS:
            return False
        ex, ey = event.x, event.y
        clicked_id: Optional[str] = None
        # Check interactive buttons first, then sim_box last
        for hid, (hx, hy, hw, hh) in self.hitboxes.items():
            if hid == "sim_box":
                continue
            if hx <= ex <= hx + hw and hy <= ey <= hy + hh:
                clicked_id = hid
                break
        if not clicked_id and "sim_box" in self.hitboxes:
            hx, hy, hw, hh = self.hitboxes["sim_box"]
            if hx <= ex <= hx + hw and hy <= ey <= hy + hh:
                clicked_id = "sim_box"

        if not clicked_id:
            return False

        is_fr = (self.lang == "fr")
        lid = self.cur_level["lab_id"]
        lab = self.studio.active_lab
        self.last_interaction_ts = time.monotonic()
        if self.pet_mood == "sleepy":
            self.pet_mood = "happy"

        if clicked_id == "back_to_sim":
            self.view_mode = "sim"
            self.queue_draw()
            return True

        if clicked_id == "avatar_btn":
            if hasattr(self.studio, "switch_classroom_student"):
                self.studio.switch_classroom_student()
                s_nm = self.studio.pack_mgr.profile.get("player_name", "Cadet Nova")
                yr = self.studio.pack_mgr.get_current_school_year()
                yr_tag = "K" if yr == 0 else str(yr)
                self.set_pet_mood("cheering", 3.5)
                self.custom_speech = (
                    f"Salut {s_nm} (Année {yr_tag}) ! Ton profil d'élève et ton bulletin K-12 sont chargés !"
                    if is_fr
                    else f"Hi {s_nm} (Year {yr_tag})! Your personal K-12 Student Profile & Report Card are active!"
                )
            self.queue_draw()
            return True

        if clicked_id == "map_btn":
            self.view_mode = "sim" if self.view_mode == "map" else "map"
            if self.view_mode == "map":
                self.custom_speech = (
                    "Voici la Carte du Monde Synapse ! Clique sur n'importe quelle île pour voyager !"
                    if is_fr
                    else "Welcome to the Synapse World Map! Click any of the 7 AI Islands to fly right there!"
                )
            self.queue_draw()
            return True

        if clicked_id.startswith("map_zone_"):
            z_idx = int(clicked_id.split("_")[-1])
            self._switch_to_level(z_idx)
            self.set_pet_mood("cheering", 3.5)
            return True

        if clicked_id.startswith("shop_buy_"):
            item_id = clicked_id.replace("shop_buy_", "")
            if hasattr(self.studio, "pack_mgr"):
                res = self.studio.pack_mgr.buy_or_toggle_shop_item(item_id, lang=self.lang)
                self.set_pet_mood("cheering" if res.get("ok") else "thinking", 4.0)
                self.custom_speech = res.get("msg", "")
            self.queue_draw()
            return True

        if clicked_id == "teacher_mode":
            pin_locked = bool(self.studio.pack_mgr.profile.get("pin_lock_enabled", False)) if hasattr(self.studio, "pack_mgr") else False
            if pin_locked and self.view_mode != "pin":
                self.view_mode = "pin"
                self.pin_buffer = ""
                self.custom_speech = (
                    "Mode Professeur protégé par code PIN (1234) !"
                    if is_fr
                    else "Teacher Mode is PIN-protected! Enter 1234 on the keypad to unlock."
                )
                self.queue_draw()
                return True
            self.view_mode = "sim"
            self.on_switch_to_teacher()
            return True

        if clicked_id.startswith("pin_key_"):
            key = clicked_id.replace("pin_key_", "")
            expected_pin = str(self.studio.pack_mgr.profile.get("teacher_pin", "1234")) if hasattr(self.studio, "pack_mgr") else "1234"
            if key == "CLR":
                self.pin_buffer = ""
            elif key == "OK":
                if self.pin_buffer == expected_pin:
                    self.view_mode = "sim"
                    self.pin_buffer = ""
                    self.on_switch_to_teacher()
                    return True
                else:
                    self.pin_buffer = ""
                    self.set_pet_mood("dizzy", 3.0)
                    self.custom_speech = "Code PIN incorrect ! Essaie 1234." if is_fr else "Incorrect PIN! Try 1234."
            else:
                if len(self.pin_buffer) < 4:
                    self.pin_buffer += key
                if self.pin_buffer == expected_pin:
                    self.view_mode = "sim"
                    self.pin_buffer = ""
                    self.on_switch_to_teacher()
                    return True
            self.queue_draw()
            return True

        if clicked_id == "toggle_lang":
            self.lang = "en" if self.lang == "fr" else "fr"
            self.custom_speech = None
            self.queue_draw()
            return True

        if clicked_id == "prev_level":
            self._switch_to_level(self.level_idx - 1)
            return True

        if clicked_id in ("cycle_level", "synapse_kids_logo"):
            self._switch_to_level(self.level_idx + 1)
            return True

        if clicked_id.startswith("level_jump_"):
            target_idx = int(clicked_id.split("_")[-1])
            self._switch_to_level(target_idx)
            return True

        if clicked_id == "upgrade_pack":
            if hasattr(self.studio, "advance_school_year_in_gui"):
                self.studio.advance_school_year_in_gui()
                yr = self.studio.pack_mgr.get_current_school_year()
                yr_tag = "K" if yr == 0 else str(yr)
                self.custom_speech = (
                    f"Passage à l'Année {yr_tag} réussi ! Ancienne année nettoyée, notes sauvegardées !"
                    if is_fr
                    else f"Graduated & advanced to School Year {yr_tag}! Old year wiped, Report Card saved!"
                )
                self.queue_draw()
            elif hasattr(self.studio, "upgrade_learning_pack"):
                self.studio.upgrade_learning_pack()
            return True

        if clicked_id == "badges_btn":
            self.view_mode = "sim" if self.view_mode == "trophies" else "trophies"
            if self.view_mode == "trophies":
                coins_v = int(self.studio.pack_mgr.profile.get("coins", 250)) if hasattr(self.studio, "pack_mgr") else 250
                self.custom_speech = (
                    f"Bienvenue dans ta Salle des Trophées ! Tu as {coins_v} pièces ★ pour acheter des décorations !"
                    if is_fr
                    else f"Welcome to your Trophy Vault & Shop! Spend your {coins_v} Coins ★ on cool upgrades!"
                )
            self.queue_draw()
            return True

        if clicked_id == "sim_box":
            if self.view_mode != "sim":
                return True
            hx, hy, hw, hh = self.hitboxes["sim_box"]
            sub_y = hy + 34.0
            sub_h = max(80.0, hh - 34.0)
            nx = ((ex - hx) / max(1.0, hw)) * 2.0 - 1.0
            ny = ((ey - sub_y) / max(1.0, sub_h)) * 2.0 - 1.0

            if lid == "moon_lander":
                self.rocket_x = max(0.18, min(0.46, (ex - hx) / max(1.0, hw)))
                self.rocket_y = max(0.14, min(0.45, (ey - hy) / max(1.0, hh)))
                self.rocket_vy = 0.0040
                self.rocket_vx = (0.31 - self.rocket_x) * 0.015
                self.rocket_state = "flying"
                self.rocket_thrusting = True
                self.custom_speech = (
                    "Fusée relancée depuis le ciel ! Regarde le cerveau IA freiner vers la cible !"
                    if is_fr
                    else "Rocket dropped from your click! Watch the AI brain fire retro-thrusters to land!"
                )
            elif lid == "raycast_car":
                for car in getattr(lab, "cars", []):
                    if car.alive:
                        car.speed = lab.params.get("max_speed", 5.5)
                self.custom_speech = (
                    "Turbo Nitro activé ! Toutes les voitures accélèrent avec leurs lasers Lidar !"
                    if is_fr
                    else "Nitro Turbo boost! Watch the Cyber Racecars zoom around the corner with Lidar lasers!"
                )
            elif lid == "rl_gridworld":
                col = max(0, min(lab.cols - 1, int(((ex - hx) / max(1.0, hw)) * lab.cols)))
                row = max(0, min(lab.rows - 1, int(((ey - sub_y) / max(1.0, sub_h)) * lab.rows)))
                cell = (col, row)
                if cell not in (lab.start_pos, lab.goal_pos) and cell not in lab.wall_cells:
                    if cell in lab.lava_cells:
                        lab.lava_cells.remove(cell)
                        action_en, action_fr = "removed a Lava tile", "enlevé une case de lave"
                    else:
                        lab.lava_cells.add(cell)
                        action_en, action_fr = "placed a new Red Lava trap", "placé un piège de lave rouge"
                    lab.fast_forward_generations(15)
                    self.custom_speech = (
                        f"Tu as {action_fr} en ({col},{row}) ! Regarde le robot calculer un nouveau chemin !"
                        if is_fr
                        else f"You {action_en} at ({col},{row})! Watch the robot learn a new safe path around it!"
                    )
            elif lid == "cartpole_rl":
                push = 1.35 if nx >= 0.0 else -1.35
                for ag in getattr(lab, "agents", []):
                    if ag.alive:
                        ag.v_theta += push
                self.custom_speech = (
                    "Hop ! Tu as poussé le bâton doré ! Regarde le chariot IA sprinter pour le rattraper !"
                    if is_fr
                    else "Boing! You nudged the Golden Pole! Watch the AI cart sprint to catch and balance it!"
                )
            elif lid == "nn_playground" and hasattr(lab, "add_interactive_dots"):
                self._next_dot_label = 0.0 if getattr(self, "_next_dot_label", 0.0) > 0.5 else 1.0
                color_en = "BLUE" if self._next_dot_label > 0.5 else "RED"
                color_fr = "BLEUS" if self._next_dot_label > 0.5 else "ROUGES"
                lab.add_interactive_dots(nx, ny, label=self._next_dot_label, count=7)
                self.custom_speech = (
                    f"Hop ! Tu as ajouté des points {color_fr} ! Regarde la frontière dorée s'adapter en direct !"
                    if is_fr
                    else f"Pop! You dropped new {color_en} dots! Watch the golden AI boundary curve around them!"
                )
            elif lid == "swarm_ecosystem" and hasattr(lab, "drop_food_cluster"):
                gx = ((ex - hx) / max(1.0, hw)) * lab.width
                gy = ((ey - sub_y) / max(1.0, sub_h)) * lab.height
                lab.drop_food_cluster(gx, gy, count=6)
                self.custom_speech = (
                    "Miam ! Tu as lâché 6 perles d'énergie dorées ! Regarde l'essaim vert nager vers ton clic !"
                    if is_fr
                    else "Yum! You dropped 6 Golden Energy Orbs! Watch the green swimmer flock rush to eat them!"
                )
            elif lid == "prime_attention":
                gaps = [64.0, 128.0, 256.0, 512.0]
                cur_g = lab.params.get("distractor_gap", 256.0)
                next_g = gaps[(gaps.index(cur_g) + 1) % len(gaps)] if cur_g in gaps else 128.0
                lab.update_param("distractor_gap", next_g)
                lab.fast_forward_generations(5)
                self.studio._populate_sliders()
                self.custom_speech = (
                    f"Test à {int(next_g)} mots de distance ! Le Coffre Doré PRIME garde la clé secrète en mémoire !"
                    if is_fr
                    else f"Testing passkey recall across {int(next_g)} words! Notice how the Golden PRIME Vault still remembers!"
                )
            self.queue_draw()
            return True

        if clicked_id == "btn_smarter":
            self.smart_boost += 1
            self.stars_score = 3
            self.obj1_done = True
            self.obj2_done = True
            self.set_pet_mood("cheering", 4.0)
            if hasattr(self.studio, "pack_mgr"):
                self.studio.pack_mgr.record_daily_progress("dm_boost")
            if hasattr(self.studio, "award_kid_level_trophy"):
                self.studio.award_kid_level_trophy(self.cur_level.get("level", 1))
            if lid == "nn_playground":
                cur_n = int(round(lab.params.get("hidden_neurons", 8.0)))
                new_n = 4 if cur_n >= 16 else min(16, cur_n + 4)
                lab.update_param("hidden_neurons", float(new_n))
                lab.fast_forward_generations(20)
                self.custom_speech = (
                    f"Cerveau agrandi à {new_n} neurones ! La frontière dorée courbe autour des formes complexes !"
                    if is_fr
                    else f"Brain upgraded to {new_n} Hidden Neurons! Watch the golden boundary curve tightly around every dot!"
                )
            elif lid == "rl_gridworld":
                lab.update_param("gamma", 0.98)
                lab.fast_forward_generations(35)
                self.custom_speech = (
                    "35 explorations terminées ! Suis les flèches dorées : le robot connaît le chemin parfait !"
                    if is_fr
                    else "Trained 35 maze runs! Look at the golden arrows — your robot mapped the shortest path to the treasure!"
                )
            elif lid == "swarm_ecosystem":
                cur_p = int(round(lab.params.get("num_prey", 35.0)))
                new_p = 25 if cur_p >= 65 else min(70, cur_p + 10)
                lab.update_param("num_prey", float(new_p))
                lab.fast_forward_generations(8)
                self.custom_speech = (
                    f"Essaim renforcé à {new_p} nageurs intelligents ! Ils esquivent les requins rouges en équipe !"
                    if is_fr
                    else f"Flock upgraded to {new_p} smart swimmers! Watch them team up and dodge the red sharks!"
                )
            elif lid == "prime_attention":
                cur_h = int(round(lab.params.get("num_heads", 8.0)))
                new_h = 8 if cur_h >= 24 else min(24, cur_h + 4)
                lab.update_param("num_heads", float(new_h))
                lab.fast_forward_generations(8)
                self.custom_speech = (
                    f"Coffre PRIME amélioré avec {new_h} têtes d'attention ! La mémoire longue distance grimpe !"
                    if is_fr
                    else f"Upgraded PRIME Vault to {new_h} Attention Heads! Watch the green recall bar climb higher!"
                )
            else:
                lab.fast_forward_generations(15)
                if hasattr(lab, "modify_brain_structure"):
                    lab.modify_brain_structure(delta_neurons=1, delta_synapses=2)
                self.custom_speech = (
                    "Super ! Le cerveau de l'IA a gagné de nouveaux neurones et 15 générations d'entraînement !"
                    if is_fr
                    else "Awesome! Your AI brain just grew new neurons and practiced 15 generations!"
                )
                if lid == "moon_lander":
                    self.reset_rocket_test()
            self.studio._populate_sliders()
            self.queue_draw()
            return True

        if clicked_id == "btn_fuel":
            self.fuel_boost = True
            self.stars_score = 3
            self.obj1_done = True
            self.obj2_done = True
            self.set_pet_mood("cheering", 3.5)
            if hasattr(self.studio, "pack_mgr"):
                self.studio.pack_mgr.record_daily_progress("dm_boost")
            if hasattr(self.studio, "award_kid_level_trophy"):
                self.studio.award_kid_level_trophy(self.cur_level.get("level", 1))
            if lid == "nn_playground":
                cur_ds = int(round(lab.params.get("dataset_id", 3.0)))
                next_ds = (cur_ds + 1) % 4
                names_en = ["XOR Quadrants", "Concentric Rings", "Two Moons", "Twin Spiral"]
                names_fr = ["Quadrants XOR", "Anneaux Concentriques", "Deux Lunes", "Double Spirale"]
                lab.update_param("dataset_id", float(next_ds))
                lab.update_param("learning_rate", 0.14)
                lab.fast_forward_generations(12)
                self.custom_speech = (
                    f"Nouvelle forme : {names_fr[next_ds]} ! Regarde le cerveau trier les couleurs en direct !"
                    if is_fr
                    else f"Switched pattern to {names_en[next_ds]}! Watch the AI brain re-carve the color boundary live!"
                )
            elif lid == "moon_lander":
                lab.update_param("thruster_power", 2.2)
                lab.update_param("fuel_capacity", 220.0)
                self.reset_rocket_test()
                self.custom_speech = (
                    "Plein de carburant ajouté ! Les moteurs de la fusée sont maintenant super puissants !"
                    if is_fr
                    else "Extra fuel added! Your rocket thrusters are now super strong for a soft landing!"
                )
            elif lid == "raycast_car":
                cur_r = lab.params.get("sensor_range", 125.0)
                new_r = 110.0 if cur_r >= 200.0 else min(220.0, cur_r + 45.0)
                lab.update_param("sensor_range", new_r)
                lab.update_param("track_width", 46.0)
                self.custom_speech = (
                    f"Lasers Lidar poussés à {int(new_r)} px ! La voiture voit les virages de très loin !"
                    if is_fr
                    else f"Lidar lasers boosted to {int(new_r)} px! Now the racecar sees corners way ahead!"
                )
            elif lid == "rl_gridworld":
                lab.update_param("alpha", 0.65)
                lab.update_param("goal_reward", 220.0)
                lab.fast_forward_generations(25)
                self.custom_speech = (
                    "Mémoire rapide activée (α=0.65) ! Le robot apprend deux fois plus vite à chaque essai !"
                    if is_fr
                    else "Fast Memory activated (α=0.65)! Your robot updates its map twice as fast on every step!"
                )
            elif lid == "cartpole_rl":
                cur_f = lab.params.get("force_mag", 11.0)
                new_f = 10.0 if cur_f >= 21.0 else min(24.0, cur_f + 5.0)
                lab.update_param("force_mag", new_f)
                for ag in getattr(lab, "agents", []):
                    if ag.alive:
                        ag.v_theta += 0.9
                self.custom_speech = (
                    f"Moteurs poussés à {int(new_f)} N ! Le chariot rattrape le bâton à toute vitesse !"
                    if is_fr
                    else f"Motors boosted to {int(new_f)} Newtons! Watch the cart snap the pole right back to center!"
                )
            elif lid == "swarm_ecosystem":
                cur_fd = int(round(lab.params.get("food_count", 28.0)))
                new_fd = 25 if cur_fd >= 55 else min(60, cur_fd + 15)
                lab.update_param("food_count", float(new_fd))
                self.custom_speech = (
                    f"Pluie de nourriture ! Il y a maintenant {new_fd} perles d'énergie dorées dans l'océan !"
                    if is_fr
                    else f"Food shower! There are now {new_fd} glowing Golden Energy Orbs for your flock to eat!"
                )
            elif lid == "prime_attention":
                wins = [32.0, 64.0, 128.0, 256.0]
                cur_w = lab.params.get("window_size", 64.0)
                new_w = wins[(wins.index(cur_w) + 1) % len(wins)] if cur_w in wins else 128.0
                lab.update_param("window_size", new_w)
                lab.fast_forward_generations(5)
                self.custom_speech = (
                    f"Fenêtre glissante réglée sur W={int(new_w)} mots ! Regarde la courbe bleue et verte bouger !"
                    if is_fr
                    else f"Sliding Window changed to W={int(new_w)} words! Watch the Blue and Green recall curves shift!"
                )
            self.studio._populate_sliders()
            self.queue_draw()
            return True

        if clicked_id == "btn_gravity":
            self.light_grav = not self.light_grav if lid in ("nn_playground", "raycast_car", "prime_attention") else True
            self.stars_score = 3
            self.obj1_done = True
            self.obj2_done = True
            if lid == "nn_playground":
                cur_noise = lab.params.get("noise", 0.08)
                new_noise = 0.22 if cur_noise < 0.12 else 0.03
                lab.update_param("noise", new_noise)
                if new_noise > 0.12:
                    self.custom_speech = (
                        "Points mélangés ! Les points rouges et bleus bougent partout — regarde l'IA s'adapter !"
                        if is_fr
                        else "Dots scrambled! The blue and red dots are extra wild now — watch the AI boundary chase them!"
                    )
                else:
                    self.custom_speech = (
                        "Points bien rangés ! Le trieur de couleurs atteint presque 100% de précision !"
                        if is_fr
                        else "Clean dots activated! Now the Color Sorter brain can reach nearly 100% accuracy!"
                    )
            elif lid == "moon_lander":
                lab.update_param("gravity", 0.85)
                self.reset_rocket_test()
                self.custom_speech = (
                    "Gravité lunaire activée ! La fusée flotte tout doucement vers la zone d'alunissage !"
                    if is_fr
                    else "Light Moon Gravity activated! Watch the lander float gently down onto the landing pad!"
                )
            elif lid == "raycast_car":
                cur_s = lab.params.get("max_speed", 4.5)
                new_s = 3.5 if cur_s > 5.0 else 6.8
                lab.update_param("max_speed", new_s)
                lab.update_param("turn_rate", 0.12)
                self.custom_speech = (
                    f"Vitesse réglée à {new_s:.1f} ! Les voitures prennent les virages avec une agilité maximale !"
                    if is_fr
                    else f"Car speed set to {new_s:.1f} with high steering agility! Watch them carve the circuit!"
                )
            elif lid == "rl_gridworld":
                lab.update_param("epsilon", 0.02)
                lab.update_param("wind_prob", 0.0)
                lab.fast_forward_generations(15)
                self.custom_speech = (
                    "Fini le hasard (ε=0.02) ! Le robot suit directement les flèches dorées jusqu'au trésor !"
                    if is_fr
                    else "Zero-slip precision mode (ε=0.02)! The robot now marches straight along the golden arrows to the treasure!"
                )
            elif lid == "cartpole_rl":
                lab.update_param("gravity", 3.2)
                lab.update_param("wind_gust", 0.35)
                for ag in getattr(lab, "agents", []):
                    if ag.alive:
                        ag.v_theta -= 0.85
                self.custom_speech = (
                    "Gravité lunaire activée (3.2 m/s²) ! Le bâton doré flotte au ralenti !"
                    if is_fr
                    else "Moon Gravity (3.2 m/s²) activated! The Golden Pole moves in gentle slow-motion!"
                )
            elif lid == "swarm_ecosystem":
                lab.update_param("prey_speed", 6.2)
                lab.update_param("vision_radius", 135.0)
                lab.update_param("predator_speed", 3.0)
                self.custom_speech = (
                    "Super vitesse activée ! Les nageurs verts sont maintenant bien plus rapides que les requins !"
                    if is_fr
                    else "Swimmer Speed Boost! Your green flock now swims at 6.2x speed and easily outruns the sharks!"
                )
            elif lid == "prime_attention":
                cur_qk = int(round(lab.params.get("use_qk_norm", 1.0)))
                new_qk = 0.0 if cur_qk >= 1 else 1.0
                lab.update_param("use_qk_norm", new_qk)
                lab.update_param("decay", 0.9995)
                lab.update_param("alpha", 0.25)
                if new_qk >= 1.0:
                    self.custom_speech = (
                        "Super Focus QK-Norm ACTIVÉ ! Le Coffre PRIME bloque le bruit et garde ~95% de précision !"
                        if is_fr
                        else "Sharp Focus (QK-Norm ON)! The Golden PRIME Vault blocks distractor noise for ~95% recall!"
                    )
                else:
                    self.custom_speech = (
                        "QK-Norm DÉSACTIVÉ ! Regarde la barre verte chuter à cause du rebond parabolique Taylor !"
                        if is_fr
                        else "QK-Norm turned OFF! Notice how the green recall bar drops from Taylor polynomial rebound!"
                    )
            self.studio._populate_sliders()
            self.queue_draw()
            return True

        if clicked_id == "btn_relaunch":
            self.view_mode = "sim"
            if hasattr(self.studio, "pack_mgr"):
                self.studio.pack_mgr.record_daily_progress("dm_run_lab")
                self.studio.pack_mgr.record_lab_activity(lid, add_run=True)
            if lid == "nn_playground":
                lab.reset_weights()
                lab.rebuild_dataset()
                self.custom_speech = (
                    "Cerveau remis à zéro (Époque 0) ! Regarde la frontière dorée se former sous tes yeux !"
                    if is_fr
                    else "Brain reset to Epoch 0! Watch the golden decision boundary learn from scratch right now!"
                )
            elif lid == "moon_lander":
                self.reset_rocket_test()
                self.custom_speech = (
                    "3... 2... 1... Mise à feu ! Regarde la fusée descendre et se poser sur la Lune !"
                    if is_fr
                    else "3... 2... 1... Liftoff! Watch your AI rocket descend and touch down on the Lunar Pad!"
                )
            else:
                self.studio._on_reset_lab(None)
                if lid == "cartpole_rl":
                    for ag in getattr(self.studio.active_lab, "agents", []):
                        ag.v_theta += 0.95
                self.custom_speech = (
                    "Simulation relancée ! Regarde l'IA passer le test en direct !"
                    if is_fr
                    else "Simulation relaunched! Watch your AI run a fresh live test!"
                )
            self.queue_draw()
            return True

        if clicked_id == "ask_robot" and not self.asking_ai:
            # First read the current speech bubble aloud for early readers (K-2)
            cur_bubble = self.custom_speech or (
                self.cur_level["speech_fr"] if is_fr else self.cur_level["speech_en"]
            )
            if hasattr(self.studio, "read_aloud_lesson"):
                self.studio.lang = self.lang
                self.studio.read_aloud_lesson(text_override=cur_bubble)

            self.asking_ai = True
            self.set_pet_mood("thinking", 5.0)
            if hasattr(self.studio, "pack_mgr"):
                self.studio.pack_mgr.record_daily_progress("dm_ask_lumi")
            self.custom_speech = (
                "♪ Lumi lit à voix haute et réfléchit à un indice Socratique..."
                if is_fr
                else "♪ Lumi is reading aloud & thinking up a Socratic hint..."
            )
            self.queue_draw()

            def worker():
                prompt = (
                    f"Tu es Lumi, un petit robot compagnon Socratique. Donne un indice court et pose une question amusante (1 phrase pour un enfant de 9 ans) sur : {self.cur_level['title_fr']}"
                    if is_fr
                    else f"You are Lumi, a friendly Socratic robot companion. Give one short hint and a guiding question (1 sentence for a 9-year-old) about: {self.cur_level['title_en']}!"
                )
                res = self.studio.cortex.chat_with_cortex(prompt, history=[])
                reply = res.get("reply", "").strip()
                if len(reply) > 135:
                    reply = reply[:132] + "..."
                self.custom_speech = reply
                self.asking_ai = False
                self.set_pet_mood("cheering", 4.0)
                GLib.idle_add(self.queue_draw)

            threading.Thread(target=worker, daemon=True).start()
            return True

        return False

