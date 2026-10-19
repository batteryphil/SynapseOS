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
from workbench.curriculum import SCHOOL_CURRICULUM, get_lesson_by_id, verify_lesson_goal
from workbench.sandbox_runner import run_student_code
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
        if self._active_id != item_id:
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
        ("prime_attention", "⚡ 7. PRIME Moment Sliding-Window Attention (O(1) State)"),
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
        self.slider_widgets: Dict[str, Gtk.Scale] = {}
        self._updating_sliders = False

        self._build_ui()
        self._populate_sliders()
        self._refresh_lesson_view()
        self._load_lesson_coding_challenge()

        GLib.timeout_add(18, self._on_tick)

    @property
    def active_lab(self) -> Any:
        return self.labs[self.active_lab_id]

    def _build_ui(self) -> None:
        root_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        root_vbox.set_margin_top(6)
        root_vbox.set_margin_bottom(6)
        root_vbox.set_margin_start(6)
        root_vbox.set_margin_end(6)
        self.add(root_vbox)

        # --- TOP HEADER BAR ---
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        root_vbox.pack_start(header_box, False, False, 0)

        title_lbl = Gtk.Label()
        title_lbl.set_markup("<b><span size='large' foreground='#38bdf8'>⚡ SYNAPSE STUDIO</span></b>")
        header_box.pack_start(title_lbl, False, False, 4)

        self.lab_combo = SynapseDropdown()
        for lid, lname in self.LAB_CATALOG:
            self.lab_combo.append(lid, lname)
        self.lab_combo.set_active_id(self.active_lab_id)
        self.lab_combo.connect("changed", self._on_lab_changed)
        header_box.pack_start(self.lab_combo, False, False, 4)

        # Badge Status Pill
        self.badge_lbl = Gtk.Label()
        self._update_badge_header()
        header_box.pack_start(self.badge_lbl, False, False, 6)

        # Universal Continuum Skill Mode Switcher
        mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        header_box.pack_end(mode_box, False, False, 4)

        btn_school = Gtk.RadioButton.new_with_label_from_widget(None, "★ Tutorial")
        btn_school.connect("toggled", self._on_mode_toggled, "school")
        btn_play = Gtk.RadioButton.new_with_label_from_widget(btn_school, "◈ Playground")
        btn_play.connect("toggled", self._on_mode_toggled, "playground")
        btn_code = Gtk.RadioButton.new_with_label_from_widget(btn_school, "✎ Code")
        btn_code.connect("toggled", self._on_mode_toggled, "studio")
        btn_pro = Gtk.RadioButton.new_with_label_from_widget(btn_school, "⚙ Pro")
        btn_pro.connect("toggled", self._on_mode_toggled, "pro")

        mode_box.pack_start(btn_school, False, False, 2)
        mode_box.pack_start(btn_play, False, False, 2)
        mode_box.pack_start(btn_code, False, False, 2)
        mode_box.pack_start(btn_pro, False, False, 2)

        # --- MAIN WORKSPACE 3-COLUMN SPLIT ---
        main_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        root_vbox.pack_start(main_hbox, True, True, 0)

        # COLUMN 1: Variable Sliders & Simulation Controls
        left_frame = Gtk.Frame(label=" ⚙ 1. Variables (Point & Click) ")
        left_frame.set_size_request(240, -1)
        main_hbox.pack_start(left_frame, False, False, 0)

        left_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        left_vbox.set_margin_top(6)
        left_vbox.set_margin_bottom(6)
        left_vbox.set_margin_start(6)
        left_vbox.set_margin_end(6)
        left_frame.add(left_vbox)

        ctrl_grid = Gtk.Grid()
        ctrl_grid.set_column_spacing(4)
        ctrl_grid.set_row_spacing(4)
        left_vbox.pack_start(ctrl_grid, False, False, 0)

        self.btn_run = Gtk.Button(label="|| Pause Sim")
        self.btn_run.connect("clicked", self._on_toggle_run)
        ctrl_grid.attach(self.btn_run, 0, 0, 1, 1)

        btn_step = Gtk.Button(label=">| Step 1 Frame")
        btn_step.connect("clicked", self._on_step_once)
        ctrl_grid.attach(btn_step, 1, 0, 1, 1)

        btn_turbo = Gtk.Button(label="⚡ Turbo +25 Gens")
        btn_turbo.connect("clicked", self._on_turbo_evolve)
        ctrl_grid.attach(btn_turbo, 0, 1, 2, 1)

        btn_reset = Gtk.Button(label="↻ Reset Brain")
        btn_reset.connect("clicked", self._on_reset_lab)
        ctrl_grid.attach(btn_reset, 0, 2, 1, 1)

        btn_export = Gtk.Button(label="✎ Export .py")
        btn_export.connect("clicked", self._on_export_py)
        ctrl_grid.attach(btn_export, 1, 2, 1, 1)

        slider_scroll = Gtk.ScrolledWindow()
        slider_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        left_vbox.pack_start(slider_scroll, True, True, 0)

        self.sliders_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        slider_scroll.add(self.sliders_vbox)

        # COLUMN 2: 60 FPS Live Physics & Agent Viewport
        center_frame = Gtk.Frame(label=" ◈ 2. Real-Time Simulation Viewport (60 FPS Cairo) ")
        main_hbox.pack_start(center_frame, True, True, 0)

        center_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        center_frame.add(center_vbox)

        self.telemetry_lbl = Gtk.Label()
        self.telemetry_lbl.set_xalign(0.02)
        self.telemetry_lbl.set_line_wrap(True)
        center_vbox.pack_start(self.telemetry_lbl, False, False, 2)

        self.sim_canvas = Gtk.DrawingArea()
        self.sim_canvas.set_size_request(440, 360)
        self.sim_canvas.connect("draw", self._draw_sim_canvas)
        center_vbox.pack_start(self.sim_canvas, True, True, 0)

        # COLUMN 3: 3-Tab Right Panel (School Tutorials | Hands-On Coding | Brain & Curves)
        right_frame = Gtk.Frame(label=" ★ 3. School Tutorials, Code & Brain ")
        right_frame.set_size_request(365, -1)
        main_hbox.pack_start(right_frame, False, False, 0)

        self.right_notebook = Gtk.Notebook()
        right_frame.add(self.right_notebook)

        # --- TAB 0: FOLLOW-ALONG SCHOOL TUTORIALS ---
        school_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        school_vbox.set_margin_top(6)
        school_vbox.set_margin_bottom(6)
        school_vbox.set_margin_start(6)
        school_vbox.set_margin_end(6)

        lesson_lbl = Gtk.Label()
        lesson_lbl.set_xalign(0.0)
        lesson_lbl.set_markup("<b>★ Choose a Follow-Along AI Lesson:</b>")
        school_vbox.pack_start(lesson_lbl, False, False, 0)

        self.lesson_combo = SynapseDropdown()
        for les in SCHOOL_CURRICULUM:
            short_title = les["title"] if len(les["title"]) <= 34 else les["title"][:31] + "..."
            self.lesson_combo.append(les["id"], short_title)
        self.lesson_combo.set_active_id(self.active_lesson_id)
        self.lesson_combo.connect("changed", self._on_lesson_changed)
        school_vbox.pack_start(self.lesson_combo, False, False, 0)

        lesson_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        school_vbox.pack_start(lesson_btn_box, False, False, 0)

        btn_load_preset = Gtk.Button(label="▸ 1. Load Preset")
        btn_load_preset.connect("clicked", self._on_apply_lesson_preset)
        lesson_btn_box.pack_start(btn_load_preset, True, True, 0)

        btn_check_goal = Gtk.Button(label="✓ 2. Check Goal")
        btn_check_goal.connect("clicked", self._on_check_lesson_goal)
        lesson_btn_box.pack_start(btn_check_goal, True, True, 0)

        btn_open_challenge = Gtk.Button(label="✎ 3. Open Python Coding Challenge")
        btn_open_challenge.connect("clicked", self._on_open_lesson_coding)
        school_vbox.pack_start(btn_open_challenge, False, False, 0)

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
        code_vbox.set_margin_top(6)
        code_vbox.set_margin_bottom(6)
        code_vbox.set_margin_start(6)
        code_vbox.set_margin_end(6)

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
        out_scroll.set_size_request(-1, 120)
        out_frame.add(out_scroll)

        self.sandbox_out_view = Gtk.TextView()
        self.sandbox_out_view.set_editable(False)
        self.sandbox_out_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.sandbox_out_view.get_buffer().set_text(
            "✎ Edit the Python code above and click '▶ Run' to see what happens!"
        )
        out_scroll.add(self.sandbox_out_view)

        self.right_notebook.append_page(code_vbox, Gtk.Label(label="✎ Code"))

        # --- TAB 2: LIVE NEURAL TOPOLOGY & FITNESS CURVES ---
        viz_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.net_canvas = Gtk.DrawingArea()
        self.net_canvas.set_size_request(330, 340)
        self.net_canvas.connect("draw", self._draw_net_canvas)
        viz_vbox.pack_start(self.net_canvas, True, True, 0)
        self.right_notebook.append_page(viz_vbox, Gtk.Label(label="⚙ Brain"))

        # --- BOTTOM BAR: BUILT-IN CORTEX-PHI3 AI TUTOR ---
        cortex_frame = Gtk.Frame(label=" ⚡ 4. Built-in Cortex-Phi3 Classroom Tutor & Linux Guide ")
        root_vbox.pack_start(cortex_frame, False, False, 0)

        cortex_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        cortex_vbox.set_margin_top(4)
        cortex_vbox.set_margin_bottom(4)
        cortex_vbox.set_margin_start(6)
        cortex_vbox.set_margin_end(6)
        cortex_frame.add(cortex_vbox)

        query_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        cortex_vbox.pack_start(query_hbox, False, False, 0)

        self.cortex_entry = Gtk.Entry()
        self.cortex_entry.set_placeholder_text("Ask Cortex Tutor: e.g. 'Explain NEAT like I am 10' or 'How do I check RAM in Linux?'")
        self.cortex_entry.connect("activate", self._on_ask_cortex_fast)
        query_hbox.pack_start(self.cortex_entry, True, True, 0)

        btn_ask_fast = Gtk.Button(label="⚡ Instant Guide (<1ms)")
        btn_ask_fast.connect("clicked", self._on_ask_cortex_fast)
        query_hbox.pack_start(btn_ask_fast, False, False, 0)

        btn_ask_llm = Gtk.Button(label="★ Ask Cortex-Phi3")
        btn_ask_llm.connect("clicked", self._on_ask_cortex_llm)
        query_hbox.pack_start(btn_ask_llm, False, False, 0)

        btn_ask_cmd = Gtk.Button(label="⌘ Linux Cmd (??)")
        btn_ask_cmd.connect("clicked", self._on_ask_linux_cmd)
        query_hbox.pack_start(btn_ask_cmd, False, False, 0)

        cortex_out_scroll = Gtk.ScrolledWindow()
        cortex_out_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        cortex_out_scroll.set_size_request(-1, 85)
        cortex_vbox.pack_start(cortex_out_scroll, False, False, 0)

        self.cortex_text = Gtk.TextView()
        self.cortex_text.set_editable(False)
        self.cortex_text.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        cortex_out_scroll.add(self.cortex_text)
        self._set_cortex_message(
            "★ Welcome to SynapseOS School Academy! Start with Lesson 1.1 in the '★ Tutorials' tab on the right, "
            "or switch to '✎ Hands-On Code' to modify and run real Python AI experiments!"
        )

    def _update_badge_header(self) -> None:
        total = len(SCHOOL_CURRICULUM)
        earned = len(self.earned_badges)
        self.badge_lbl.set_markup(
            f"<b><span foreground='#facc15'>★ Badges: {earned} / {total}</span></b>"
        )

    def _populate_sliders(self) -> None:
        self._updating_sliders = True
        for child in self.sliders_vbox.get_children():
            self.sliders_vbox.remove(child)
        self.slider_widgets.clear()

        lab = self.active_lab
        for spec in lab.VARIABLE_SPECS:
            key = spec["key"]
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
            lbl = Gtk.Label()
            lbl.set_xalign(0.0)
            lbl.set_markup(f"<b>{GLib.markup_escape_text(spec['label'])}</b>")
            lbl.set_tooltip_text(spec["desc"])
            box.pack_start(lbl, False, False, 0)

            desc_lbl = Gtk.Label()
            desc_lbl.set_xalign(0.0)
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
            f"▸ Loaded preset for '{lesson['title']}'! Now follow the steps in the Tutorials tab or click '⚡ Turbo +25 Gens'."
        )

    def _on_check_lesson_goal(self, _btn: Gtk.Button) -> None:
        lesson = get_lesson_by_id(self.active_lesson_id)
        telem = self.labs[lesson["lab_id"]].get_telemetry()
        passed, msg = verify_lesson_goal(lesson, telem)
        if passed:
            self.earned_badges.add(lesson["id"])
            self._update_badge_header()
            self._refresh_lesson_view()
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

    def _on_lab_changed(self, combo: Gtk.ComboBoxText) -> None:
        lid = combo.get_active_id()
        if lid and lid in self.labs:
            self.active_lab_id = lid
            self._populate_sliders()
            self._set_cortex_message(f"Switched to {combo.get_active_text()}. Drag sliders on the left or click '⚡ Turbo +25 Gens'!")

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

    def _on_toggle_run(self, _btn: Gtk.Button) -> None:
        self.running = not self.running
        self.btn_run.set_label("|| Pause Sim" if self.running else "▶ Resume Sim")

    def _on_step_once(self, _btn: Gtk.Button) -> None:
        self.running = False
        self.btn_run.set_label("▶ Resume Sim")
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
                bonus_msg = f"\n{goal_msg}"

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
        info = self.cortex.explain_ai_concept(q, force_llm=False)
        telem = self.active_lab.get_telemetry()
        text = (
            f"⚙ [{info.get('title', q)}] ({info.get('source', 'FTS5 KB')})\n"
            f"• Kid & Layman Guide: {info.get('layman_guide', info.get('summary', ''))}\n"
            f"• Live Lab Telemetry: Gen/Ep={telem['generation']}, Best={telem['best_fitness']}, All-Time={telem['best_ever']}"
        )
        self._set_cortex_message(text)

    def _on_ask_cortex_llm(self, _widget: Any) -> None:
        q = self.cortex_entry.get_text().strip() or f"Explain how {self.active_lab_id} works for a student!"
        telem = self.active_lab.get_telemetry()
        enriched_q = f"{q} (Current Lab: {telem['lab']}, Gen: {telem['generation']}, Best: {telem['best_fitness']}, Variables: {telem['params']})"
        self._set_cortex_message("Consulting local `cortex-phi3:latest` Classroom Tutor...")

        def worker():
            info = self.cortex.explain_ai_concept(enriched_q, force_llm=True)
            ans = f"★ {info.get('title')} [{info.get('source')}]\n{info.get('summary', '')}"
            GLib.idle_add(self._set_cortex_message, ans)

        threading.Thread(target=worker, daemon=True).start()

    def _on_ask_linux_cmd(self, _widget: Any) -> None:
        q = self.cortex_entry.get_text().strip() or "boost ram on a potato with zram"
        res = self.cortex.synthesize_command_and_instructions(q, force_llm=False)
        steps = " | ".join(f"{i}. {s}" for i, s in enumerate(res.get("instructions", []), 1))
        text = (
            f"⌘ Linux Command [{res.get('safety', 'safe').upper()}] ({res.get('source', 'FTS5')}): {res.get('summary')}\n"
            f"▸ Command:  {res.get('command')}\n"
            f"▸ Steps:    {steps}"
        )
        self._set_cortex_message(text)

    def _on_tick(self) -> bool:
        if self.running:
            self.active_lab.step_physics()

        telem = self.active_lab.get_telemetry()
        extra = ""
        if "landed_last_gen" in telem:
            extra = f" | Landed: <b><span foreground='#4ade80'>{telem['landed_last_gen']}</span></b>"
        self.telemetry_lbl.set_markup(
            f"<b>{telem['lab']}</b>   |   Gen/Epoch: <b><span foreground='#38bdf8'>{telem['generation']}</span></b>   "
            f"|   Best: <b><span foreground='#4ade80'>{telem['best_fitness']}</span></b>   "
            f"|   Avg: <span foreground='#facc15'>{telem['avg_fitness']}</span>   "
            f"|   Record: <b><span foreground='#f472b6'>{telem['best_ever']}</span></b>{extra}"
        )

        self.sim_canvas.queue_draw()
        if self.right_notebook.get_current_page() == 2:
            self.net_canvas.queue_draw()
        return True

    # ==========================================================================
    # CAIRO 60 FPS SIMULATION VIEWPORT RENDERERS
    # ==========================================================================
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
        for r in lab.rockets:
            if not r.alive and not r.landed:
                continue
            is_lead = (r is leader)
            cr.save()
            cr.translate(r.x, r.y)
            cr.rotate(r.angle)

            if r.main_thruster and r.alive:
                cr.set_source_rgba(1.0, 0.55, 0.1, 0.9 if is_lead else 0.35)
                cr.move_to(-4, 8)
                cr.line_to(0, 19)
                cr.line_to(4, 8)
                cr.close_path()
                cr.fill()

            if r.landed:
                cr.set_source_rgba(0.2, 0.95, 0.5, 0.95)
            elif is_lead:
                cr.set_source_rgba(0.22, 0.75, 0.98, 1.0)
            else:
                cr.set_source_rgba(0.6, 0.65, 0.75, 0.30)

            cr.move_to(0, -11)
            cr.line_to(-7, 8)
            cr.line_to(7, 8)
            cr.close_path()
            cr.fill()
            cr.restore()

        cr.restore()

    def _render_raycast_car(self, cr: cairo.Context, w: float, h: float) -> None:
        lab: NEATRaycastCarLab = self.labs["raycast_car"]
        sx, sy = w / lab.width, h / lab.height
        cr.save()
        cr.scale(sx, sy)

        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_line_join(cairo.LINE_JOIN_ROUND)

        cr.set_source_rgb(0.32, 0.38, 0.50)
        cr.set_line_width(lab.params["track_width"] * 2.0 + 6.0)
        for i, (wx, wy) in enumerate(lab.waypoints):
            if i == 0:
                cr.move_to(wx, wy)
            else:
                cr.line_to(wx, wy)
        cr.close_path()
        cr.stroke()

        cr.set_source_rgb(0.11, 0.13, 0.18)
        cr.set_line_width(lab.params["track_width"] * 2.0)
        for i, (wx, wy) in enumerate(lab.waypoints):
            if i == 0:
                cr.move_to(wx, wy)
            else:
                cr.line_to(wx, wy)
        cr.close_path()
        cr.stroke()

        cr.set_source_rgba(0.95, 0.80, 0.20, 0.35)
        cr.set_line_width(1.5)
        cr.set_dash([8.0, 8.0])
        for i, (wx, wy) in enumerate(lab.waypoints):
            if i == 0:
                cr.move_to(wx, wy)
            else:
                cr.line_to(wx, wy)
        cr.close_path()
        cr.stroke()
        cr.set_dash([])

        leader = lab.get_leader()
        if leader.alive:
            cr.set_line_width(1.4)
            for rx, ry, nd in leader.rays:
                cr.set_source_rgba(1.0 - nd, nd, 0.2, 0.85)
                cr.move_to(leader.x, leader.y)
                cr.line_to(rx, ry)
                cr.stroke()

        for car in lab.cars:
            if not car.alive and car is not leader:
                continue
            is_lead = (car is leader)
            cr.save()
            cr.translate(car.x, car.y)
            cr.rotate(car.heading)
            if is_lead:
                cr.set_source_rgba(0.2, 0.9, 0.55, 1.0)
            else:
                cr.set_source_rgba(0.35, 0.65, 0.95, 0.45)
            cr.rectangle(-8, -4.5, 16, 9)
            cr.fill()
            cr.restore()

        cr.restore()

    def _render_rl_gridworld(self, cr: cairo.Context, w: float, h: float) -> None:
        lab: RLGridWorldLab = self.labs["rl_gridworld"]
        pad = 24.0
        cw = (w - 2 * pad) / lab.cols
        ch = (h - 2 * pad) / lab.rows

        for c in range(lab.cols):
            for r in range(lab.rows):
                x = pad + c * cw
                y = pad + r * ch
                pos = (c, r)
                max_q = max(lab.q_table[pos])

                if pos == lab.goal_pos:
                    cr.set_source_rgb(0.12, 0.65, 0.35)
                elif pos in lab.lava_cells:
                    cr.set_source_rgb(0.65, 0.14, 0.18)
                elif pos in lab.wall_cells:
                    cr.set_source_rgb(0.22, 0.25, 0.32)
                else:
                    norm = max(-1.0, min(1.0, max_q / 100.0))
                    if norm >= 0:
                        cr.set_source_rgb(0.10, 0.14 + 0.45 * norm, 0.22 + 0.25 * norm)
                    else:
                        cr.set_source_rgb(0.14 - 0.35 * norm, 0.12, 0.16)

                cr.rectangle(x + 1, y + 1, cw - 2, ch - 2)
                cr.fill()

                if pos not in lab.lava_cells and pos not in lab.wall_cells and pos != lab.goal_pos:
                    q_vals = lab.q_table[pos]
                    best_a = max(range(4), key=q_vals.__getitem__)
                    cr.set_source_rgba(0.85, 0.92, 1.0, 0.85)
                    cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                    cr.set_font_size(14)
                    cr.move_to(x + cw * 0.38, y + ch * 0.48)
                    cr.show_text(lab.ARROWS[best_a])

                    cr.set_font_size(9.5)
                    cr.set_source_rgba(0.65, 0.75, 0.88, 0.85)
                    cr.move_to(x + 5, y + ch - 6)
                    cr.show_text(f"{max_q:+.1f}")
                elif pos == lab.goal_pos:
                    cr.set_source_rgb(1.0, 0.95, 0.5)
                    cr.set_font_size(12)
                    cr.move_to(x + 8, y + ch * 0.55)
                    cr.show_text("★ GOAL")
                elif pos in lab.lava_cells:
                    cr.set_source_rgb(1.0, 0.65, 0.65)
                    cr.set_font_size(10)
                    cr.move_to(x + 10, y + ch * 0.55)
                    cr.show_text("LAVA")

        ax = pad + (lab.agent_pos[0] + 0.5) * cw
        ay = pad + (lab.agent_pos[1] + 0.5) * ch
        cr.set_source_rgb(0.22, 0.82, 0.98)
        cr.arc(ax, ay, min(cw, ch) * 0.28, 0, 2 * math.pi)
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
        grid_n = 28
        cw = w / grid_n
        ch = h / grid_n

        for gx in range(grid_n):
            x_val = ((gx + 0.5) / grid_n) * 2.0 - 1.0
            for gy in range(grid_n):
                y_val = 1.0 - ((gy + 0.5) / grid_n) * 2.0
                prob, _ = lab.predict_prob(x_val, y_val)
                r_col = 0.65 * (1.0 - prob) + 0.08 * prob
                g_col = 0.22 * (1.0 - prob) + 0.52 * prob
                b_col = 0.25 * (1.0 - prob) + 0.75 * prob
                cr.set_source_rgb(r_col, g_col, b_col)
                cr.rectangle(gx * cw, gy * ch, cw + 1, ch + 1)
                cr.fill()

        for x, y, label in lab.samples:
            sx = (x + 1.0) * 0.5 * w
            sy = (1.0 - (y + 1.0) * 0.5) * h
            cr.set_source_rgb(0.98, 0.98, 0.98)
            cr.arc(sx, sy, 5.2, 0, 2 * math.pi)
            cr.fill()
            if label > 0.5:
                cr.set_source_rgb(0.10, 0.85, 0.98)
            else:
                cr.set_source_rgb(0.98, 0.40, 0.30)
            cr.arc(sx, sy, 3.8, 0, 2 * math.pi)
            cr.fill()

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
        lab: PrimeAttentionLab = self.labs["prime_attention"]
        pad = 22.0
        chart_w = w * 0.58 - pad
        chart_h = h * 0.62 - pad

        # 1. Retention Curve Chart (Top-Left)
        cr.set_source_rgb(0.09, 0.11, 0.16)
        cr.rectangle(pad, pad, chart_w, chart_h)
        cr.fill()

        cr.set_source_rgb(0.85, 0.92, 0.98)
        cr.set_font_size(12)
        cr.move_to(pad + 8, pad + 18)
        cr.show_text("Passkey Cosine Retention vs Distractor Gap (N)")

        # Legend
        cr.set_font_size(10)
        cr.set_source_rgb(0.20, 0.92, 0.50)
        cr.move_to(pad + 8, pad + 34)
        cr.show_text("[*] Hybrid Window + PRIME Moment")
        cr.set_source_rgb(0.22, 0.74, 0.98)
        cr.move_to(pad + 205, pad + 34)
        cr.show_text("[*] Window Only")
        cr.set_source_rgb(0.98, 0.80, 0.20)
        cr.move_to(pad + 298, pad + 34)
        cr.show_text("[*] Linear ELU+1")

        gx0, gy0 = pad + 32.0, pad + 48.0
        gw, gh = chart_w - 44.0, chart_h - 68.0

        # Grid lines
        cr.set_source_rgba(0.3, 0.35, 0.45, 0.4)
        cr.set_line_width(1.0)
        for frac in (0.0, 0.5, 1.0):
            yy = gy0 + gh * (1.0 - frac)
            cr.move_to(gx0, yy)
            cr.line_to(gx0 + gw, yy)
            cr.stroke()
            cr.move_to(pad + 4, yy + 4)
            cr.show_text(f"{int(frac*100)}%")

        gaps = lab.GAPS
        for idx, gval in enumerate(gaps):
            xx = gx0 + (idx / max(1, len(gaps) - 1)) * gw
            cr.set_source_rgb(0.65, 0.72, 0.82)
            cr.move_to(xx - 10, gy0 + gh + 14)
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
                cr.arc(px, py, 3.2, 0, 2 * math.pi)
                cr.fill()

        draw_curve(lab.curve_linear_elu, 0.98, 0.80, 0.20, 1.8)
        draw_curve(lab.curve_window_only, 0.22, 0.74, 0.98, 1.8)
        draw_curve(lab.curve_hybrid, 0.20, 0.92, 0.50, 2.8)

        # 2. Live 2nd-Order S2 Moment Matrix Heatmap (Top-Right)
        hx0 = pad + chart_w + 14.0
        hw = w - hx0 - pad
        cr.set_source_rgb(0.09, 0.11, 0.16)
        cr.rectangle(hx0, pad, hw, chart_h)
        cr.fill()

        cr.set_source_rgb(0.85, 0.92, 0.98)
        cr.set_font_size(11)
        cr.move_to(hx0 + 8, pad + 18)
        cr.show_text("2nd-Order Moment State S2 (O(D^2))")

        mat = lab.s2_heatmap
        rows = len(mat)
        cols = len(mat[0]) if rows > 0 else 1
        cell_w = (hw - 20.0) / max(1, cols)
        cell_h = (chart_h - 36.0) / max(1, rows)
        vmax = max((abs(v) for row in mat for v in row), default=0.0) + 1e-5
        for r_i in range(rows):
            for c_i in range(cols):
                val = float(mat[r_i][c_i]) / vmax
                if val >= 0:
                    cr.set_source_rgb(0.10, 0.35 + 0.60 * val, 0.55 + 0.40 * val)
                else:
                    cr.set_source_rgb(0.45 + 0.50 * abs(val), 0.12, 0.25)
                cr.rectangle(
                    hx0 + 10.0 + c_i * cell_w,
                    pad + 26.0 + r_i * cell_h,
                    max(1.0, cell_w - 1.0),
                    max(1.0, cell_h - 1.0),
                )
                cr.fill()

        # 3. Bottom Bar: Constant L2 Cache Memory vs Softmax KV Cache & C99 Speed
        by0 = pad + chart_h + 12.0
        bh = h - by0 - pad
        cr.set_source_rgb(0.09, 0.11, 0.16)
        cr.rectangle(pad, by0, w - 2 * pad, bh)
        cr.fill()

        telem = lab.get_telemetry()
        state_kb = telem["state_kb"]
        c_tps = telem["c_tokens_per_sec"]
        w_tok = int(lab.params["window_size"])
        qk_on = int(round(lab.params["use_qk_norm"])) >= 1

        cr.set_source_rgb(0.22, 0.82, 0.98)
        cr.set_font_size(12)
        cr.move_to(pad + 12, by0 + 22)
        cr.show_text(
            f"[C99 Native Kernel]: {c_tps:,.0f} tok/s  |  "
            f"O(1) PRIME State: {state_kb} KB (Fits in CPU L2 Cache!)  |  "
            f"Sliding Window W={w_tok} tok"
        )

        # Memory Comparison Bars (16K Context Softmax = 288 MB vs PRIME = 0.26 MB)
        cr.set_font_size(11)
        cr.set_source_rgb(0.95, 0.35, 0.35)
        cr.move_to(pad + 12, by0 + 46)
        cr.show_text("Softmax 16K KV-Cache: 288,000 KB (DRAM Bound)")
        cr.rectangle(pad + 310, by0 + 35, max(20.0, (w - 360 - pad) * 0.92), 12)
        cr.fill()

        cr.set_source_rgb(0.20, 0.92, 0.50)
        cr.move_to(pad + 12, by0 + 68)
        cr.show_text(f"PRIME + Window (O(1)):     {state_kb:>6.1f} KB (99.9% RAM Saved)")
        cr.rectangle(pad + 310, by0 + 57, 14.0, 12)
        cr.fill()

        cr.set_source_rgb(0.98, 0.82, 0.25) if qk_on else cr.set_source_rgb(0.98, 0.30, 0.30)
        cr.move_to(pad + 12, by0 + 90)
        status_qk = (
            "[OK] Per-Head QK-Norm ACTIVE: Taylor inputs |x| <= 1.0 bounded (No Parabolic Rebound)"
            if qk_on
            else "[!] QK-Norm OFF: Parabolic Rebound P(x)=1+x+0.5x^2 explodes on negative logits!"
        )
        cr.show_text(status_qk)

    # ==========================================================================
    # CAIRO NEURAL TOPOLOGY & FITNESS HISTORY RENDERER
    # ==========================================================================
    def _draw_net_canvas(self, widget: Gtk.DrawingArea, cr: cairo.Context) -> bool:
        alloc = widget.get_allocation()
        w, h = float(alloc.width), float(alloc.height)

        cr.set_source_rgb(0.06, 0.08, 0.11)
        cr.paint()

        top_h = h * 0.56
        lab = self.active_lab

        if hasattr(lab, "neat"):
            leader = lab.get_leader()
            genome = leader.genome
            self._render_neat_genome(cr, genome, 12.0, 18.0, w - 24.0, top_h - 24.0)
        else:
            cr.set_source_rgb(0.65, 0.75, 0.90)
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(12)
            cr.move_to(16, 28)
            cr.show_text("Live Policy / Parameter State")
            y_cursor = 52
            cr.set_font_size(11)
            for k, v in lab.params.items():
                cr.move_to(20, y_cursor)
                cr.show_text(f"• {k}: {v:.3f}")
                y_cursor += 18

        self._render_fitness_chart(cr, lab, 16.0, top_h + 12.0, w - 32.0, h - top_h - 24.0)
        return False

    def _render_neat_genome(self, cr: cairo.Context, genome: Any, x0: float, y0: float, gw: float, gh: float) -> None:
        cr.set_source_rgb(0.65, 0.78, 0.95)
        cr.set_font_size(11)
        cr.move_to(x0, y0 - 4)
        cr.show_text(f"Live Neural Topology (Nodes: {len(genome.nodes)} | Synapses: {len(genome.connections)})")

        layers: Dict[float, List[Any]] = {}
        for n in genome.nodes.values():
            ly = round(n.layer, 3)
            layers.setdefault(ly, []).append(n)

        node_pos: Dict[int, Tuple[float, float]] = {}
        for ly, nlist in layers.items():
            nx = x0 + 18.0 + ly * (gw - 36.0)
            count = len(nlist)
            for i, node in enumerate(nlist):
                ny = y0 + 14.0 + ((i + 0.5) / max(1, count)) * (gh - 24.0)
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
            cr.set_line_width(max(0.8, min(3.5, abs(conn.weight) * 1.2)))
            cr.move_to(p1[0], p1[1])
            cr.line_to(p2[0], p2[1])
            cr.stroke()

        for nid, (nx, ny) in node_pos.items():
            node = genome.nodes[nid]
            act = max(-1.0, min(1.0, node.last_activation))
            if act >= 0:
                cr.set_source_rgb(0.18 + 0.75 * act, 0.55 + 0.40 * act, 0.95)
            else:
                cr.set_source_rgb(0.95, 0.35 * (1.0 + act), 0.35)
            cr.arc(nx, ny, 6.0, 0, 2 * math.pi)
            cr.fill()

    def _render_fitness_chart(self, cr: cairo.Context, lab: Any, x0: float, y0: float, cw: float, ch: float) -> None:
        cr.set_source_rgb(0.10, 0.12, 0.17)
        cr.rectangle(x0, y0, cw, ch)
        cr.fill()

        best_hist = getattr(lab, "history_best", None) or (lab.neat.history_best if hasattr(lab, "neat") else [])
        avg_hist = getattr(lab, "history_avg", None) or (lab.neat.history_avg if hasattr(lab, "neat") else [])

        cr.set_source_rgb(0.65, 0.75, 0.88)
        cr.set_font_size(11)
        cr.move_to(x0 + 6, y0 + 14)
        cr.show_text("Convergence Curve (Green = Best, Yellow = Avg)")

        if len(best_hist) < 2:
            cr.set_source_rgba(0.5, 0.6, 0.7, 0.7)
            cr.move_to(x0 + 12, y0 + ch * 0.55)
            cr.show_text("Click '⚡ Turbo +25 Gens' or let simulation run to plot curve...")
            return

        pts_best = best_hist[-40:]
        pts_avg = avg_hist[-40:]
        all_vals = pts_best + pts_avg
        vmin, vmax = min(all_vals), max(all_vals)
        span = max(1e-3, vmax - vmin)

        cr.set_source_rgba(0.95, 0.80, 0.20, 0.85)
        cr.set_line_width(1.6)
        for i, val in enumerate(pts_avg):
            px = x0 + 8.0 + (i / max(1, len(pts_avg) - 1)) * (cw - 16.0)
            py = y0 + ch - 10.0 - ((val - vmin) / span) * (ch - 30.0)
            if i == 0:
                cr.move_to(px, py)
            else:
                cr.line_to(px, py)
        cr.stroke()

        cr.set_source_rgba(0.20, 0.92, 0.50, 0.95)
        cr.set_line_width(2.2)
        for i, val in enumerate(pts_best):
            px = x0 + 8.0 + (i / max(1, len(pts_best) - 1)) * (cw - 16.0)
            py = y0 + ch - 10.0 - ((val - vmin) / span) * (ch - 30.0)
            if i == 0:
                cr.move_to(px, py)
            else:
                cr.line_to(px, py)
        cr.stroke()


def main():
    win = SynapseStudioWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
