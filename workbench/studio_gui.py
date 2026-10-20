#!/usr/bin/env python3
"""
Synapse Studio: Potato-Grade Point-and-Click AI Experimentation & Classroom Workbench
Built with native Linux GTK3 + Cairo (<25 MB RAM, 60 FPS, zero Electron bloat).

Features:
  - 6 Interactive Real-Time AI Labs (NEAT Moon Lander, Lidar Car, RL GridWorld, CartPole, MLP Backprop, Swarm)
  - 10 Follow-Along School Tutorials & Gamified Mission Badges (`curriculum.py`)
  - Editable Hands-On Python Coding Sandbox with Safe Subprocess Runner & Kid-Friendly Hints (`sandbox_runner.py`)
  - Live Neural Topology Visualizer & Built-in `Cortex-Phi3` AI Tutor
"""

import os
import sys
import math
import time
import threading
from typing import Dict, Any, List, Set, Tuple, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib
import cairo

from workbench.labs.moon_lander import NEATMoonLanderLab
from workbench.labs.raycast_car import NEATRaycastCarLab
from workbench.labs.rl_gridworld import RLGridWorldLab
from workbench.labs.cartpole_rl import CartPoleLab
from workbench.labs.nn_playground import NeuralPlaygroundLab
from workbench.labs.swarm_ecosystem import SwarmEcosystemLab
from workbench.labs.prime_attention_lab import PrimeAttentionLab
from workbench.code_generator import generate_lab_python_code
from workbench.curriculum import (
    SCHOOL_CURRICULUM,
    LAB_EXAMPLES,
    get_examples_for_lab,
    get_lesson_by_id,
    verify_lesson_goal,
)
from workbench.sandbox_runner import run_student_code
from workbench.kid_arcade_view import SynapseKidsView
from cortex.engine import CortexEngine


DARK_CSS = b"""
window {
    background-color: #0f1117;
    color: #e2e8f0;
}
frame, notebook, scrolledwindow {
    background-color: #161922;
    color: #e2e8f0;
    border-color: #262b38;
}
label {
    color: #e2e8f0;
}
button {
    background-image: none;
    background-color: #212634;
    color: #e2e8f0;
    border: 1px solid #333b4f;
    border-radius: 4px;
    padding: 4px 8px;
}
button:hover {
    background-color: #2d3548;
}
button.kid-btn-play {
    background-color: #15803d;
    color: #ffffff;
    font-weight: bold;
    border: 2px solid #4ade80;
    border-radius: 7px;
    padding: 7px 10px;
}
button.kid-btn-play:hover {
    background-color: #16a34a;
}
button.kid-btn-turbo {
    background-color: #b45309;
    color: #ffffff;
    font-weight: bold;
    border: 2px solid #facc15;
    border-radius: 7px;
    padding: 8px 10px;
}
button.kid-btn-turbo:hover {
    background-color: #d97706;
}
button.kid-btn-brain {
    background-color: #0369a1;
    color: #ffffff;
    font-weight: bold;
    border: 2px solid #38bdf8;
    border-radius: 7px;
    padding: 6px 8px;
}
button.kid-btn-brain:hover {
    background-color: #0284c7;
}
button.kid-btn-unlock {
    background-color: #5b21b6;
    color: #ffffff;
    font-weight: bold;
    border: 2px solid #c084fc;
    border-radius: 7px;
    padding: 6px 10px;
}
button.kid-btn-unlock:hover {
    background-color: #6d28d9;
}
button.mode-active-kid {
    background-color: #15803d;
    color: #fef08a;
    font-weight: bold;
    border: 2px solid #4ade80;
    border-radius: 6px;
}
button.mode-active-pro {
    background-color: #0369a1;
    color: #ffffff;
    font-weight: bold;
    border: 2px solid #38bdf8;
    border-radius: 6px;
}
menu, .menu, .popup, combobox window, combobox menu {
    background-color: #161922;
    color: #f8fafc;
    border: 1px solid #38bdf8;
}
menuitem, .menuitem, cellview {
    background-color: #161922;
    color: #f8fafc;
    padding: 4px 8px;
}
menuitem:hover, .menuitem:hover, menuitem:selected {
    background-color: #0284c7;
    color: #ffffff;
}
notebook, notebook stack {
    background-color: #0e1017;
    color: #f8fafc;
}
notebook header, notebook tab {
    background-color: #161922;
    color: #94a3b8;
    padding: 4px 8px;
    border: 1px solid #262b38;
}
notebook tab:checked {
    background-color: #1e293b;
    color: #38bdf8;
}
notebook tab label {
    color: #f8fafc;
    font-weight: bold;
}
entry, textview, textview text {
    background-color: #12151e;
    color: #a5f3fc;
    font-family: monospace;
}
popover, popover.background {
    background-color: #161922;
    color: #f8fafc;
    border: 1px solid #38bdf8;
    padding: 4px;
}
"""


class SynapseDropdown(Gtk.Button):
    """Downward-opening Popover dropdown that never shrinks or clips near the top of the screen."""

    def __init__(self) -> None:
        super().__init__()
        self._items: List[Tuple[str, str]] = []
        self._active_id: Optional[str] = None
        self._callbacks: List[Any] = []

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self._label = Gtk.Label(label="")
        self._label.set_xalign(0.0)
        arrow_lbl = Gtk.Label(label="▾")
        hbox.pack_start(self._label, True, True, 2)
        hbox.pack_end(arrow_lbl, False, False, 2)
        self.add(hbox)

        self._popover = Gtk.Popover.new(self)
        self._popover.set_position(Gtk.PositionType.BOTTOM)
        self._popover.set_constrain_to(Gtk.PopoverConstraint.NONE)
        self._vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self._vbox.set_margin_top(4)
        self._vbox.set_margin_bottom(4)
        self._vbox.set_margin_start(4)
        self._vbox.set_margin_end(4)
        self._popover.add(self._vbox)
        super().connect("clicked", self._on_self_clicked)

    def _on_self_clicked(self, _btn: Gtk.Button) -> None:
        self._vbox.show_all()
        self._popover.popup()

    def clear(self) -> None:
        self._items.clear()
        self._active_id = None
        self._label.set_text("")
        for child in self._vbox.get_children():
            self._vbox.remove(child)

    def append(self, item_id: str, text: str) -> None:
        self._items.append((item_id, text))
        btn = Gtk.Button()
        lbl = Gtk.Label(label=text)
        lbl.set_xalign(0.0)
        btn.add(lbl)
        btn.connect("clicked", self._on_item_clicked, item_id)
        self._vbox.pack_start(btn, False, False, 0)
        self._vbox.show_all()
        if self._active_id is None:
            self.set_active_id(item_id)

    def _on_item_clicked(self, _btn: Gtk.Button, item_id: str) -> None:
        self._popover.popdown()
        self.set_active_id(item_id)
        for cb in self._callbacks:
            cb(self)

    def set_active_id(self, item_id: str) -> None:
        for iid, txt in self._items:
            if iid == item_id:
                self._active_id = iid
                self._label.set_text(txt)
                break

    def get_active_id(self) -> Optional[str]:
        return self._active_id

    def get_active_text(self) -> str:
        for iid, txt in self._items:
            if iid == self._active_id:
                return txt
        return ""

    def connect(self, signal_name: str, callback: Any, *args: Any) -> Any:
        if signal_name == "changed":
            self._callbacks.append(callback)
            return len(self._callbacks)
        return super().connect(signal_name, callback, *args)


class SynapseStudioWindow(Gtk.Window):
    LAB_CATALOG = [
        ("moon_lander", "★ 1. NEAT Rocket Moon Lander (Neuroevolution)"),
        ("raycast_car", "◈ 2. NEAT Self-Driving Lidar Car (Autonomous)"),
        ("rl_gridworld", "❖ 3. RL Hazard GridWorld (Q-Learning / SARSA)"),
        ("cartpole_rl", "⚖ 4. CartPole Inverted Pendulum (Neuro-Control)"),
        ("nn_playground", "⚙ 5. Neural Network Backprop (2D Decision Boundaries)"),
        ("swarm_ecosystem", "✦ 6. Predator-Prey Swarm (Co-Evolutionary Boids)"),
        ("prime_attention", "⚡ 7. PRIME Moment Sliding-Window Attention (O(1) Vault)"),
    ]

    def __init__(self):
        super().__init__(title="Synapse Studio — Point & Click AI Lab & School Academy (Potato-Grade)")
        self.set_default_size(1260, 760)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.maximize()

        provider = Gtk.CssProvider()
        provider.load_from_data(DARK_CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.cortex = CortexEngine()
        self.labs: Dict[str, Any] = {
            "moon_lander": NEATMoonLanderLab(),
            "raycast_car": NEATRaycastCarLab(),
            "rl_gridworld": RLGridWorldLab(),
            "cartpole_rl": CartPoleLab(),
            "nn_playground": NeuralPlaygroundLab(),
            "swarm_ecosystem": SwarmEcosystemLab(),
            "prime_attention": PrimeAttentionLab(),
        }
        self.active_lab_id = "moon_lander"
        self.active_lesson_id = SCHOOL_CURRICULUM[0]["id"]
        self.earned_badges: Set[str] = set()
        self.running = True
        self.user_mode = "school"
        self.kid_mode: bool = True
        self.kid_unlocked_sliders: int = 2
        self.slider_widgets: Dict[str, Gtk.Scale] = {}
        self._updating_sliders = False
        self.chat_history: List[Tuple[str, str]] = []

        # Live performance metrics tracking
        self._tick_count = 0
        self._last_fps_time = time.perf_counter()
        self.live_fps = 55.0
        self.last_step_ms = 0.35
        self.ram_used_mb = 420
        self.ram_total_mb = 16000
        self._anim_phase = 0.0

        self._build_ui()
        self._populate_examples_dropdown()
        self._populate_sliders()
        self._refresh_lesson_view()
        self._load_lesson_coding_challenge()

        GLib.timeout_add(18, self._on_tick)

    @property
    def active_lab(self) -> Any:
        return self.labs[self.active_lab_id]

    def _build_ui(self) -> None:
        self.mode_stack = Gtk.Stack()
        self.mode_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.mode_stack.set_transition_duration(180)
        self.add(self.mode_stack)

        # PAGE 1: Full-Screen "Synapse Kids" Interactive Arcade View
        self.kids_view = SynapseKidsView(
            self,
            on_switch_to_teacher=lambda: self._set_kid_mode(False),
        )
        self.mode_stack.add_named(self.kids_view, "kid")

        # PAGE 2: Full 3-Column "Teacher / Pro Workstation" View
        root_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        root_vbox.set_margin_top(4)
        root_vbox.set_margin_bottom(4)
        root_vbox.set_margin_start(5)
        root_vbox.set_margin_end(5)
        self.mode_stack.add_named(root_vbox, "pro")

        # --- TOP HEADER BAR (Fits comfortably within 1260px) ---
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        root_vbox.pack_start(header_box, False, False, 0)

        self.title_lbl = Gtk.Label()
        self.title_lbl.set_markup("<b><span foreground='#38bdf8'>⚡ SYNAPSE STUDIO</span></b>")
        header_box.pack_start(self.title_lbl, False, False, 2)

        self.lab_combo = SynapseDropdown()
        for lid, lname in self.LAB_CATALOG:
            self.lab_combo.append(lid, lname)
        self.lab_combo.set_active_id(self.active_lab_id)
        self.lab_combo.connect("changed", self._on_lab_changed)
        header_box.pack_start(self.lab_combo, False, False, 2)

        # Web Browser Launch Button
        self.btn_browser = Gtk.Button(label="◈ Web Browser")
        self.btn_browser.set_tooltip_text("Open Internet Web Browser (Firefox ESR / NetSurf)")
        self.btn_browser.connect("clicked", self._on_open_browser)
        header_box.pack_start(self.btn_browser, False, False, 2)

        # Secure Remote HTTPS Tunnel Button
        self.btn_tunnel = Gtk.Button(label="❖ Tunnel")
        self.btn_tunnel.set_tooltip_text("Show or start encrypted HTTPS Remote Browser Tunnel (Cloudflare + noVNC)")
        self.btn_tunnel.connect("clicked", self._on_show_tunnel)
        header_box.pack_start(self.btn_tunnel, False, False, 2)

        # Badge Status Pill
        self.badge_lbl = Gtk.Label()
        self._update_badge_header()
        header_box.pack_start(self.badge_lbl, False, False, 4)

        # KID MODE vs TEACHER / PRO MODE PROMINENT TOGGLE SWITCHER
        mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        header_box.pack_end(mode_box, False, False, 2)

        self.btn_kid_mode = Gtk.Button(label="★ Synapse Kids")
        self.btn_kid_mode.set_tooltip_text("Switch to full-screen Synapse Kids mode!")
        self.btn_kid_mode.connect("clicked", lambda _b: self._set_kid_mode(True))
        mode_box.pack_start(self.btn_kid_mode, False, False, 1)

        self.btn_pro_mode = Gtk.Button(label="⚙ Mode Professeur / Teacher")
        self.btn_pro_mode.set_tooltip_text("Full Engineering & Classroom Workstation: all sliders, TTFT/RAM telemetry, Python code & Linux runner!")
        self.btn_pro_mode.connect("clicked", lambda _b: self._set_kid_mode(False))
        mode_box.pack_start(self.btn_pro_mode, False, False, 1)

        # --- MAIN WORKSPACE 3-COLUMN SPLIT (245 + 420 + 360 = 1025px < 1280px) ---
        main_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        root_vbox.pack_start(main_hbox, True, True, 0)

        # COLUMN 1: 5 Lab Examples + Direct Brain Surgery + Variable Sliders
        self.left_frame = Gtk.Frame(label=" ★ 1. Game Controls & Unlocked Sliders ")
        self.left_frame.set_size_request(245, -1)
        main_hbox.pack_start(self.left_frame, False, False, 0)

        left_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        left_vbox.set_margin_top(4)
        left_vbox.set_margin_bottom(4)
        left_vbox.set_margin_start(5)
        left_vbox.set_margin_end(5)
        self.left_frame.add(left_vbox)

        # 5 Examples per Lab Selector
        self.ex_lbl = Gtk.Label()
        self.ex_lbl.set_xalign(0.0)
        self.ex_lbl.set_markup("<b><span size='small' foreground='#facc15'>★ Pick a Fun Game Preset:</span></b>")
        left_vbox.pack_start(self.ex_lbl, False, False, 0)

        self.example_combo = SynapseDropdown()
        self.example_combo.connect("changed", self._on_example_selected)
        left_vbox.pack_start(self.example_combo, False, False, 0)

        ctrl_grid = Gtk.Grid()
        ctrl_grid.set_column_spacing(3)
        ctrl_grid.set_row_spacing(4)
        left_vbox.pack_start(ctrl_grid, False, False, 0)

        self.btn_run = Gtk.Button(label="|| PAUSE GAME")
        self.btn_run.set_hexpand(True)
        self.btn_run.connect("clicked", self._on_toggle_run)
        ctrl_grid.attach(self.btn_run, 0, 0, 1, 1)

        self.btn_step = Gtk.Button(label=">| Step 1")
        self.btn_step.connect("clicked", self._on_step_once)
        ctrl_grid.attach(self.btn_step, 1, 0, 1, 1)

        self.btn_turbo = Gtk.Button(label="⚡ SUPER TRAIN AI (+25 TRIES!)")
        self.btn_turbo.set_hexpand(True)
        self.btn_turbo.connect("clicked", self._on_turbo_evolve)
        ctrl_grid.attach(self.btn_turbo, 0, 1, 2, 1)

        self.btn_reset = Gtk.Button(label="↻ Start Over")
        self.btn_reset.set_hexpand(True)
        self.btn_reset.connect("clicked", self._on_reset_lab)
        ctrl_grid.attach(self.btn_reset, 0, 2, 1, 1)

        self.btn_export = Gtk.Button(label="✎ Export .py")
        self.btn_export.connect("clicked", self._on_export_py)
        ctrl_grid.attach(self.btn_export, 1, 2, 1, 1)

        # Direct Structural Brain Surgery Buttons (+ / - Neurons & Synapses)
        self.surg_lbl = Gtk.Label()
        self.surg_lbl.set_xalign(0.0)
        self.surg_lbl.set_markup("<b><span size='small' foreground='#38bdf8'>★ Grow or Shrink AI Brain:</span></b>")
        left_vbox.pack_start(self.surg_lbl, False, False, 0)

        surg_grid = Gtk.Grid()
        surg_grid.set_column_spacing(3)
        surg_grid.set_row_spacing(3)
        left_vbox.pack_start(surg_grid, False, False, 0)

        self.btn_add_neuron = Gtk.Button(label="+ Grow Brain")
        self.btn_add_neuron.set_hexpand(True)
        self.btn_add_neuron.connect("clicked", self._on_brain_surgery, 1, 0)
        surg_grid.attach(self.btn_add_neuron, 0, 0, 1, 1)

        self.btn_sub_neuron = Gtk.Button(label="- Shrink")
        self.btn_sub_neuron.set_hexpand(True)
        self.btn_sub_neuron.connect("clicked", self._on_brain_surgery, -1, 0)
        surg_grid.attach(self.btn_sub_neuron, 1, 0, 1, 1)

        self.btn_add_syn = Gtk.Button(label="+ Add Synapse")
        self.btn_add_syn.connect("clicked", self._on_brain_surgery, 0, 2)
        surg_grid.attach(self.btn_add_syn, 0, 1, 1, 1)

        self.btn_sub_syn = Gtk.Button(label="- Prune Wire")
        self.btn_sub_syn.connect("clicked", self._on_brain_surgery, 0, -2)
        surg_grid.attach(self.btn_sub_syn, 1, 1, 1, 1)

        slider_scroll = Gtk.ScrolledWindow()
        slider_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        left_vbox.pack_start(slider_scroll, True, True, 0)

        self.sliders_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        slider_scroll.add(self.sliders_vbox)

        # COLUMN 2: 60 FPS Live Physics & Agent Viewport + Performance Telemetry Bar
        self.center_frame = Gtk.Frame(label=" ★ 2. Live AI Game Arena (60 FPS) ")
        main_hbox.pack_start(self.center_frame, True, True, 0)

        center_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.center_frame.add(center_vbox)

        self.telemetry_lbl = Gtk.Label()
        self.telemetry_lbl.set_xalign(0.01)
        self.telemetry_lbl.set_line_wrap(True)
        center_vbox.pack_start(self.telemetry_lbl, False, False, 1)

        self.perf_lbl = Gtk.Label()
        self.perf_lbl.set_xalign(0.01)
        self.perf_lbl.set_markup(
            "<span size='small' foreground='#4ade80'>⚡ 55 FPS (0.25ms) | PRIME C99: 8,737 tok/s | Phi-3: 24.8 tok/s | RAM: 3690/11681MB</span>"
        )
        center_vbox.pack_start(self.perf_lbl, False, False, 1)

        self.sim_canvas = Gtk.DrawingArea()
        self.sim_canvas.set_size_request(420, 320)
        self.sim_canvas.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.sim_canvas.connect("draw", self._draw_sim_canvas)
        self.sim_canvas.connect("button-press-event", self._on_sim_canvas_click)
        center_vbox.pack_start(self.sim_canvas, True, True, 0)

        # COLUMN 3: 3-Tab Right Panel (School Tutorials | Hands-On Coding | Brain & Phi-3)
        self.right_frame = Gtk.Frame(label=" ★ 3. Mission Steps & AI Brain Peek ")
        self.right_frame.set_size_request(330, -1)
        main_hbox.pack_start(self.right_frame, False, False, 0)

        self.right_notebook = Gtk.Notebook()
        self.right_frame.add(self.right_notebook)

        # --- TAB 0: FOLLOW-ALONG SCHOOL TUTORIALS ---
        school_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        school_vbox.set_margin_top(5)
        school_vbox.set_margin_bottom(5)
        school_vbox.set_margin_start(5)
        school_vbox.set_margin_end(5)

        self.lesson_lbl = Gtk.Label()
        self.lesson_lbl.set_xalign(0.0)
        self.lesson_lbl.set_markup("<b><span foreground='#facc15'>★ Pick Your AI Mission:</span></b>")
        school_vbox.pack_start(self.lesson_lbl, False, False, 0)

        self.lesson_combo = SynapseDropdown()
        for les in SCHOOL_CURRICULUM:
            short_title = les["title"] if len(les["title"]) <= 34 else les["title"][:31] + "..."
            self.lesson_combo.append(les["id"], short_title)
        self.lesson_combo.set_active_id(self.active_lesson_id)
        self.lesson_combo.connect("changed", self._on_lesson_changed)
        school_vbox.pack_start(self.lesson_combo, False, False, 0)

        lesson_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        school_vbox.pack_start(lesson_btn_box, False, False, 0)

        self.btn_load_preset = Gtk.Button(label="★ 1. Start Mission!")
        self.btn_load_preset.connect("clicked", self._on_apply_lesson_preset)
        lesson_btn_box.pack_start(self.btn_load_preset, True, True, 0)

        self.btn_check_goal = Gtk.Button(label="✓ 2. Did I Win?")
        self.btn_check_goal.connect("clicked", self._on_check_lesson_goal)
        lesson_btn_box.pack_start(self.btn_check_goal, True, True, 0)

        self.btn_kid_peek_brain = Gtk.Button(label="⚙ Peek Inside AI Brain!")
        self.btn_kid_peek_brain.connect("clicked", lambda _b: self.right_notebook.set_current_page(2))
        school_vbox.pack_start(self.btn_kid_peek_brain, False, False, 0)

        self.btn_open_challenge = Gtk.Button(label="✎ 3. Open Python Coding Challenge")
        self.btn_open_challenge.connect("clicked", self._on_open_lesson_coding)
        school_vbox.pack_start(self.btn_open_challenge, False, False, 0)

        lesson_scroll = Gtk.ScrolledWindow()
        lesson_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        school_vbox.pack_start(lesson_scroll, True, True, 0)

        self.lesson_text = Gtk.TextView()
        self.lesson_text.set_editable(False)
        self.lesson_text.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        lesson_scroll.add(self.lesson_text)

        self.right_notebook.append_page(school_vbox, Gtk.Label(label="★ Tutorials"))

        # --- TAB 1: HANDS-ON PYTHON CODING SANDBOX (EDIT & RUN!) ---
        code_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        code_vbox.set_margin_top(5)
        code_vbox.set_margin_bottom(5)
        code_vbox.set_margin_start(5)
        code_vbox.set_margin_end(5)

        code_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        code_vbox.pack_start(code_btn_box, False, False, 0)

        btn_run_code = Gtk.Button(label="▶ Run")
        btn_run_code.connect("clicked", self._on_run_student_code)
        code_btn_box.pack_start(btn_run_code, True, True, 0)

        btn_sync_sliders = Gtk.Button(label="↻ Sync")
        btn_sync_sliders.connect("clicked", self._on_sync_code_from_sliders)
        code_btn_box.pack_start(btn_sync_sliders, True, True, 0)

        btn_tutor_help = Gtk.Button(label="⚡ Tutor")
        btn_tutor_help.connect("clicked", self._on_ask_tutor_about_code)
        code_btn_box.pack_start(btn_tutor_help, True, True, 0)

        code_scroll = Gtk.ScrolledWindow()
        code_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        code_vbox.pack_start(code_scroll, True, True, 0)

        self.code_view = Gtk.TextView()
        self.code_view.set_editable(True)
        self.code_view.set_monospace(True)
        code_scroll.add(self.code_view)

        out_frame = Gtk.Frame(label=" ▸ Sandbox Output ")
        code_vbox.pack_start(out_frame, False, False, 0)

        out_scroll = Gtk.ScrolledWindow()
        out_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        out_scroll.set_size_request(-1, 110)
        out_frame.add(out_scroll)

        self.sandbox_out_view = Gtk.TextView()
        self.sandbox_out_view.set_editable(False)
        self.sandbox_out_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.sandbox_out_view.get_buffer().set_text(
            "✎ Edit the Python code above and click '▶ Run' to see what happens!"
        )
        out_scroll.add(self.sandbox_out_view)

        self.right_notebook.append_page(code_vbox, Gtk.Label(label="✎ Code"))

        # --- TAB 2: ANIMATED PHI-3 BRAIN & LIVE NEURAL TOPOLOGY ---
        viz_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.btn_kid_back_mission = Gtk.Button(label="★ Back to My Mission Steps")
        self.btn_kid_back_mission.connect("clicked", lambda _b: self.right_notebook.set_current_page(0))
        viz_vbox.pack_start(self.btn_kid_back_mission, False, False, 2)

        self.net_canvas = Gtk.DrawingArea()
        self.net_canvas.set_size_request(315, 340)
        self.net_canvas.connect("draw", self._draw_net_canvas)
        viz_vbox.pack_start(self.net_canvas, True, True, 0)
        self.right_notebook.append_page(viz_vbox, Gtk.Label(label="⚙ Brain & Phi-3"))

        # --- BOTTOM BAR: BUILT-IN CORTEX-PHI3 GENERAL CHAT, AI TUTOR & LINUX RUNNER ---
        self.cortex_frame = Gtk.Frame(label=" ★ 4. Ask Cortex (Your Friendly AI Buddy!) ")
        root_vbox.pack_start(self.cortex_frame, False, False, 0)

        cortex_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        cortex_vbox.set_margin_top(3)
        cortex_vbox.set_margin_bottom(3)
        cortex_vbox.set_margin_start(5)
        cortex_vbox.set_margin_end(5)
        self.cortex_frame.add(cortex_vbox)

        query_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        cortex_vbox.pack_start(query_hbox, False, False, 0)

        self.cortex_entry = Gtk.Entry()
        self.cortex_entry.set_placeholder_text("Ask your AI Buddy Cortex a question about the game...")
        self.cortex_entry.connect("activate", self._on_general_chat)
        query_hbox.pack_start(self.cortex_entry, True, True, 0)

        self.btn_chat = Gtk.Button(label="★ Ask AI Buddy!")
        self.btn_chat.set_tooltip_text("Chat with your friendly local Cortex-Phi3 AI Buddy!")
        self.btn_chat.connect("clicked", self._on_general_chat)
        query_hbox.pack_start(self.btn_chat, False, False, 0)

        self.btn_ask_fast = Gtk.Button(label="⚡ Instant (<1ms)")
        self.btn_ask_fast.connect("clicked", self._on_ask_cortex_fast)
        query_hbox.pack_start(self.btn_ask_fast, False, False, 0)

        self.btn_ask_llm = Gtk.Button(label="★ Give Me a Hint!")
        self.btn_ask_llm.connect("clicked", self._on_ask_cortex_llm)
        query_hbox.pack_start(self.btn_ask_llm, False, False, 0)

        self.btn_ask_cmd = Gtk.Button(label="⌘ Linux (??)")
        self.btn_ask_cmd.connect("clicked", self._on_ask_linux_cmd)
        query_hbox.pack_start(self.btn_ask_cmd, False, False, 0)

        self.btn_run_cmd = Gtk.Button(label="▶ Run Cmd")
        self.btn_run_cmd.connect("clicked", self._on_run_linux_cmd)
        query_hbox.pack_start(self.btn_run_cmd, False, False, 0)

        self.btn_clear_chat = Gtk.Button(label="↻ Clear")
        self.btn_clear_chat.connect("clicked", self._on_clear_chat)
        query_hbox.pack_start(self.btn_clear_chat, False, False, 0)

        self.last_synthesized_cmd: str = ""
        self.last_cmd_query: str = ""

        cortex_out_scroll = Gtk.ScrolledWindow()
        cortex_out_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        cortex_out_scroll.set_size_request(-1, 76)
        cortex_vbox.pack_start(cortex_out_scroll, False, False, 0)

        self.cortex_text = Gtk.TextView()
        self.cortex_text.set_editable(False)
        self.cortex_text.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        cortex_out_scroll.add(self.cortex_text)
        self._set_cortex_message(
            "★ Welcome to Kid Mode! Click '⚡ SUPER TRAIN AI (+25 TRIES!)' on the left to watch your AI learn, "
            "complete Missions on the right to unlock new sliders, or click '⚙ Teacher / Pro Mode' at the top-right for full engineering controls!"
        )

    def _populate_examples_dropdown(self) -> None:
        self.example_combo.clear()
        examples = get_examples_for_lab(self.active_lab_id)
        for ex in examples:
            short_t = ex["title"] if len(ex["title"]) <= 28 else ex["title"][:25] + "..."
            self.example_combo.append(ex["id"], short_t)

    def _on_example_selected(self, combo: SynapseDropdown) -> None:
        ex_id = combo.get_active_id()
        if not ex_id:
            return
        examples = get_examples_for_lab(self.active_lab_id)
        chosen = next((e for e in examples if e["id"] == ex_id), None)
        if not chosen:
            return

        lab = self.active_lab
        for k, v in chosen["params"].items():
            if k in lab.params:
                lab.update_param(k, v)
        if hasattr(lab, "reset_generation"):
            lab.reset_generation()
            # Re-apply target_hidden after reset_generation so pre-grown hidden neurons persist in fleet
            if "target_hidden" in chosen["params"]:
                lab.update_param("target_hidden", chosen["params"]["target_hidden"])
        elif hasattr(lab, "reset_q_table"):
            lab.reset_q_table()
        elif hasattr(lab, "reset_ecosystem"):
            lab.reset_ecosystem()
        elif hasattr(lab, "rebuild_simulation"):
            lab.rebuild_simulation()

        self._populate_sliders()
        self.sim_canvas.queue_draw()
        self.net_canvas.queue_draw()
        self._set_cortex_message(
            f"★ Loaded {chosen['title']}!\n   • {chosen['desc']}\n   • Click '⚡ Turbo +25 Gens' or drag sliders on the left to experiment!"
        )

    def _on_brain_surgery(self, _btn: Gtk.Button, delta_neurons: int, delta_synapses: int) -> None:
        lab = self.active_lab
        if hasattr(lab, "modify_brain_structure"):
            info = lab.modify_brain_structure(delta_neurons=delta_neurons, delta_synapses=delta_synapses)
            self._populate_sliders()
            self.right_notebook.set_current_page(2)  # Show the live Brain tab immediately
            self.sim_canvas.queue_draw()
            self.net_canvas.queue_draw()
            action = (
                f"Added +{delta_neurons} Neuron(s)" if delta_neurons > 0 else
                f"Removed {delta_neurons} Neuron(s)" if delta_neurons < 0 else
                f"Added +{delta_synapses} Synapse(s)" if delta_synapses > 0 else
                f"Pruned {abs(delta_synapses)} Synapse(s)"
            )
            self._set_cortex_message(
                f"⚙ Live Brain Surgery: {action}! Active Topology -> Total Nodes: {info.get('total_nodes')}, "
                f"Hidden/Active Units: {info.get('hidden_nodes')}, Synapses: {info.get('enabled_synapses')}."
            )

    def _on_open_browser(self, _btn: Gtk.Button) -> None:
        import subprocess
        import shutil
        url = "https://github.com/batteryphil/SynapseOS"
        if shutil.which("firefox-esr"):
            cmd = f"firefox-esr --no-sandbox '{url}' &"
            bname = "Firefox ESR"
        elif shutil.which("netsurf-gtk"):
            cmd = f"netsurf-gtk '{url}' &"
            bname = "NetSurf GTK"
        elif shutil.which("xdg-open"):
            cmd = f"xdg-open '{url}' &"
            bname = "System Browser"
        else:
            self._set_cortex_message("✗ No web browser binary found on PATH.")
            return
        subprocess.Popen(cmd, shell=True)
        self._set_cortex_message(f"◈ Launched {bname} Web Browser! (Opening {url} on desktop)")

    def _on_show_tunnel(self, _btn: Gtk.Button) -> None:
        import re
        log_path = "/tmp/cloudflared.log"
        url = ""
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    m = re.search(r"https://[a-zA-Z0-9.-]+\.trycloudflare\.com", f.read())
                    if m:
                        url = m.group(0)
            except Exception:
                pass
        if url:
            self._set_cortex_message(
                f"❖ SECURE REMOTE BROWSER TUNNEL ACTIVE!\n"
                f"   • Shareable HTTPS Link (Anywhere):  {url}/vnc.html?autoconnect=1&resize=scale\n"
                f"   • Local Wi-Fi / LAN Link:           http://192.168.40.151:6080\n"
                f"   • Remote VNC Password:              synapse-ai"
            )
        else:
            self._set_cortex_message("❖ Starting encrypted Cloudflare + noVNC tunnel in background...")
            def start_worker():
                import subprocess
                subprocess.run(["/usr/local/bin/synapse-tunnel", "synapse-ai"], check=False)
                GLib.idle_add(self._on_show_tunnel, _btn)
            threading.Thread(target=start_worker, daemon=True).start()

    def _on_general_chat(self, _widget: Any) -> None:
        q = self.cortex_entry.get_text().strip()
        if not q:
            q = "Hello Cortex-Phi3! Who are you and how does your PRIME Moment Attention memory work?"
            self.cortex_entry.set_text(q)

        # Switch right notebook to Brain & Phi-3 tab so user sees the Phi-3 neural brain light up!
        self.right_notebook.set_current_page(2)
        self._set_cortex_message(f"▸ You: {q}\n⚡ Cortex-Phi3 is thinking (watch the Phi-3 Brain fire on the right!)...")

        def worker():
            res = self.cortex.chat_with_cortex(q, history=self.chat_history)
            reply = res.get("reply", "")
            self.chat_history.append((q, reply))
            if len(self.chat_history) > 12:
                self.chat_history.pop(0)

            history_lines = []
            for u_msg, a_msg in self.chat_history[-3:]:
                history_lines.append(f"▸ You: {u_msg}\n★ Cortex-Phi3 [{res.get('gen_tps', 0)} tok/s | TTFT {res.get('ttft_ms', 0)}ms | PRIME {res.get('prime_state_kb', 67.1)}KB]: {a_msg}")
            full_text = "\n\n".join(history_lines)
            GLib.idle_add(self._set_cortex_message, full_text)

        threading.Thread(target=worker, daemon=True).start()

    def _on_clear_chat(self, _btn: Gtk.Button) -> None:
        self.chat_history.clear()
        self.cortex_entry.set_text("")
        self._set_cortex_message("↻ Cleared General Chat history and PRIME conversation buffer.")

    def _update_badge_header(self) -> None:
        total = len(SCHOOL_CURRICULUM)
        earned = len(self.earned_badges)
        self.badge_lbl.set_markup(
            f"<b><span foreground='#facc15'>★ Badges: {earned} / {total}</span></b>"
        )

    def _on_unlock_next_slider(self, _btn: Gtk.Button) -> None:
        total_specs = len(self.active_lab.VARIABLE_SPECS)
        self.kid_unlocked_sliders = min(total_specs, self.kid_unlocked_sliders + 1)
        self._populate_sliders()
        unlocked_name = self.active_lab.VARIABLE_SPECS[min(total_specs - 1, self.kid_unlocked_sliders - 1)]["label"]
        self._set_cortex_message(
            f"★ LEVEL UP! You unlocked a new AI control slider: '{unlocked_name}'! Try dragging it on the left!"
        )

    def _set_kid_mode(self, is_kid: bool) -> None:
        self.kid_mode = is_kid
        self._apply_ui_mode()
        self._populate_sliders()
        if is_kid:
            self._set_cortex_message(
                "★ Switched to KID MODE (Scratch Style)! Big buttons are active, complex telemetry is hidden, and sliders unlock step-by-step as you complete missions!"
            )
        else:
            self._set_cortex_message(
                "⚙ Switched to TEACHER / PRO MODE! All engineering sliders, live FPS/TTFT/RAM telemetry, Python code sandbox, and Linux command runner are now unlocked!"
            )

    def _apply_ui_mode(self) -> None:
        def set_cls(btn: Gtk.Widget, add_classes: List[str], rem_classes: List[str]) -> None:
            ctx = btn.get_style_context()
            for rc in rem_classes:
                ctx.remove_class(rc)
            for ac in add_classes:
                ctx.add_class(ac)

        all_kid_classes = ["kid-btn-play", "kid-btn-turbo", "kid-btn-brain", "kid-btn-unlock", "mode-active-kid", "mode-active-pro"]

        if self.kid_mode:
            self.mode_stack.set_visible_child_name("kid")
            self.kids_view.queue_draw()
            set_cls(self.btn_kid_mode, ["mode-active-kid"], ["mode-active-pro"])
            set_cls(self.btn_pro_mode, [], ["mode-active-pro", "mode-active-kid"])
        else:
            self.mode_stack.set_visible_child_name("pro")
            set_cls(self.btn_pro_mode, ["mode-active-pro"], ["mode-active-kid"])
            set_cls(self.btn_kid_mode, [], ["mode-active-kid", "mode-active-pro"])
            for b in [
                self.btn_run, self.btn_turbo, self.btn_add_neuron, self.btn_sub_neuron,
                self.btn_load_preset, self.btn_check_goal, self.btn_chat, self.btn_ask_llm,
            ]:
                set_cls(b, [], all_kid_classes)

            self.title_lbl.set_markup("<b><span foreground='#38bdf8'>⚡ SYNAPSE STUDIO</span></b>")
            self.left_frame.set_label(" ⚙ 1. Presets, Brain Surgery & Sliders ")
            self.center_frame.set_label(" ◈ 2. Real-Time Simulation Viewport & Performance Telemetry ")
            self.right_frame.set_label(" ★ 3. Tutorials, Code & Live Phi-3 Brain ")
            self.right_frame.set_size_request(360, -1)
            self.cortex_frame.set_label(" ⚡ 4. Cortex-Phi3 General Chat, Classroom AI Tutor & Live Linux Runner ")

            self.ex_lbl.set_markup("<b><span size='small' foreground='#facc15'>★ 5 Examples for Current Lab:</span></b>")
            self.surg_lbl.set_markup("<b><span size='small' foreground='#38bdf8'>⚙ Direct Brain Surgery (+/-):</span></b>")
            self.btn_run.set_label("|| Pause" if self.running else "▶ Resume")
            self.btn_turbo.set_label("⚡ Turbo +25 Gens")
            self.btn_reset.set_label("↻ Reset")
            self.btn_add_neuron.set_label("+ Add Neuron")
            self.btn_sub_neuron.set_label("- Sub Neuron")
            self.btn_load_preset.set_label("▸ 1. Load Preset")
            self.btn_check_goal.set_label("✓ 2. Check Goal")
            self.btn_chat.set_label("★ General Chat")
            self.btn_ask_llm.set_label("★ AI Tutor")
            self.cortex_entry.set_placeholder_text("Chat with Cortex-Phi3, ask an AI question, or type a Linux command...")

            # Show all engineering controls in Teacher / Pro Mode
            self.btn_step.show()
            self.btn_export.show()
            self.btn_add_syn.show()
            self.btn_sub_syn.show()
            self.perf_lbl.show()
            self.btn_open_challenge.show()
            self.btn_ask_fast.show()
            self.btn_ask_cmd.show()
            self.btn_run_cmd.show()

            self.btn_kid_peek_brain.hide()
            self.btn_kid_back_mission.hide()
            self.right_notebook.set_show_tabs(True)
            self.right_notebook.set_current_page(2)

    def _populate_sliders(self) -> None:
        self._updating_sliders = True
        for child in self.sliders_vbox.get_children():
            self.sliders_vbox.remove(child)
        self.slider_widgets.clear()

        lab = self.active_lab
        specs = lab.VARIABLE_SPECS
        total_specs = len(specs)
        if self.kid_mode:
            unlocked_count = min(total_specs, self.kid_unlocked_sliders + len(self.earned_badges) * 2)
        else:
            unlocked_count = total_specs

        for idx, spec in enumerate(specs):
            if idx >= unlocked_count:
                break
            key = spec["key"]
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
            lbl = Gtk.Label()
            lbl.set_xalign(0.0)
            prefix = f"★ " if self.kid_mode else ""
            lbl.set_markup(f"<b>{prefix}{GLib.markup_escape_text(spec['label'])}</b>")
            lbl.set_tooltip_text(spec["desc"])
            box.pack_start(lbl, False, False, 0)

            desc_lbl = Gtk.Label()
            desc_lbl.set_xalign(0.0)
            desc_lbl.set_line_wrap(True)
            desc_lbl.set_max_width_chars(30)
            desc_lbl.set_markup(f"<span size='small' foreground='#94a3b8'>{GLib.markup_escape_text(spec['desc'])}</span>")
            box.pack_start(desc_lbl, False, False, 0)

            adj = Gtk.Adjustment(
                value=lab.params[key],
                lower=spec["min"],
                upper=spec["max"],
                step_increment=spec["step"],
                page_increment=spec["step"] * 2,
                page_size=0
            )
            scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj)
            scale.set_digits(2 if spec["step"] < 1.0 else 0)
            scale.set_value_pos(Gtk.PositionType.RIGHT)
            scale.connect("value-changed", self._on_slider_changed, key)
            box.pack_start(scale, False, False, 0)

            self.sliders_vbox.pack_start(box, False, False, 2)
            self.slider_widgets[key] = scale

        if self.kid_mode and unlocked_count < total_specs:
            rem = total_specs - unlocked_count
            next_label = specs[unlocked_count]["label"]
            unlock_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
            unlock_box.set_margin_top(6)

            lock_lbl = Gtk.Label()
            lock_lbl.set_xalign(0.0)
            lock_lbl.set_line_wrap(True)
            lock_lbl.set_max_width_chars(28)
            lock_lbl.set_markup(
                f"<b><span foreground='#c084fc'>★ {rem} More Sliders Locked!</span></b>\n"
                f"<span size='small' foreground='#cbd5e1'>Next: <b>{GLib.markup_escape_text(next_label)}</b>\n"
                f"Win a Mission Badge or click below to unlock step-by-step:</span>"
            )
            unlock_box.pack_start(lock_lbl, False, False, 0)

            btn_unlock = Gtk.Button(label=f"★ Unlock '{next_label[:16]}' (+1)")
            btn_unlock.get_style_context().add_class("kid-btn-unlock")
            btn_unlock.connect("clicked", self._on_unlock_next_slider)
            unlock_box.pack_start(btn_unlock, False, False, 0)

            self.sliders_vbox.pack_start(unlock_box, False, False, 4)

        self.sliders_vbox.show_all()
        self._updating_sliders = False

    @staticmethod
    def _clean_bmp(text: str) -> str:
        """Replace supplementary-plane emojis (>U+FFFF) with crisp BMP symbols for minimal X11 fonts."""
        replacements = {
            "🎯": "▸",
            "✅": "✓",
            "🎉": "★",
            "🏅": "★",
            "🏆": "★",
            "🎖️": "★",
            "🎓": "★",
            "🧠": "⚙",
            "🚀": "★",
            "🏎️": "◈",
            "🧭": "❖",
            "🧬": "✦",
            "🤖": "⚡",
            "🐧": "⌘",
            "💡": "▸",
            "📖": "▸",
            "🔄": "↻",
            "💾": "✎",
            "🔥": "⚡",
            "💬": "▸",
            "🌐": "◈",
            "🔑": "★",
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        return "".join(ch for ch in text if ord(ch) < 0x10000)

    def _refresh_lesson_view(self) -> None:
        lesson = get_lesson_by_id(self.active_lesson_id)
        badge_status = "✓ EARNED!" if lesson["id"] in self.earned_badges else "In Progress"
        steps_str = "\n".join(f"  {self._clean_bmp(s)}" for s in lesson["steps"])
        clean_badge = self._clean_bmp(lesson["badge"]).strip()
        txt = (
            f"★ {self._clean_bmp(lesson['track'])}\n"
            f"▸ {self._clean_bmp(lesson['title'])}  [{lesson['grade_level']}]\n"
            f"★ Badge: [{clean_badge}] ({badge_status})\n"
            f"--------------------------------------------------\n\n"
            f"▸ STORY & AI CONCEPT:\n{self._clean_bmp(lesson['story'])}\n\n"
            f"▸ FOLLOW-ALONG STEPS:\n{steps_str}\n\n"
            f"▸ MISSION GOAL:\n  • {self._clean_bmp(lesson['goal_desc'])}"
        )
        self.lesson_text.get_buffer().set_text(txt)

    def _load_lesson_coding_challenge(self) -> None:
        lesson = get_lesson_by_id(self.active_lesson_id)
        self.code_view.get_buffer().set_text(self._clean_bmp(lesson["coding_challenge"]))

    def _on_lesson_changed(self, combo: Gtk.ComboBoxText) -> None:
        lid = combo.get_active_id()
        if lid:
            self.active_lesson_id = lid
            self._refresh_lesson_view()
            self._load_lesson_coding_challenge()

    def _on_apply_lesson_preset(self, _btn: Gtk.Button) -> None:
        lesson = get_lesson_by_id(self.active_lesson_id)
        target_lab = lesson["lab_id"]
        if self.active_lab_id != target_lab:
            self.active_lab_id = target_lab
            self.lab_combo.set_active_id(target_lab)
            self._populate_examples_dropdown()

        lab = self.active_lab
        for k, v in lesson["preset_params"].items():
            lab.update_param(k, v)
        if hasattr(lab, "reset_generation"):
            lab.reset_generation()
        elif hasattr(lab, "reset_q_table"):
            lab.reset_q_table()
        elif hasattr(lab, "reset_ecosystem"):
            lab.reset_ecosystem()

        self._populate_sliders()
        self._set_cortex_message(
            f"★ Mission '{lesson['title']}' Ready! Now click '⚡ SUPER TRAIN AI (+25 TRIES!)' on the left to train your AI!"
        )

    def _on_check_lesson_goal(self, _btn: Gtk.Button) -> None:
        lesson = get_lesson_by_id(self.active_lesson_id)
        telem = self.labs[lesson["lab_id"]].get_telemetry()
        passed, msg = verify_lesson_goal(lesson, telem)
        if passed:
            was_new = lesson["id"] not in self.earned_badges
            self.earned_badges.add(lesson["id"])
            self._update_badge_header()
            self._refresh_lesson_view()
            if was_new and self.kid_mode:
                self._populate_sliders()
                msg += "\n★ BONUS: You unlocked 2 new AI Control Sliders on the left!"
        self._set_cortex_message(msg)

    def _on_open_lesson_coding(self, _btn: Gtk.Button) -> None:
        self._load_lesson_coding_challenge()
        self.right_notebook.set_current_page(1)
        self._set_cortex_message(
            "✎ Loaded the Hands-On Python Coding Challenge! Read the `# HANDS-ON CODING CHALLENGE` comment at the top and click '▶ Run Code'!"
        )

    def _on_run_student_code(self, _btn: Gtk.Button) -> None:
        buf = self.code_view.get_buffer()
        start, end = buf.get_bounds()
        code_str = buf.get_text(start, end, False)
        self.sandbox_out_view.get_buffer().set_text("Running your Python code in sandbox...")

        def worker():
            res = run_student_code(code_str)
            GLib.idle_add(self.sandbox_out_view.get_buffer().set_text, self._clean_bmp(res["output"]))

        threading.Thread(target=worker, daemon=True).start()

    def _on_sync_code_from_sliders(self, _btn: Gtk.Button) -> None:
        code = generate_lab_python_code(self.active_lab_id, self.active_lab.params, self.active_lab.get_telemetry())
        self.code_view.get_buffer().set_text(self._clean_bmp(code))

    def _on_ask_tutor_about_code(self, _btn: Gtk.Button) -> None:
        buf = self.code_view.get_buffer()
        start, end = buf.get_bounds()
        code_str = buf.get_text(start, end, False)
        self._set_cortex_message("Cortex-Phi3 Classroom Tutor is reading your Python code...")

        def worker():
            if self.cortex.is_ollama_available():
                sys_p = (
                    "You are Cortex, a friendly, encouraging school AI coding tutor. "
                    "Explain what the student's Python code does in 3 short bullet points suitable for a 10-to-14-year-old, "
                    "and suggest 1 fun experiment they can try changing!"
                )
                resp = self.cortex.query_local_ollama(f"Student Python Code:\n```python\n{code_str}\n```", system_prompt=sys_p)
                if resp:
                    GLib.idle_add(self._set_cortex_message, f"★ Cortex Coding Tutor:\n{resp.strip()}")
                    return
            GLib.idle_add(
                self._set_cortex_message,
                "★ Cortex Coding Tutor (Offline Tip): Your code imports a SynapseOS AI Lab, sets experiment variables with "
                "`update_param(...)`, evolves generations, and prints the telemetry scores! Try changing the numbers inside `update_param` and click '▶ Run Code'!"
            )

        threading.Thread(target=worker, daemon=True).start()

    def _on_lab_changed(self, combo: SynapseDropdown) -> None:
        lid = combo.get_active_id()
        if lid and lid in self.labs:
            self.active_lab_id = lid
            self.kid_unlocked_sliders = 2
            self._populate_examples_dropdown()
            self._populate_sliders()
            self._set_cortex_message(
                f"★ Switched to {combo.get_active_text()}! Click '⚡ SUPER TRAIN AI (+25 TRIES!)' or try the unlocked sliders on the left!"
            )

    def _on_mode_toggled(self, btn: Gtk.RadioButton, mode: str) -> None:
        if not btn.get_active():
            return
        self.user_mode = mode
        if mode == "school":
            self.right_notebook.set_current_page(0)
        elif mode == "studio":
            self.right_notebook.set_current_page(1)
        elif mode == "pro":
            self.right_notebook.set_current_page(2)

    def _on_slider_changed(self, scale: Gtk.Scale, key: str) -> None:
        if self._updating_sliders:
            return
        val = scale.get_value()
        self.active_lab.update_param(key, val)
        if self.right_notebook.get_current_page() == 2:
            self.net_canvas.queue_draw()

    def _on_toggle_run(self, _btn: Gtk.Button) -> None:
        self.running = not self.running
        if self.kid_mode:
            self.btn_run.set_label("|| PAUSE GAME" if self.running else "▶ PLAY GAME!")
        else:
            self.btn_run.set_label("|| Pause" if self.running else "▶ Resume")

    def _on_step_once(self, _btn: Gtk.Button) -> None:
        self.running = False
        self.btn_run.set_label("▶ PLAY GAME!" if self.kid_mode else "▶ Resume")
        self.active_lab.step_physics()
        self.sim_canvas.queue_draw()
        self.net_canvas.queue_draw()

    def _on_turbo_evolve(self, _btn: Gtk.Button) -> None:
        t0 = time.perf_counter()
        stats = self.active_lab.fast_forward_generations(25)
        dt_ms = round((time.perf_counter() - t0) * 1000, 1)
        self.sim_canvas.queue_draw()
        self.net_canvas.queue_draw()

        # Auto-check active lesson goal if it matches the current lab
        lesson = get_lesson_by_id(self.active_lesson_id)
        bonus_msg = ""
        if lesson["lab_id"] == self.active_lab_id:
            passed, goal_msg = verify_lesson_goal(lesson, stats)
            if passed and lesson["id"] not in self.earned_badges:
                self.earned_badges.add(lesson["id"])
                self._update_badge_header()
                self._refresh_lesson_view()
                if self.kid_mode:
                    self._populate_sliders()
                    bonus_msg = f"\n{goal_msg}\n★ BONUS: You unlocked 2 new AI Control Sliders on the left!"
                else:
                    bonus_msg = f"\n{goal_msg}"

        if self.kid_mode:
            self._set_cortex_message(
                f"⚡ SUPER TRAINED! Your AI practiced 25 times in {dt_ms} ms!\n"
                f"   • AI Try #{stats['generation']} | Best Score: {stats['best_fitness']} | All-Time High Score: {stats['best_ever']}{bonus_msg}"
            )
        else:
            self._set_cortex_message(
                f"⚡ Turbo Evolution completed 25 generations/epochs in {dt_ms} ms on pure CPU!\n"
                f"   • Current Gen/Epoch: {stats['generation']} | Best Score: {stats['best_fitness']} | All-Time Best: {stats['best_ever']}{bonus_msg}"
            )

    def _on_reset_lab(self, _btn: Gtk.Button) -> None:
        lid = self.active_lab_id
        cls = type(self.labs[lid])
        self.labs[lid] = cls()
        self._populate_sliders()
        self._set_cortex_message(f"↻ Reset {lid} population and weights to Generation 1.")

    def _on_export_py(self, _btn: Gtk.Button) -> None:
        code = generate_lab_python_code(self.active_lab_id, self.active_lab.params, self.active_lab.get_telemetry())
        out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", f"exported_{self.active_lab_id}.py"))
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(code)
        os.chmod(out_path, 0o755)
        self.code_view.get_buffer().set_text(self._clean_bmp(code))
        self.right_notebook.set_current_page(1)
        self._set_cortex_message(f"✎ Exported standalone runnable Python experiment to:\n   {out_path}")

    def _set_cortex_message(self, msg: str) -> None:
        self.cortex_text.get_buffer().set_text(self._clean_bmp(msg))

    def _on_ask_cortex_fast(self, _widget: Any) -> None:
        q = self.cortex_entry.get_text().strip() or self.active_lab_id.replace("_", " ")
        t0 = time.perf_counter()
        info = self.cortex.explain_ai_concept(q, force_llm=False)
        fts_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        telem = self.active_lab.get_telemetry()
        text = (
            f"⚙ [{info.get('title', q)}] ({info.get('source', 'FTS5 KB')} in {fts_ms} ms)\n"
            f"• Kid & Layman Guide: {info.get('layman_guide', info.get('summary', ''))}\n"
            f"• Live Lab Telemetry: Gen/Ep={telem['generation']}, Best={telem['best_fitness']}, All-Time={telem['best_ever']}"
        )
        self._set_cortex_message(text)

    def _on_ask_cortex_llm(self, _widget: Any) -> None:
        q = self.cortex_entry.get_text().strip() or f"Explain how {self.active_lab_id} works for a student!"
        telem = self.active_lab.get_telemetry()
        enriched_q = f"{q} (Current Lab: {telem['lab']}, Gen: {telem['generation']}, Best: {telem['best_fitness']}, Variables: {telem['params']})"
        self.right_notebook.set_current_page(2)
        self._set_cortex_message("Consulting local `cortex-phi3:latest` Classroom Tutor (watch the Phi-3 Brain fire on the right!)...")

        def worker():
            info = self.cortex.explain_ai_concept(enriched_q, force_llm=True)
            m = self.cortex.last_llm_metrics
            ans = (
                f"★ {info.get('title')} [{info.get('source')} | {m.get('gen_tps', 0)} tok/s | TTFT {m.get('ttft_ms', 0)}ms]\n"
                f"{info.get('summary', '')}"
            )
            GLib.idle_add(self._set_cortex_message, ans)

        threading.Thread(target=worker, daemon=True).start()

    def _on_ask_linux_cmd(self, _widget: Any) -> None:
        q = self.cortex_entry.get_text().strip() or "check disk space and memory"
        res = self.cortex.synthesize_command_and_instructions(q, force_llm=False)
        self.last_synthesized_cmd = res.get("command", "")
        self.last_cmd_query = q
        steps = " | ".join(f"{i}. {s}" for i, s in enumerate(res.get("instructions", []), 1))
        text = (
            f"⌘ Linux Command [{res.get('safety', 'safe').upper()}] ({res.get('source', 'FTS5')}): {res.get('summary')}\n"
            f"▸ Command:  {self.last_synthesized_cmd}   (Click '▶ Run Cmd' to execute live!)\n"
            f"▸ Steps:    {steps}"
        )
        self._set_cortex_message(text)

    def _on_run_linux_cmd(self, _widget: Any) -> None:
        import subprocess
        import shutil
        q = self.cortex_entry.get_text().strip() or "check disk space and memory"
        first_word = q.split()[0] if q.split() else ""
        is_direct_shell = (
            bool(first_word)
            and shutil.which(first_word) is not None
            and (any(c in q for c in ["-", "|", "/", ";", "&"]) or len(q.split()) <= 3)
        )
        if self.last_synthesized_cmd and q == self.last_cmd_query:
            cmd = self.last_synthesized_cmd
            safety = "safe"
            source = "Synthesized"
        elif is_direct_shell:
            cmd = q
            safety = "safe"
            source = "Direct Shell"
        else:
            res = self.cortex.synthesize_command_and_instructions(q, force_llm=False)
            cmd = res.get("command", "").strip()
            safety = res.get("safety", "safe").lower()
            source = res.get("source", "FTS5")
            self.last_synthesized_cmd = cmd
            self.last_cmd_query = q

        # Block destructive patterns
        danger_tokens = ["rm -rf /", "mkfs", "dd if=", ":(){", "shutdown", "reboot", "poweroff", "> /dev/sd"]
        if safety == "danger" or any(tok in cmd for tok in danger_tokens):
            self._set_cortex_message(f"✗ Blocked potentially destructive command: {cmd}")
            return

        self._set_cortex_message(f"▶ Executing Linux command ({source}): $ {cmd} ...")

        def worker():
            try:
                proc = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=8,
                )
                out = (proc.stdout or "") + (proc.stderr or "")
                out = out.strip() or "(Command completed with exit code 0 and no stdout)"
                lines = out.splitlines()
                if len(lines) > 12:
                    out = "\n".join(lines[:12]) + f"\n... ({len(lines) - 12} more lines)"
                msg = f"⌘ Executed: $ {cmd}  [Exit: {proc.returncode}]\n{out}"
            except Exception as e:
                msg = f"✗ Execution Error ($ {cmd}): {e}"
            GLib.idle_add(self._set_cortex_message, msg)

        threading.Thread(target=worker, daemon=True).start()

    def _sample_system_ram(self) -> None:
        try:
            mem_total = 16000
            mem_avail = 12000
            with open("/proc/meminfo", "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        mem_total = int(line.split()[1]) // 1024
                    elif line.startswith("MemAvailable:"):
                        mem_avail = int(line.split()[1]) // 1024
            self.ram_total_mb = mem_total
            self.ram_used_mb = max(1, mem_total - mem_avail)
        except Exception:
            pass

    def _on_tick(self) -> bool:
        self._anim_phase += 0.12
        self._tick_count += 1

        if self.running:
            t_step0 = time.perf_counter()
            self.active_lab.step_physics()
            self.last_step_ms = round((time.perf_counter() - t_step0) * 1000.0, 2)

        now = time.perf_counter()
        if now - self._last_fps_time >= 0.6:
            self.live_fps = round(self._tick_count / max(1e-3, now - self._last_fps_time), 1)
            self._tick_count = 0
            self._last_fps_time = now
            self._sample_system_ram()

            m = self.cortex.last_llm_metrics
            prime_tps = self.labs["prime_attention"].c_bench.get("tokens_per_sec", 8737.0)
            phi_str = (
                f"⚡ Phi-3 GENERATING..."
                if m.get("active")
                else (f"Phi-3: {m.get('gen_tps', 24.8)} tok/s (TTFT {m.get('ttft_ms', 280)}ms)" if m.get("gen_tps", 0) > 0 else "Phi-3: 24.8 tok/s Ready")
            )
            self.perf_lbl.set_markup(
                f"<b><span size='small' foreground='#4ade80'>⚡ {self.live_fps:.0f} FPS ({self.last_step_ms:.2f}ms)</span></b> "
                f"<span size='small' foreground='#94a3b8'>|</span> "
                f"<span size='small' foreground='#38bdf8'>PRIME C99: {prime_tps:,.0f} tok/s</span> "
                f"<span size='small' foreground='#94a3b8'>|</span> "
                f"<span size='small' foreground='#facc15'>{phi_str}</span> "
                f"<span size='small' foreground='#94a3b8'>|</span> "
                f"<span size='small' foreground='#cbd5e1'>RAM: {self.ram_used_mb}/{self.ram_total_mb}MB</span>"
            )

        telem = self.active_lab.get_telemetry()
        extra = ""
        if "landed_last_gen" in telem:
            extra = f" | Landed: <b><span foreground='#4ade80'>{telem['landed_last_gen']}</span></b>"
        elif "champion_nodes" in telem and not self.kid_mode:
            extra = f" | Nodes: <b><span foreground='#38bdf8'>{telem['champion_nodes']}</span></b>"

        rec_val = telem["best_ever"]
        rec_str = "--" if isinstance(rec_val, (int, float)) and rec_val <= -1e6 else str(rec_val)

        if self.kid_mode:
            self.kids_view.step_kid_simulation()
            self.kids_view.queue_draw()
        else:
            self.telemetry_lbl.set_markup(
                f"<b>{telem['lab']}</b>   |   Gen/Ep: <b><span foreground='#38bdf8'>{telem['generation']}</span></b>   "
                f"|   Best: <b><span foreground='#4ade80'>{telem['best_fitness']}</span></b>   "
                f"|   Avg: <span foreground='#facc15'>{telem['avg_fitness']}</span>   "
                f"|   Record: <b><span foreground='#f472b6'>{rec_str}</span></b>{extra}"
            )
            self.sim_canvas.queue_draw()
            if self.right_notebook.get_current_page() == 2:
                self.net_canvas.queue_draw()
        return True

    # ==========================================================================
    # CAIRO 60 FPS SIMULATION VIEWPORT RENDERERS
    # ==========================================================================
    def _on_sim_canvas_click(self, widget: Gtk.DrawingArea, event: Gdk.EventButton) -> bool:
        alloc = widget.get_allocation()
        w, h = max(1.0, float(alloc.width)), max(1.0, float(alloc.height))
        if self.active_lab_id == "nn_playground":
            lab: NeuralPlaygroundLab = self.labs["nn_playground"]
            nx = (event.x / w) * 2.0 - 1.0
            ny = (event.y / h) * 2.0 - 1.0
            if event.button == 3:
                lbl = 0.0
            elif event.button == 2:
                lbl = 1.0
            else:
                self._pro_dot_toggle = 0.0 if getattr(self, "_pro_dot_toggle", 0.0) > 0.5 else 1.0
                lbl = self._pro_dot_toggle
            lab.add_interactive_dots(nx, ny, label=lbl, count=7)
            self.sim_canvas.queue_draw()
            return True
        return False

    def _draw_sim_canvas(self, widget: Gtk.DrawingArea, cr: cairo.Context) -> bool:
        alloc = widget.get_allocation()
        w, h = float(alloc.width), float(alloc.height)

        cr.set_source_rgb(0.05, 0.06, 0.09)
        cr.paint()

        lid = self.active_lab_id
        if lid == "moon_lander":
            self._render_moon_lander(cr, w, h)
        elif lid == "raycast_car":
            self._render_raycast_car(cr, w, h)
        elif lid == "rl_gridworld":
            self._render_rl_gridworld(cr, w, h)
        elif lid == "cartpole_rl":
            self._render_cartpole(cr, w, h)
        elif lid == "nn_playground":
            self._render_nn_playground(cr, w, h)
        elif lid == "swarm_ecosystem":
            self._render_swarm(cr, w, h)
        elif lid == "prime_attention":
            self._render_prime_attention(cr, w, h)
        return False

    def _render_moon_lander(self, cr: cairo.Context, w: float, h: float) -> None:
        lab: NEATMoonLanderLab = self.labs["moon_lander"]
        sx, sy = w / lab.width, h / lab.height
        cr.save()
        cr.scale(sx, sy)

        cr.set_source_rgba(0.8, 0.85, 1.0, 0.4)
        for i in range(25):
            cr.arc((i * 97) % int(lab.width), (i * 53) % 240, 1.2, 0, 2 * math.pi)
            cr.fill()

        cr.set_source_rgb(0.18, 0.21, 0.28)
        cr.move_to(0, lab.height)
        for tx, ty in lab.terrain:
            cr.line_to(tx, ty)
        cr.line_to(lab.width, lab.height)
        cr.close_path()
        cr.fill()

        cr.set_source_rgb(0.45, 0.52, 0.65)
        cr.set_line_width(2.0)
        for i, (tx, ty) in enumerate(lab.terrain):
            if i == 0:
                cr.move_to(tx, ty)
            else:
                cr.line_to(tx, ty)
        cr.stroke()

        px1 = lab.pad_x - lab.pad_half_w
        px2 = lab.pad_x + lab.pad_half_w
        cr.set_source_rgb(0.15, 0.85, 0.45)
        cr.set_line_width(4.0)
        cr.move_to(px1, lab.pad_y)
        cr.line_to(px2, lab.pad_y)
        cr.stroke()

        leader = lab.get_leader()
        # Draw floating connected Neural Network in upper-right sky connected to leader rocket
        if hasattr(self, "kids_view"):
            self.kids_view._draw_sky_neural_network(
                cr,
                lander_x=leader.x + 10,
                lander_y=leader.y,
                nn_cx=lab.width * 0.80,
                nn_cy=lab.height * 0.25,
                scale=0.82,
                phase=self._anim_phase,
                is_fr=False,
            )

        for r in lab.rockets:
            if not r.alive and not r.landed:
                continue
            is_lead = (r is leader)
            cr.save()
            cr.translate(r.x, r.y)
            cr.rotate(r.angle)

            if r.main_thruster and r.alive:
                cr.set_source_rgba(1.0, 0.55, 0.1, 0.92 if is_lead else 0.35)
                cr.move_to(-5, 8)
                cr.line_to(0, 21)
                cr.line_to(5, 8)
                cr.close_path()
                cr.fill()

            if is_lead:
                # Draw solar panels on lead lander
                cr.set_source_rgba(0.16, 0.58, 0.96, 0.92)
                cr.rectangle(-19, -4, 10, 7)
                cr.rectangle(9, -4, 10, 7)
                cr.fill()

            if r.landed:
                cr.set_source_rgba(0.2, 0.95, 0.5, 0.95)
            elif is_lead:
                cr.set_source_rgba(0.22, 0.82, 0.98, 1.0)
            else:
                cr.set_source_rgba(0.6, 0.65, 0.75, 0.30)

            cr.move_to(0, -12)
            cr.line_to(-8, 8)
            cr.line_to(8, 8)
            cr.close_path()
            cr.fill()
            cr.restore()

        cr.restore()

    def _render_raycast_car(self, cr: cairo.Context, w: float, h: float) -> None:
        lab: NEATRaycastCarLab = self.labs["raycast_car"]
        sx, sy = w / lab.width, h / lab.height
        phase = self._anim_phase
        cr.save()
        cr.scale(sx, sy)

        # 1. Subtle Cyber-Circuit Grid Background
        cr.set_source_rgba(0.05, 0.25, 0.32, 0.22)
        cr.set_line_width(0.8)
        for gx in range(0, int(lab.width), 36):
            cr.move_to(gx, 0)
            cr.line_to(gx, lab.height)
        for gy in range(0, int(lab.height), 36):
            cr.move_to(0, gy)
            cr.line_to(lab.width, gy)
        cr.stroke()

        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_line_join(cairo.LINE_JOIN_ROUND)

        # 2. Glowing Neon Emerald/Cyan Track Borders + Dark Asphalt Road
        # Outer neon halo
        cr.set_source_rgba(0.06, 0.92, 0.68, 0.28)
        cr.set_line_width(lab.params["track_width"] * 2.0 + 14.0)
        for i, (wx, wy) in enumerate(lab.waypoints):
            if i == 0:
                cr.move_to(wx, wy)
            else:
                cr.line_to(wx, wy)
        cr.close_path()
        cr.stroke()

        # Crisp neon cyan/emerald border
        cr.set_source_rgba(0.15, 0.96, 0.78, 0.95)
        cr.set_line_width(lab.params["track_width"] * 2.0 + 4.5)
        for i, (wx, wy) in enumerate(lab.waypoints):
            if i == 0:
                cr.move_to(wx, wy)
            else:
                cr.line_to(wx, wy)
        cr.close_path()
        cr.stroke()

        # Dark asphalt interior
        cr.set_source_rgb(0.05, 0.09, 0.14)
        cr.set_line_width(lab.params["track_width"] * 2.0)
        for i, (wx, wy) in enumerate(lab.waypoints):
            if i == 0:
                cr.move_to(wx, wy)
            else:
                cr.line_to(wx, wy)
        cr.close_path()
        cr.stroke()

        # Glowing center dashed lane + chevron arrows
        cr.set_source_rgba(0.18, 0.88, 0.75, 0.35)
        cr.set_line_width(1.4)
        cr.set_dash([7.0, 9.0])
        for i, (wx, wy) in enumerate(lab.waypoints):
            if i == 0:
                cr.move_to(wx, wy)
            else:
                cr.line_to(wx, wy)
        cr.close_path()
        cr.stroke()
        cr.set_dash([])

        # Neon Holo-Checkpoint Diamond Gate & Traffic Cones along track
        if len(lab.waypoints) >= 6:
            cpx, cpy = lab.waypoints[len(lab.waypoints) // 2]
            cr.save()
            cr.translate(cpx, cpy)
            cr.rotate(0.45)
            cr.set_source_rgba(0.15, 0.98, 0.55, 0.25)
            cr.rectangle(-12, -12, 24, 24)
            cr.fill_preserve()
            cr.set_source_rgba(0.25, 1.0, 0.65, 0.85)
            cr.set_line_width(1.6)
            cr.stroke()
            cr.restore()

        # 3. Translucent Fan-Shaped Green/Cyan LIDAR Radar Cones from Leader Car
        leader = lab.get_leader()
        if leader.alive and len(leader.rays) >= 2:
            # Fill translucent radar wedges between adjacent rays
            for i in range(len(leader.rays) - 1):
                rx1, ry1, nd1 = leader.rays[i]
                rx2, ry2, nd2 = leader.rays[i + 1]
                cr.new_path()
                cr.move_to(leader.x, leader.y)
                cr.line_to(rx1, ry1)
                cr.line_to(rx2, ry2)
                cr.close_path()
                if i % 2 == 0:
                    cr.set_source_rgba(0.10, 0.96, 0.65, 0.24)
                else:
                    cr.set_source_rgba(0.12, 0.82, 0.98, 0.22)
                cr.fill()

            # Crisp LIDAR beam lines & glowing wall-hit dots
            cr.set_line_width(1.5)
            for rx, ry, nd in leader.rays:
                cr.set_source_rgba(0.20, 0.98, 0.78, 0.78)
                cr.move_to(leader.x, leader.y)
                cr.line_to(rx, ry)
                cr.stroke()
                cr.new_path()
                cr.set_source_rgba(0.55, 1.0, 0.85, 0.95)
                cr.arc(rx, ry, 2.6, 0, 2 * math.pi)
                cr.fill()

        # 4. Render Cars (Cute Cyber Robot Car for Leader)
        for car in lab.cars:
            if not car.alive and car is not leader:
                continue
            is_lead = (car is leader)
            cr.save()
            cr.translate(car.x, car.y)
            cr.rotate(car.heading)
            if is_lead:
                # Outer cyan glow
                cr.set_source_rgba(0.15, 0.95, 0.80, 0.35)
                cr.rectangle(-12, -7, 24, 14)
                cr.fill()
                # Main cyber car chassis
                cr.set_source_rgb(0.18, 0.68, 0.96)
                cr.rectangle(-10, -5.5, 20, 11)
                cr.fill_preserve()
                cr.set_source_rgb(0.55, 0.98, 0.90)
                cr.set_line_width(1.4)
                cr.stroke()
                # Glowing cyan eyes / headlights on front
                cr.set_source_rgb(0.65, 1.0, 0.95)
                cr.arc(7, -2.8, 1.8, 0, 2 * math.pi)
                cr.arc(7, 2.8, 1.8, 0, 2 * math.pi)
                cr.fill()
            else:
                cr.set_source_rgba(0.30, 0.62, 0.90, 0.35)
                cr.rectangle(-8, -4.5, 16, 9)
                cr.fill()
            cr.restore()

        # 5. Corner HUD Overlays: [((•)) LIDAR ACTIVE], [SPEED Gauge], [Mini Radar Scope]
        # Top-Right: ((•)) LIDAR ACTIVE badge
        cr.set_source_rgba(0.04, 0.22, 0.24, 0.88)
        cr.rectangle(lab.width - 118, 10, 106, 22)
        cr.fill_preserve()
        cr.set_source_rgba(0.18, 0.96, 0.75, 0.90)
        cr.set_line_width(1.3)
        cr.stroke()
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(8.5)
        cr.set_source_rgb(0.35, 1.0, 0.82)
        cr.move_to(lab.width - 110, 24)
        cr.show_text("((•)) LIDAR ACTIVE")

        # Bottom-Left: Circular Neon SPEED Gauge
        sp_cx, sp_cy, sp_r = 34.0, lab.height - 32.0, 22.0
        cr.new_path()
        cr.set_source_rgba(0.04, 0.14, 0.22, 0.88)
        cr.arc(sp_cx, sp_cy, sp_r, 0, 2 * math.pi)
        cr.fill_preserve()
        cr.set_source_rgba(0.18, 0.92, 0.78, 0.85)
        cr.set_line_width(1.8)
        cr.stroke()
        # Speed arc & needle
        spd_norm = min(1.0, getattr(leader, "speed", 3.5) / 6.0)
        needle_ang = math.pi * 0.8 + spd_norm * math.pi * 1.4
        cr.set_source_rgb(0.25, 1.0, 0.75)
        cr.set_line_width(2.0)
        cr.move_to(sp_cx, sp_cy)
        cr.line_to(sp_cx + math.cos(needle_ang) * (sp_r - 5), sp_cy + math.sin(needle_ang) * (sp_r - 5))
        cr.stroke()
        cr.set_font_size(6.5)
        cr.move_to(sp_cx - 11, sp_cy + sp_r - 4)
        cr.show_text("SPEED")

        # Bottom-Right: Mini Rotating Radar Scope
        rd_cx, rd_cy, rd_r = lab.width - 34.0, lab.height - 32.0, 22.0
        cr.new_path()
        cr.set_source_rgba(0.04, 0.18, 0.16, 0.88)
        cr.arc(rd_cx, rd_cy, rd_r, 0, 2 * math.pi)
        cr.fill_preserve()
        cr.set_source_rgba(0.18, 0.95, 0.65, 0.85)
        cr.set_line_width(1.6)
        cr.stroke()
        cr.new_path()
        cr.set_source_rgba(0.18, 0.95, 0.65, 0.30)
        cr.arc(rd_cx, rd_cy, rd_r * 0.55, 0, 2 * math.pi)
        cr.stroke()
        sweep_a = phase * 2.2
        cr.set_source_rgba(0.25, 1.0, 0.70, 0.90)
        cr.move_to(rd_cx, rd_cy)
        cr.line_to(rd_cx + math.cos(sweep_a) * rd_r, rd_cy + math.sin(sweep_a) * rd_r)
        cr.stroke()

        cr.restore()

    def _render_rl_gridworld(self, cr: cairo.Context, w: float, h: float) -> None:
        lab: RLGridWorldLab = self.labs["rl_gridworld"]
        pad = 26.0
        cw = (w - 2 * pad) / lab.cols
        ch = (h - 2 * pad) / lab.rows

        # Subtle background cyber-circuit traces
        cr.set_source_rgba(0.12, 0.55, 0.88, 0.16)
        cr.set_line_width(1.0)
        for c in range(lab.cols + 1):
            gx = pad + c * cw
            cr.move_to(gx, 6)
            cr.line_to(gx, h - 6)
        for r in range(lab.rows + 1):
            gy = pad + r * ch
            cr.move_to(6, gy)
            cr.line_to(w - 6, gy)
        cr.stroke()

        for c in range(lab.cols):
            for r in range(lab.rows):
                x = pad + c * cw
                y = pad + r * ch
                pos = (c, r)
                max_q = max(lab.q_table[pos])

                if pos == lab.goal_pos:
                    # Glowing Gold/Amber Treasure Tile (matching middle artwork!)
                    cr.set_source_rgba(0.98, 0.75, 0.18, 0.92)
                elif pos in lab.lava_cells:
                    # Glowing Purple/Crimson Hazard Tile
                    cr.set_source_rgba(0.58, 0.16, 0.68, 0.88)
                elif pos in lab.wall_cells:
                    cr.set_source_rgba(0.16, 0.22, 0.34, 0.92)
                else:
                    norm = max(-1.0, min(1.0, max_q / 100.0))
                    if norm >= 0:
                        cr.set_source_rgba(0.07, 0.16 + 0.52 * norm, 0.28 + 0.48 * norm, 0.92)
                    else:
                        cr.set_source_rgba(0.22 - 0.30 * norm, 0.10, 0.28, 0.90)

                cr.rectangle(x + 2, y + 2, cw - 4, ch - 4)
                cr.fill_preserve()
                # Neon tile border
                if pos == lab.goal_pos:
                    cr.set_source_rgba(1.0, 0.92, 0.45, 0.95)
                elif pos in lab.lava_cells:
                    cr.set_source_rgba(0.85, 0.38, 0.96, 0.85)
                else:
                    cr.set_source_rgba(0.22, 0.62, 0.92, 0.40)
                cr.set_line_width(1.3)
                cr.stroke()

                if pos not in lab.lava_cells and pos not in lab.wall_cells and pos != lab.goal_pos:
                    q_vals = lab.q_table[pos]
                    best_a = max(range(4), key=q_vals.__getitem__)
                    cr.set_source_rgba(0.45, 0.92, 1.0, 0.92)
                    cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                    cr.set_font_size(14)
                    cr.move_to(x + cw * 0.38, y + ch * 0.48)
                    cr.show_text(lab.ARROWS[best_a])

                    cr.set_font_size(9.5)
                    cr.set_source_rgba(0.70, 0.84, 0.96, 0.88)
                    cr.move_to(x + 5, y + ch - 6)
                    cr.show_text(f"{max_q:+.1f}")
                elif pos == lab.goal_pos:
                    cr.set_source_rgb(0.10, 0.12, 0.18)
                    cr.set_font_size(11.5)
                    cr.move_to(x + 6, y + ch * 0.56)
                    cr.show_text("★ GOAL")
                elif pos in lab.lava_cells:
                    cr.set_source_rgb(0.98, 0.82, 1.0)
                    cr.set_font_size(10)
                    cr.move_to(x + 8, y + ch * 0.56)
                    cr.show_text("HAZARD")

        ax = pad + (lab.agent_pos[0] + 0.5) * cw
        ay = pad + (lab.agent_pos[1] + 0.5) * ch
        cr.new_path()
        cr.set_source_rgba(0.18, 0.90, 1.0, 0.32)
        cr.arc(ax, ay, min(cw, ch) * 0.38, 0, 2 * math.pi)
        cr.fill()
        cr.new_path()
        cr.set_source_rgb(0.28, 0.92, 1.0)
        cr.arc(ax, ay, min(cw, ch) * 0.26, 0, 2 * math.pi)
        cr.fill()

    def _render_cartpole(self, cr: cairo.Context, w: float, h: float) -> None:
        lab: CartPoleLab = self.labs["cartpole_rl"]
        rail_y = h * 0.70
        scale_x = (w * 0.38) / lab.x_threshold

        cr.set_source_rgb(0.35, 0.42, 0.55)
        cr.set_line_width(3.0)
        cr.move_to(w * 0.08, rail_y)
        cr.line_to(w * 0.92, rail_y)
        cr.stroke()

        leader = lab.get_leader()
        for ag in lab.agents:
            if not ag.alive and ag is not leader:
                continue
            is_lead = (ag is leader)
            cx = w * 0.5 + ag.x * scale_x
            pole_px = lab.params["pole_length"] * 170.0
            px = cx + math.sin(ag.theta) * pole_px
            py = rail_y - math.cos(ag.theta) * pole_px

            if is_lead:
                cr.set_source_rgba(0.22, 0.78, 0.98, 1.0)
                cr.rectangle(cx - 26, rail_y - 14, 52, 28)
                cr.fill()
                cr.set_source_rgba(0.98, 0.75, 0.22, 1.0)
                cr.set_line_width(5.0)
            else:
                cr.set_source_rgba(0.55, 0.65, 0.80, 0.22)
                cr.set_line_width(2.0)

            cr.move_to(cx, rail_y)
            cr.line_to(px, py)
            cr.stroke()

            if is_lead:
                cr.set_source_rgb(0.95, 0.35, 0.45)
                cr.arc(px, py, 7.0, 0, 2 * math.pi)
                cr.fill()

    def _render_nn_playground(self, cr: cairo.Context, w: float, h: float) -> None:
        lab: NeuralPlaygroundLab = self.labs["nn_playground"]
        grid_n = 30
        cw = w / grid_n
        ch = h / grid_n

        for gx in range(grid_n):
            x_val = ((gx + 0.5) / grid_n) * 2.0 - 1.0
            for gy in range(grid_n):
                y_val = 1.0 - ((gy + 0.5) / grid_n) * 2.0
                prob, _ = lab.predict_prob(x_val, y_val)
                dist_to_boundary = abs(prob - 0.5)
                if dist_to_boundary < 0.065:
                    # Glowing Gold/White Decision Boundary Contour (prob ~ 0.50)
                    glow = 1.0 - (dist_to_boundary / 0.065)
                    r_col = 0.25 + 0.72 * glow
                    g_col = 0.55 + 0.42 * glow
                    b_col = 0.65 + 0.30 * glow
                else:
                    r_col = 0.62 * (1.0 - prob) + 0.06 * prob
                    g_col = 0.18 * (1.0 - prob) + 0.48 * prob
                    b_col = 0.24 * (1.0 - prob) + 0.78 * prob
                cr.set_source_rgb(r_col, g_col, b_col)
                cr.rectangle(gx * cw, gy * ch, cw + 1.2, ch + 1.2)
                cr.fill()

        # Subtle coordinate crosshair grid
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.12)
        cr.set_line_width(1.0)
        cr.move_to(w * 0.5, 0)
        cr.line_to(w * 0.5, h)
        cr.move_to(0, h * 0.5)
        cr.line_to(w, h * 0.5)
        cr.stroke()

        # Draw swirling sample points with classification status halo
        for x, y, label in lab.samples:
            sx = (x + 1.0) * 0.5 * w
            sy = (1.0 - (y + 1.0) * 0.5) * h
            prob, _ = lab.predict_prob(x, y)
            is_correct = (prob >= 0.5) == (label >= 0.5)

            cr.new_path()
            if is_correct:
                cr.set_source_rgba(0.98, 0.98, 1.0, 0.95)
                cr.arc(sx, sy, 5.6, 0, 2 * math.pi)
            else:
                # Pulsing yellow ring on misclassified points being learned
                cr.set_source_rgba(1.0, 0.90, 0.20, 0.95)
                cr.arc(sx, sy, 7.2, 0, 2 * math.pi)
            cr.fill()

            cr.new_path()
            if label > 0.5:
                cr.set_source_rgb(0.12, 0.88, 1.0)
            else:
                cr.set_source_rgb(1.0, 0.36, 0.26)
            cr.arc(sx, sy, 4.0, 0, 2 * math.pi)
            cr.fill()

        # Top HUD Banner showing active dataset, neuron count, and live sorting accuracy
        dtype = int(round(lab.params.get("dataset_id", 2)))
        dname = lab.DATASET_NAMES.get(dtype, "Custom")
        cr.set_source_rgba(0.04, 0.08, 0.16, 0.84)
        cr.rectangle(10, h - 34, w - 20, 26)
        cr.fill_preserve()
        cr.set_source_rgba(0.25, 0.78, 0.98, 0.75)
        cr.set_line_width(1.2)
        cr.stroke()

        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(11.5)
        cr.set_source_rgb(0.95, 0.98, 1.0)
        hud_txt = (
            f"Pattern: {dname}   |   Hidden Neurons: {len(lab.w1)}   |   "
            f"Sorted Accuracy: {lab.accuracy:.1f}%   |   Epoch: #{lab.epoch}"
        )
        cr.move_to(18, h - 16)
        cr.show_text(hud_txt)

    def _render_swarm(self, cr: cairo.Context, w: float, h: float) -> None:
        lab: SwarmEcosystemLab = self.labs["swarm_ecosystem"]
        sx, sy = w / lab.width, h / lab.height
        cr.save()
        cr.scale(sx, sy)

        cr.set_source_rgb(0.25, 0.92, 0.45)
        for fx, fy in lab.foods:
            cr.arc(fx, fy, 3.2, 0, 2 * math.pi)
            cr.fill()

        cr.set_source_rgb(0.25, 0.80, 0.98)
        for p in lab.prey:
            ang = math.atan2(p.vy, p.vx)
            cr.save()
            cr.translate(p.x, p.y)
            cr.rotate(ang)
            cr.move_to(6, 0)
            cr.line_to(-4, -3.5)
            cr.line_to(-4, 3.5)
            cr.close_path()
            cr.fill()
            cr.restore()

        for pred in lab.predators:
            cr.set_source_rgba(0.95, 0.25, 0.30, 0.15)
            cr.arc(pred.x, pred.y, lab.params["vision_radius"], 0, 2 * math.pi)
            cr.stroke()

            ang = math.atan2(pred.vy, pred.vx)
            cr.save()
            cr.translate(pred.x, pred.y)
            cr.rotate(ang)
            cr.set_source_rgb(0.98, 0.28, 0.32)
            cr.move_to(9, 0)
            cr.line_to(-6, -5)
            cr.line_to(-6, 5)
            cr.close_path()
            cr.fill()
            cr.restore()

        cr.restore()

    def _render_prime_attention(self, cr: cairo.Context, w: float, h: float) -> None:
        """
        Intuitive 3-Stage Animated Visual Guide for PRIME Moment Sliding-Window Attention:
        Stage 1 (Top): Animated Token Stream Conveyor Belt -> Local Sliding Window (W) -> O(1) PRIME Memory Vault (S0,S1,S2)
        Stage 2 (Middle): "Who Remembers the Secret Passkey?" Visual Recall Bars + Retention Curve
        Stage 3 (Bottom): Why It Fits on a Potato (67 KB PRIME State vs 288,000 KB Softmax KV-Cache)
        """
        lab: PrimeAttentionLab = self.labs["prime_attention"]
        telem = lab.get_telemetry()
        pad = 14.0
        w_tok = int(round(lab.params["window_size"]))
        gap_n = int(round(lab.params["distractor_gap"]))
        hyb_pct = telem["best_fitness"]
        win_pct = telem.get("win_fitness", 100.0 if gap_n <= w_tok else 0.0)
        lin_pct = telem["avg_fitness"]
        state_kb = telem["state_kb"]
        c_tps = telem["c_tokens_per_sec"]
        qk_on = int(round(lab.params["use_qk_norm"])) >= 1
        inside_window = gap_n <= w_tok

        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)

        # ======================================================================
        # STAGE 1 (TOP BANNER): HOW PRIME MOMENT ATTENTION WORKS (LIVE FLOW)
        # ======================================================================
        s1_y = pad
        s1_h = h * 0.34
        cr.set_source_rgb(0.08, 0.11, 0.17)
        cr.rectangle(pad, s1_y, w - 2 * pad, s1_h)
        cr.fill()
        cr.set_source_rgba(0.22, 0.74, 0.98, 0.45)
        cr.set_line_width(1.2)
        cr.rectangle(pad, s1_y, w - 2 * pad, s1_h)
        cr.stroke()

        cr.set_source_rgb(0.95, 0.98, 1.0)
        cr.set_font_size(11.0)
        cr.move_to(pad + 10, s1_y + 19)
        cr.show_text(
            f"HOW IT WORKS: Passkey 'KEY: 7492' spoken {gap_n} tok ago (Sliding Window W = {w_tok} tok)"
        )

        # Draw 3 Visual Zones left-to-right inside Stage 1:
        # Zone A (Left): Old Evicted Tokens + PRIME Memory Vault (S0, S1, S2)
        # Zone B (Center): Local Sliding Window (Last W tokens)
        # Zone C (Right): Current Question ("What was the KEY?")
        zone_y = s1_y + 28
        zone_h = s1_h - 36
        inner_w = w - 2 * pad - 20

        vault_x = pad + 10
        vault_w = inner_w * 0.36
        win_x = vault_x + vault_w + 10
        win_w = inner_w * 0.36
        query_x = win_x + win_w + 10
        query_w = inner_w - vault_w - win_w - 20

        # --- ZONE A: O(1) PRIME MOMENT VAULT (Captures tokens evicted from Window) ---
        cr.set_source_rgba(0.08, 0.24, 0.18, 0.85)
        cr.rectangle(vault_x, zone_y, vault_w, zone_h)
        cr.fill()
        cr.set_source_rgb(0.20, 0.92, 0.50)
        cr.set_line_width(2.0)
        cr.rectangle(vault_x, zone_y, vault_w, zone_h)
        cr.stroke()

        cr.set_source_rgb(0.30, 0.98, 0.60)
        cr.set_font_size(10.0)
        cr.move_to(vault_x + 6, zone_y + 16)
        cr.show_text(f"1. PRIME Vault ({state_kb} KB)")

        cr.set_source_rgb(0.80, 0.92, 0.85)
        cr.set_font_size(8.8)
        cr.move_to(vault_x + 6, zone_y + 30)
        cr.show_text("S0, S1, S2 Taylor Moments")

        # If passkey is outside window (gap_n > w_tok), show the GOLD PASSKEY stored inside the Vault!
        if not inside_window:
            pulse = 0.5 + 0.5 * math.sin(self._anim_phase * 2.0)
            cr.set_source_rgba(0.98, 0.80, 0.15, 0.85 + 0.15 * pulse)
            cr.rectangle(vault_x + 6, zone_y + 38, vault_w - 12, 24)
            cr.fill()
            cr.set_source_rgb(0.08, 0.08, 0.10)
            cr.set_font_size(9.2)
            cr.move_to(vault_x + 10, zone_y + 54)
            cr.show_text(f"★ IN VAULT: KEY=7492 ({gap_n}t)")
        else:
            cr.set_source_rgba(0.25, 0.38, 0.32, 0.8)
            cr.rectangle(vault_x + 6, zone_y + 38, vault_w - 12, 24)
            cr.fill()
            cr.set_source_rgb(0.75, 0.88, 0.80)
            cr.set_font_size(9.0)
            cr.move_to(vault_x + 10, zone_y + 54)
            cr.show_text("Vault ready (Passkey in Win ->)")

        # Mini live S2 Matrix bars inside Vault
        mat = lab.s2_heatmap
        bar_y = zone_y + zone_h - 8
        for idx_m in range(10):
            v_m = abs(mat[idx_m % len(mat)][(idx_m * 2) % len(mat[0])])
            bh_m = min(14.0, 3.0 + v_m * 12.0)
            cr.set_source_rgba(0.20, 0.95, 0.55, 0.75)
            cr.rectangle(vault_x + 8 + idx_m * ((vault_w - 16) / 10.0), bar_y - bh_m, 8, bh_m)
            cr.fill()

        # --- ZONE B: LOCAL SLIDING WINDOW (Keeps only the newest W tokens) ---
        cr.set_source_rgba(0.08, 0.18, 0.28, 0.85)
        cr.rectangle(win_x, zone_y, win_w, zone_h)
        cr.fill()
        cr.set_source_rgb(0.22, 0.74, 0.98)
        cr.set_line_width(2.0)
        cr.rectangle(win_x, zone_y, win_w, zone_h)
        cr.stroke()

        cr.set_source_rgb(0.38, 0.84, 1.0)
        cr.set_font_size(10.0)
        cr.move_to(win_x + 6, zone_y + 16)
        cr.show_text(f"2. Sliding Window (W={w_tok})")

        cr.set_source_rgb(0.78, 0.88, 0.98)
        cr.set_font_size(8.8)
        cr.move_to(win_x + 6, zone_y + 30)
        cr.show_text(f"Keeps newest {w_tok} words exact:")

        if inside_window:
            cr.set_source_rgb(0.98, 0.80, 0.15)
            cr.rectangle(win_x + 6, zone_y + 38, win_w - 12, 24)
            cr.fill()
            cr.set_source_rgb(0.08, 0.08, 0.10)
            cr.set_font_size(9.2)
            cr.move_to(win_x + 10, zone_y + 54)
            cr.show_text(f"★ IN WINDOW: KEY=7492 ({gap_n}<=W)")
        else:
            cr.set_source_rgba(0.65, 0.18, 0.22, 0.85)
            cr.rectangle(win_x + 6, zone_y + 38, win_w - 12, 24)
            cr.fill()
            cr.set_source_rgb(1.0, 0.85, 0.85)
            cr.set_font_size(9.0)
            cr.move_to(win_x + 10, zone_y + 54)
            cr.show_text(f"✗ EVICTED! ({gap_n} > W={w_tok})")

        # Animated scrolling distractor tokens inside the window
        scroll_off = int(self._anim_phase * 3.0) % 100
        cr.set_source_rgb(0.55, 0.72, 0.90)
        cr.set_font_size(8.5)
        cr.move_to(win_x + 6, zone_y + zone_h - 8)
        cr.show_text(f"Stream: ..w_{scroll_off+1} -> w_{scroll_off+2} -> w_{scroll_off+3}")

        # --- ZONE C: LIVE QUERY & RECALL RESULT ---
        cr.set_source_rgba(0.16, 0.14, 0.26, 0.90)
        cr.rectangle(query_x, zone_y, query_w, zone_h)
        cr.fill()
        cr.set_source_rgb(0.75, 0.55, 0.98)
        cr.set_line_width(2.0)
        cr.rectangle(query_x, zone_y, query_w, zone_h)
        cr.stroke()

        cr.set_source_rgb(0.88, 0.78, 1.0)
        cr.set_font_size(10.0)
        cr.move_to(query_x + 6, zone_y + 16)
        cr.show_text("3. AI Query Now:")

        cr.set_source_rgb(0.95, 0.95, 1.0)
        cr.set_font_size(8.8)
        cr.move_to(query_x + 6, zone_y + 30)
        cr.show_text("\"What was KEY?\"")

        recalled_ok = hyb_pct >= 30.0
        if recalled_ok:
            cr.set_source_rgb(0.18, 0.88, 0.48)
            cr.rectangle(query_x + 6, zone_y + 38, query_w - 12, 24)
            cr.fill()
            cr.set_source_rgb(0.05, 0.08, 0.06)
            cr.set_font_size(9.2)
            cr.move_to(query_x + 9, zone_y + 54)
            cr.show_text(f"✓ KEY=7492 ({hyb_pct:.0f}%)")
        else:
            cr.set_source_rgb(0.85, 0.22, 0.28)
            cr.rectangle(query_x + 6, zone_y + 38, query_w - 12, 24)
            cr.fill()
            cr.set_source_rgb(1.0, 0.92, 0.92)
            cr.set_font_size(9.2)
            cr.move_to(query_x + 9, zone_y + 54)
            cr.show_text(f"✗ LOST ({hyb_pct:.0f}%)")

        # Draw animated Recall Beam from Vault (or Window) to Query box
        if recalled_ok:
            beam_src_x = (win_x + win_w * 0.5) if inside_window else (vault_x + vault_w * 0.5)
            beam_dst_x = query_x + 10
            beam_y = zone_y + zone_h - 3
            cr.set_source_rgba(0.25, 0.98, 0.55, 0.85)
            cr.set_line_width(2.0)
            cr.move_to(beam_src_x, beam_y)
            cr.line_to(beam_dst_x, beam_y)
            cr.stroke()
            # Moving pulse dot along the recall beam
            t_pulse = (self._anim_phase * 0.4) % 1.0
            px_dot = beam_src_x + t_pulse * (beam_dst_x - beam_src_x)
            cr.set_source_rgb(1.0, 0.95, 0.30)
            cr.arc(px_dot, beam_y, 4.0, 0, 2 * math.pi)
            cr.fill()

        # ======================================================================
        # STAGE 2 (MIDDLE SPLIT): SCOREBOARD BARS (LEFT) + RETENTION CURVE (RIGHT)
        # ======================================================================
        s2_y = s1_y + s1_h + 8.0
        s2_h = h * 0.42
        left_w = (w - 2 * pad - 10.0) * 0.52
        right_x = pad + left_w + 10.0
        right_w = w - right_x - pad

        # --- LEFT CARD: WHO REMEMBERS THE PASSKEY AT GAP N? ---
        cr.set_source_rgb(0.09, 0.11, 0.16)
        cr.rectangle(pad, s2_y, left_w, s2_h)
        cr.fill()

        cr.set_source_rgb(0.95, 0.98, 1.0)
        cr.set_font_size(10.5)
        cr.move_to(pad + 8, s2_y + 18)
        cr.show_text(f"Recall Scoreboard (Gap N = {gap_n} Words)")

        bars = [
            (
                "1. Hybrid Win + PRIME (Ours)",
                hyb_pct,
                (0.20, 0.92, 0.50),
                "Keeps recent words + old keys in 67 KB!",
            ),
            (
                f"2. Window Only (W = {w_tok})",
                win_pct,
                (0.22, 0.74, 0.98) if win_pct > 50 else (0.92, 0.28, 0.32),
                "100% if N<=W, drops to 0% when N>W!",
            ),
            (
                "3. Linear Attention (ELU+1)",
                lin_pct,
                (0.98, 0.80, 0.20),
                "1st-order state blurs as N grows.",
            ),
        ]

        by_cursor = s2_y + 34.0
        bar_max_w = left_w - 18.0
        for b_title, b_pct, (br, bg, bb), b_sub in bars:
            cr.set_source_rgb(0.90, 0.94, 0.98)
            cr.set_font_size(9.8)
            cr.move_to(pad + 9, by_cursor)
            cr.show_text(f"{b_title}: {b_pct:.1f}%")

            # Background track
            cr.set_source_rgb(0.15, 0.18, 0.25)
            cr.rectangle(pad + 9, by_cursor + 4, bar_max_w, 11)
            cr.fill()

            # Filled bar
            fill_w = max(4.0, (b_pct / 100.0) * bar_max_w)
            cr.set_source_rgb(br, bg, bb)
            cr.rectangle(pad + 9, by_cursor + 4, fill_w, 11)
            cr.fill()

            cr.set_source_rgb(0.65, 0.74, 0.86)
            cr.set_font_size(8.5)
            cr.move_to(pad + 9, by_cursor + 26)
            cr.show_text(b_sub)
            by_cursor += 42.0

        # --- RIGHT CARD: RETENTION CURVE ACROSS ALL GAPS (32 .. 1024) ---
        cr.set_source_rgb(0.09, 0.11, 0.16)
        cr.rectangle(right_x, s2_y, right_w, s2_h)
        cr.fill()

        cr.set_source_rgb(0.90, 0.95, 1.0)
        cr.set_font_size(10.0)
        cr.move_to(right_x + 8, s2_y + 18)
        cr.show_text("Recall vs Distance (32..1024 Tok)")

        gx0, gy0 = right_x + 30.0, s2_y + 30.0
        gw, gh = right_w - 42.0, s2_h - 50.0

        cr.set_source_rgba(0.3, 0.35, 0.45, 0.4)
        cr.set_line_width(1.0)
        cr.set_font_size(8.5)
        for frac in (0.0, 0.5, 1.0):
            yy = gy0 + gh * (1.0 - frac)
            cr.move_to(gx0, yy)
            cr.line_to(gx0 + gw, yy)
            cr.stroke()
            cr.move_to(right_x + 3, yy + 3)
            cr.show_text(f"{int(frac*100)}%")

        gaps = lab.GAPS
        active_gap_idx = min(range(len(gaps)), key=lambda i: abs(gaps[i] - gap_n))
        for idx, gval in enumerate(gaps):
            xx = gx0 + (idx / max(1, len(gaps) - 1)) * gw
            if idx == active_gap_idx:
                cr.set_source_rgba(0.98, 0.85, 0.25, 0.35)
                cr.set_line_width(2.0)
                cr.move_to(xx, gy0)
                cr.line_to(xx, gy0 + gh)
                cr.stroke()
            cr.set_source_rgb(0.75, 0.82, 0.92)
            cr.move_to(xx - 9, gy0 + gh + 12)
            cr.show_text(str(gval))

        def draw_curve(vals: List[float], r: float, g: float, b: float, lw: float) -> None:
            cr.set_source_rgb(r, g, b)
            cr.set_line_width(lw)
            for i, v in enumerate(vals):
                px = gx0 + (i / max(1, len(vals) - 1)) * gw
                py = gy0 + gh * (1.0 - max(0.0, min(1.0, v)))
                if i == 0:
                    cr.move_to(px, py)
                else:
                    cr.line_to(px, py)
            cr.stroke()
            for i, v in enumerate(vals):
                px = gx0 + (i / max(1, len(vals) - 1)) * gw
                py = gy0 + gh * (1.0 - max(0.0, min(1.0, v)))
                cr.arc(px, py, 2.8, 0, 2 * math.pi)
                cr.fill()

        draw_curve(lab.curve_linear_elu, 0.98, 0.80, 0.20, 1.6)
        draw_curve(lab.curve_window_only, 0.22, 0.74, 0.98, 1.8)
        draw_curve(lab.curve_hybrid, 0.20, 0.92, 0.50, 2.8)

        # ======================================================================
        # STAGE 3 (BOTTOM BAR): POTATO RAM SAVINGS & NATIVE C99 SPEED
        # ======================================================================
        by0 = s2_y + s2_h + 8.0
        bh = max(62.0, h - by0 - pad)
        cr.set_source_rgb(0.08, 0.10, 0.15)
        cr.rectangle(pad, by0, w - 2 * pad, bh)
        cr.fill()

        cr.set_source_rgb(0.22, 0.82, 0.98)
        cr.set_font_size(10.2)
        cr.move_to(pad + 10, by0 + 16)
        cr.show_text(
            f"POTATO RAM SAVINGS: C99 Kernel = {c_tps:,.0f} tok/s | PRIME = {state_kb} KB vs 288,000 KB Softmax"
        )

        bar_x0 = pad + 315
        max_ram_w = max(40.0, w - bar_x0 - pad - 16)
        cr.set_font_size(9.5)
        cr.set_source_rgb(0.95, 0.35, 0.35)
        cr.move_to(pad + 10, by0 + 34)
        cr.show_text("16K Softmax KV-Cache: 288,000 KB")
        cr.rectangle(bar_x0, by0 + 24, max_ram_w, 10)
        cr.fill()

        cr.set_source_rgb(0.20, 0.92, 0.50)
        cr.move_to(pad + 10, by0 + 50)
        cr.show_text(f"PRIME + Window (Ours): {state_kb:>6.1f} KB (99.97% Saved!)")
        cr.rectangle(bar_x0, by0 + 40, 10.0, 10)
        cr.fill()

        cr.set_source_rgb(0.98, 0.82, 0.25) if qk_on else cr.set_source_rgb(0.98, 0.30, 0.30)
        cr.set_font_size(9.0)
        cr.move_to(pad + 10, by0 + 66)
        status_qk = (
            "✓ QK-Norm ON (1): Bounds Taylor P(x)=1+x+0.5*x^2 so distractors never explode!"
            if qk_on
            else "✗ WARNING — QK-Norm OFF (0): Parabolic rebound P(x)=1+x+0.5*x^2 amplifies noise 6x!"
        )
        cr.show_text(status_qk)

    # ==========================================================================
    # CAIRO ANIMATED CORTEX-PHI3 BRAIN + ACTIVE LAB NEURAL TOPOLOGY RENDERER
    # ==========================================================================
    def _draw_net_canvas(self, widget: Gtk.DrawingArea, cr: cairo.Context) -> bool:
        alloc = widget.get_allocation()
        w, h = float(alloc.width), float(alloc.height)

        cr.set_source_rgb(0.06, 0.08, 0.11)
        cr.paint()

        # Section 1 (Top 43%): Animated Cortex-Phi3 + PRIME Moment Neural Brain
        phi_h = h * 0.43
        self._render_phi3_brain_animation(cr, 8.0, 6.0, w - 16.0, phi_h - 8.0)

        # Section 2 (Middle 34%): Active Lab Neural Network Topology (+ / - Neurons live!)
        mid_y = phi_h + 2.0
        mid_h = h * 0.34
        lab = self.active_lab
        if hasattr(lab, "neat"):
            leader = lab.get_leader()
            self._render_neat_genome(cr, leader.genome, 8.0, mid_y + 14.0, w - 16.0, mid_h - 18.0)
        elif hasattr(lab, "w1"):
            self._render_mlp_network(cr, lab, 8.0, mid_y + 14.0, w - 16.0, mid_h - 18.0)
        else:
            self._render_policy_network(cr, lab, 8.0, mid_y + 14.0, w - 16.0, mid_h - 18.0)

        # Section 3 (Bottom 23%): Convergence / Fitness Curve
        bot_y = mid_y + mid_h + 2.0
        bot_h = h - bot_y - 8.0
        self._render_fitness_chart(cr, lab, 8.0, bot_y, w - 16.0, max(50.0, bot_h))
        return False

    def _render_phi3_brain_animation(self, cr: cairo.Context, x0: float, y0: float, bw: float, bh: float) -> None:
        """Draws a 60 FPS animated neural diagram of Cortex-Phi3 + PRIME Moment Attention working live."""
        m = self.cortex.last_llm_metrics
        is_active = bool(m.get("active", False))
        gen_tps = m.get("gen_tps", 0.0) or 24.8
        ttft_ms = m.get("ttft_ms", 0.0) or 280.0
        prime_kb = m.get("prime_state_kb", 67.1)

        cr.set_source_rgb(0.09, 0.12, 0.18)
        cr.rectangle(x0, y0, bw, bh)
        cr.fill()

        border_col = (0.98, 0.80, 0.20) if is_active else (0.22, 0.74, 0.98)
        cr.set_source_rgba(border_col[0], border_col[1], border_col[2], 0.65)
        cr.set_line_width(1.6 if is_active else 1.0)
        cr.rectangle(x0, y0, bw, bh)
        cr.stroke()

        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(9.8)
        status_tag = "⚡ GENERATING" if is_active else "● ONLINE"
        cr.set_source_rgb(0.98, 0.85, 0.25) if is_active else cr.set_source_rgb(0.30, 0.92, 0.55)
        cr.move_to(x0 + 6, y0 + 15)
        cr.show_text(f"Cortex-Phi3 (3.8B) + PRIME Brain [{status_tag}]")

        cr.set_font_size(8.6)
        cr.set_source_rgb(0.75, 0.85, 0.96)
        cr.move_to(x0 + 6, y0 + 28)
        cr.show_text(
            f"Phi-3: {gen_tps:.1f} tok/s | TTFT {ttft_ms:.0f}ms | PRIME {prime_kb:.0f}KB | {self.live_fps:.0f} FPS"
        )

        # 5 Columns of the Phi-3 + PRIME Brain:
        # Col 0: Prompt Embed (4 nodes)
        # Col 1: Sliding Window W (4 nodes)
        # Col 2: PRIME Moment S0,S1,S2 Rings (3 glowing vault nodes)
        # Col 3: Phi-3 32 Attention Heads (6 nodes)
        # Col 4: Output Token Stream (3 nodes)
        col_counts = [4, 4, 3, 6, 3]
        col_labels = ["Input", "Win(W)", "PRIME", "Phi-3(32H)", "Output"]
        col_x = [x0 + 24.0 + (i / 4.0) * (bw - 48.0) for i in range(5)]
        net_y0 = y0 + 38.0
        net_h = bh - 62.0

        positions: List[List[Tuple[float, float]]] = []
        for c_idx, cnt in enumerate(col_counts):
            col_pts: List[Tuple[float, float]] = []
            for r_idx in range(cnt):
                ny = net_y0 + ((r_idx + 0.5) / cnt) * net_h
                col_pts.append((col_x[c_idx], ny))
            positions.append(col_pts)

        speed_mult = 2.6 if is_active else 1.0
        phase = self._anim_phase * speed_mult

        # Draw synaptic connections & traveling energy pulses between columns
        for c_idx in range(4):
            src_list = positions[c_idx]
            dst_list = positions[c_idx + 1]
            for i_s, (sx, sy) in enumerate(src_list):
                for i_d, (dx, dy) in enumerate(dst_list):
                    wave = math.sin(phase + c_idx * 1.1 + i_s * 0.7 + i_d * 0.5)
                    if wave > -0.2:
                        alpha = (0.25 + 0.45 * max(0.0, wave)) if is_active else (0.12 + 0.25 * max(0.0, wave))
                        if c_idx == 1:
                            cr.set_source_rgba(0.20, 0.95, 0.55, alpha)  # PRIME Vault green wires
                        elif c_idx == 2:
                            cr.set_source_rgba(0.98, 0.80, 0.22, alpha)  # Moment -> Phi-3 gold wires
                        else:
                            cr.set_source_rgba(0.25, 0.78, 0.98, alpha)  # Transformer cyan wires
                        cr.set_line_width(1.2 if is_active else 0.8)
                        cr.move_to(sx, sy)
                        cr.line_to(dx, dy)
                        cr.stroke()

                        # Traveling pulse particle on active waves
                        if wave > 0.55:
                            t_p = (phase * 0.35 + i_s * 0.23 + i_d * 0.17) % 1.0
                            px = sx + t_p * (dx - sx)
                            py = sy + t_p * (dy - sy)
                            cr.set_source_rgba(1.0, 0.96, 0.45, 0.9)
                            cr.arc(px, py, 2.4 if is_active else 1.8, 0, 2 * math.pi)
                            cr.fill()

        # Draw column nodes and labels
        for c_idx, col_pts in enumerate(positions):
            cr.set_font_size(8.2)
            cr.set_source_rgb(0.65, 0.76, 0.88)
            cr.move_to(col_x[c_idx] - 16, y0 + bh - 17)
            cr.show_text(col_labels[c_idx])

            for r_idx, (nx, ny) in enumerate(col_pts):
                act = 0.5 + 0.5 * math.sin(phase * 1.3 + c_idx * 0.9 + r_idx * 1.1)
                if c_idx == 2:
                    # PRIME S0, S1, S2 Moment Rings
                    cr.set_source_rgba(0.20, 0.95, 0.55, 0.35 + 0.4 * act)
                    cr.arc(nx, ny, 8.0, 0, 2 * math.pi)
                    cr.fill()
                    cr.set_source_rgb(0.25, 0.98, 0.60)
                    cr.arc(nx, ny, 4.8, 0, 2 * math.pi)
                    cr.fill()
                elif c_idx == 3:
                    # Phi-3 Attention Heads
                    cr.set_source_rgb(0.22 + 0.75 * act, 0.65 + 0.30 * act, 0.98)
                    cr.arc(nx, ny, 4.8, 0, 2 * math.pi)
                    cr.fill()
                else:
                    cr.set_source_rgb(0.25 + 0.60 * act, 0.75, 0.95)
                    cr.arc(nx, ny, 4.2, 0, 2 * math.pi)
                    cr.fill()

        # Snippet of last Cortex-Phi3 thought at the bottom of the Phi-3 brain card
        snippet = m.get("last_response_snippet", "Ready for Chat, AI Tutor, or Linux Cmds!")
        if len(snippet) > 44:
            snippet = snippet[:41] + "..."
        cr.set_font_size(8.5)
        cr.set_source_rgb(0.90, 0.94, 0.98)
        cr.move_to(x0 + 6, y0 + bh - 4)
        cr.show_text(f"▸ Phi-3: {self._clean_bmp(snippet)}")

    def _render_mlp_network(self, cr: cairo.Context, lab: NeuralPlaygroundLab, x0: float, y0: float, gw: float, gh: float) -> None:
        h_count = len(lab.w1)
        f_count = int(round(lab.params.get("synapse_density", 4.0)))
        cr.set_source_rgb(0.65, 0.82, 0.98)
        cr.set_font_size(9.5)
        cr.move_to(x0, y0 - 3)
        cr.show_text(f"Lab MLP Brain ({f_count} In -> {h_count} Hidden -> 1 Out)")

        in_pts = [(x0 + 24.0, y0 + 10.0 + ((i + 0.5) / f_count) * (gh - 16.0)) for i in range(f_count)]
        vis_h = min(14, h_count)
        hid_pts = [(x0 + gw * 0.52, y0 + 6.0 + ((j + 0.5) / vis_h) * (gh - 10.0)) for j in range(vis_h)]
        out_pt = (x0 + gw - 24.0, y0 + gh * 0.5)

        for j, (hx, hy) in enumerate(hid_pts):
            for k, (ix, iy) in enumerate(in_pts):
                w_val = lab.w1[j][k]
                if w_val >= 0:
                    cr.set_source_rgba(0.20, 0.90, 0.45, 0.65)
                else:
                    cr.set_source_rgba(0.95, 0.28, 0.35, 0.65)
                cr.set_line_width(max(0.6, min(2.8, abs(w_val) * 1.1)))
                cr.move_to(ix, iy)
                cr.line_to(hx, hy)
                cr.stroke()

            w2_val = lab.w2[j]
            if w2_val >= 0:
                cr.set_source_rgba(0.20, 0.90, 0.45, 0.75)
            else:
                cr.set_source_rgba(0.95, 0.28, 0.35, 0.75)
            cr.set_line_width(max(0.8, min(3.0, abs(w2_val) * 1.2)))
            cr.move_to(hx, hy)
            cr.line_to(out_pt[0], out_pt[1])
            cr.stroke()

        for ix, iy in in_pts:
            cr.set_source_rgb(0.38, 0.82, 0.98)
            cr.arc(ix, iy, 5.0, 0, 2 * math.pi)
            cr.fill()
        for hx, hy in hid_pts:
            cr.set_source_rgb(0.98, 0.80, 0.22)
            cr.arc(hx, hy, 5.2, 0, 2 * math.pi)
            cr.fill()
        cr.set_source_rgb(0.25, 0.95, 0.55)
        cr.arc(out_pt[0], out_pt[1], 6.5, 0, 2 * math.pi)
        cr.fill()

    def _render_policy_network(self, cr: cairo.Context, lab: Any, x0: float, y0: float, gw: float, gh: float) -> None:
        cr.set_source_rgb(0.65, 0.82, 0.98)
        cr.set_font_size(9.5)
        cr.move_to(x0, y0 - 3)
        if hasattr(lab, "s2_heatmap"):
            h_cnt = int(round(lab.params.get("num_heads", 8.0)))
            d_cnt = int(round(lab.params.get("head_dim", 32.0)))
            cr.show_text(f"PRIME Topology ({h_cnt} Heads x D={d_cnt})")
            n_mid = min(12, h_cnt)
        elif hasattr(lab, "prey"):
            cr.show_text(f"Swarm Policy ({len(lab.prey)} Prey x 4 Genes)")
            n_mid = min(12, max(4, len(lab.prey) // 5))
        else:
            cr.show_text(f"RL Value Policy (70 States x 4 Actions)")
            n_mid = 8

        in_pts = [(x0 + 24.0, y0 + 10.0 + ((i + 0.5) / 4) * (gh - 16.0)) for i in range(4)]
        mid_pts = [(x0 + gw * 0.5, y0 + 8.0 + ((j + 0.5) / n_mid) * (gh - 12.0)) for j in range(n_mid)]
        out_pts = [(x0 + gw - 24.0, y0 + 10.0 + ((k + 0.5) / 4) * (gh - 16.0)) for k in range(4)]

        for i, (ix, iy) in enumerate(in_pts):
            for j, (mx, my) in enumerate(mid_pts):
                w_wave = math.sin(self._anim_phase + i * 0.8 + j * 0.5)
                cr.set_source_rgba(0.22, 0.85, 0.65, 0.25 + 0.35 * max(0.0, w_wave))
                cr.set_line_width(1.0)
                cr.move_to(ix, iy)
                cr.line_to(mx, my)
                cr.stroke()
        for j, (mx, my) in enumerate(mid_pts):
            for k, (ox, oy) in enumerate(out_pts):
                w_wave = math.cos(self._anim_phase + j * 0.6 + k * 0.9)
                cr.set_source_rgba(0.35, 0.78, 0.98, 0.25 + 0.35 * max(0.0, w_wave))
                cr.set_line_width(1.0)
                cr.move_to(mx, my)
                cr.line_to(ox, oy)
                cr.stroke()

        for pt_list, col in [(in_pts, (0.38, 0.82, 0.98)), (mid_pts, (0.98, 0.80, 0.22)), (out_pts, (0.25, 0.95, 0.55))]:
            cr.set_source_rgb(*col)
            for px, py in pt_list:
                cr.arc(px, py, 4.8, 0, 2 * math.pi)
                cr.fill()

    def _render_neat_genome(self, cr: cairo.Context, genome: Any, x0: float, y0: float, gw: float, gh: float) -> None:
        hidden_cnt = sum(1 for n in genome.nodes.values() if n.type == "hidden")
        enabled_cnt = sum(1 for c in genome.connections.values() if c.enabled)
        cr.set_source_rgb(0.65, 0.82, 0.98)
        cr.set_font_size(9.5)
        cr.move_to(x0, y0 - 3)
        cr.show_text(
            f"Lab Neural Brain (Nodes: {len(genome.nodes)} [{hidden_cnt} Hid] | Wires: {enabled_cnt})"
        )

        layers: Dict[float, List[Any]] = {}
        for n in genome.nodes.values():
            ly = round(n.layer, 3)
            layers.setdefault(ly, []).append(n)

        node_pos: Dict[int, Tuple[float, float]] = {}
        for ly, nlist in layers.items():
            nx = x0 + 18.0 + ly * (gw - 36.0)
            count = len(nlist)
            for i, node in enumerate(nlist):
                ny = y0 + 10.0 + ((i + 0.5) / max(1, count)) * (gh - 18.0)
                node_pos[node.id] = (nx, ny)

        for conn in genome.connections.values():
            if not conn.enabled:
                continue
            p1 = node_pos.get(conn.in_node)
            p2 = node_pos.get(conn.out_node)
            if not p1 or not p2:
                continue
            if conn.weight >= 0:
                cr.set_source_rgba(0.20, 0.90, 0.45, 0.75)
            else:
                cr.set_source_rgba(0.95, 0.28, 0.35, 0.75)
            cr.set_line_width(max(0.8, min(3.2, abs(conn.weight) * 1.1)))
            cr.move_to(p1[0], p1[1])
            cr.line_to(p2[0], p2[1])
            cr.stroke()

        for nid, (nx, ny) in node_pos.items():
            node = genome.nodes[nid]
            act = max(-1.0, min(1.0, node.last_activation))
            if node.type == "hidden":
                cr.set_source_rgb(0.98, 0.82, 0.20)
                cr.arc(nx, ny, 6.2, 0, 2 * math.pi)
                cr.fill()
            else:
                if act >= 0:
                    cr.set_source_rgb(0.18 + 0.75 * act, 0.55 + 0.40 * act, 0.95)
                else:
                    cr.set_source_rgb(0.95, 0.35 * (1.0 + act), 0.35)
                cr.arc(nx, ny, 5.2, 0, 2 * math.pi)
                cr.fill()

    def _render_fitness_chart(self, cr: cairo.Context, lab: Any, x0: float, y0: float, cw: float, ch: float) -> None:
        cr.set_source_rgb(0.10, 0.12, 0.17)
        cr.rectangle(x0, y0, cw, ch)
        cr.fill()

        best_hist = getattr(lab, "history_best", None) or (lab.neat.history_best if hasattr(lab, "neat") else [])
        avg_hist = getattr(lab, "history_avg", None) or (lab.neat.history_avg if hasattr(lab, "neat") else [])

        cr.set_source_rgb(0.65, 0.75, 0.88)
        cr.set_font_size(9.2)
        cr.move_to(x0 + 6, y0 + 13)
        cr.show_text("Convergence Curve (Green = Best, Yellow = Avg)")

        if len(best_hist) < 2:
            cr.set_source_rgba(0.5, 0.6, 0.7, 0.7)
            cr.set_font_size(8.8)
            cr.move_to(x0 + 8, y0 + ch * 0.58)
            cr.show_text("Click '⚡ Turbo +25 Gens' or run sim to plot curve...")
            return

        pts_best = best_hist[-40:]
        pts_avg = avg_hist[-40:]
        all_vals = pts_best + pts_avg
        vmin, vmax = min(all_vals), max(all_vals)
        span = max(1e-3, vmax - vmin)

        cr.set_source_rgba(0.95, 0.80, 0.20, 0.85)
        cr.set_line_width(1.5)
        for i, val in enumerate(pts_avg):
            px = x0 + 8.0 + (i / max(1, len(pts_avg) - 1)) * (cw - 16.0)
            py = y0 + ch - 8.0 - ((val - vmin) / span) * (ch - 24.0)
            if i == 0:
                cr.move_to(px, py)
            else:
                cr.line_to(px, py)
        cr.stroke()

        cr.set_source_rgba(0.20, 0.92, 0.50, 0.95)
        cr.set_line_width(2.0)
        for i, val in enumerate(pts_best):
            px = x0 + 8.0 + (i / max(1, len(pts_best) - 1)) * (cw - 16.0)
            py = y0 + ch - 8.0 - ((val - vmin) / span) * (ch - 24.0)
            if i == 0:
                cr.move_to(px, py)
            else:
                cr.line_to(px, py)
        cr.stroke()


def main():
    win = SynapseStudioWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    init_mode = os.environ.get("SYNAPSE_INITIAL_MODE", "kid").strip().lower()
    win.kid_mode = (init_mode != "pro")
    win._apply_ui_mode()
    win._populate_sliders()
    init_lab = os.environ.get("SYNAPSE_INITIAL_LAB", "").strip()
    if init_lab and init_lab in win.labs:
        win.lab_combo.set_active_id(init_lab)
        win._on_lab_changed(win.lab_combo)
    Gtk.main()


if __name__ == "__main__":
    main()
