"""
SynapseOS Safe Media & Content Sandbox ("Synapse Kids TV" + Offline Kiwix Encyclopedia).
Provides a 100% offline, distraction-free, verified educational media player and encyclopedia
so students have YouTube-Kids-style animated STEM lessons and Kiwix/Wikipedia-style articles
without unrestricted web browsing.
"""

import math
import time
from typing import Any, Callable, Dict, List, Optional

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk, Gdk, GLib, Pango
    GTK_AVAILABLE = True
except Exception:
    GTK_AVAILABLE = False


CURATED_VIDEO_EPISODES: List[Dict[str, Any]] = [
    {
        "id": "ep_rocket_physics",
        "title": "🚀 Ep 1: How Rockets Land Gently on the Moon",
        "duration_sec": 30,
        "category": "Space & Physics (Grades 3-8)",
        "narration": (
            "On the Moon, there is no air for parachutes! Instead, a Lunar Lander fires its bottom rocket thruster "
            "to push upward against gravity. If it fires too late, it crashes; if it fires too early, it wastes fuel "
            "and floats back up. An AI autopilot watches height and downward speed to land softer than a feather!"
        ),
        "subtitles": [
            (0.0, 7.5, "🌕 Welcome to the Moon! Gravity here is 1/6th as strong as on Earth, with zero air for parachutes."),
            (7.5, 15.0, "🔥 To slow down, the lander fires its main engine downward—creating upward thrust force."),
            (15.0, 22.5, "🧠 The AI brain checks two sensors: Distance to the Pad (Y) and Downward Velocity (Vy)."),
            (22.5, 30.0, "🏆 Touchdown! Keeping speed under 2.0 m/s inside the yellow flags scores +200 reward points!"),
        ],
        "quiz_q": "Why can't a Lunar Lander use a parachute on the Moon?",
        "quiz_options": [
            ("Because the Moon has no atmosphere (air) to catch a parachute!", True),
            ("Because parachutes are too heavy for rockets.", False),
            ("Because the Moon spins too fast.", False),
        ],
    },
    {
        "id": "ep_neural_brain",
        "title": "🧠 Ep 2: How a Tiny Neural Network Learns",
        "duration_sec": 30,
        "category": "AI & Brains (Grades 4-10)",
        "narration": (
            "A neural network is inspired by the neurons in your brain! Input neurons read numbers from sensors, "
            "hidden neurons mix those signals using connection weights, and output neurons decide what action to take. "
            "During NEAT evolution, the best brains survive and pass their connections to the next generation!"
        ),
        "subtitles": [
            (0.0, 7.5, "🔌 Step 1 (Inputs): Sensors measure the world—like distance to walls or rocket tilt angle."),
            (7.5, 15.0, "⚡ Step 2 (Synapse Weights): Green connections boost a signal (+1); red connections block it (-1)."),
            (15.0, 22.5, "🎯 Step 3 (Outputs): The output neurons trigger actions like 'Steer Left' or 'Fire Thruster'."),
            (22.5, 30.0, "🧬 Step 4 (Evolution): Generation after generation, mutations discover smarter wiring!"),
        ],
        "quiz_q": "What do the connection weights in a neural network do?",
        "quiz_options": [
            ("They control how strongly one neuron's signal influences the next neuron.", True),
            ("They make the computer monitor brighter.", False),
            ("They delete the operating system.", False),
        ],
    },
    {
        "id": "ep_lidar_cars",
        "title": "🏎️ Ep 3: How Self-Driving Cars See with Raycast LIDAR",
        "duration_sec": 30,
        "category": "Robotics & Sensors (Grades 5-12)",
        "narration": (
            "How does an autonomous car drive around corners without bumping into walls? It shoots out invisible laser "
            "beams called raycasts in 5 directions! When the left beam gets short, the car knows a wall is close on "
            "the left and steers smoothly toward the longest open beam."
        ),
        "subtitles": [
            (0.0, 7.5, "📡 Raycast sensors act like 5 laser tape measures pointing ahead of the car."),
            (7.5, 15.0, "🟢 Long green beam = wide open road ahead! Keep throttle high."),
            (15.0, 22.5, "🔴 Short red beam on the left = wall approaching! Turn the steering wheel right."),
            (22.5, 30.0, "🏁 By combining all 5 beams, a tiny 20-neuron brain can race laps without crashing!"),
        ],
        "quiz_q": "If the left raycast beam becomes very short (near 0.1), what should the car do?",
        "quiz_options": [
            ("Steer to the right toward the longer open beams!", True),
            ("Close its eyes and accelerate.", False),
            ("Turn sharper into the left wall.", False),
        ],
    },
    {
        "id": "ep_potato_ternary",
        "title": "🥔 Ep 4: Superfast AI on Older Laptops (1.58-Bit Ternary & PRIME)",
        "duration_sec": 30,
        "category": "Computer Engineering (Grades 6-12)",
        "narration": (
            "You don't need an expensive supercomputer to build AI! By simplifying neural weights to just three values—"
            "minus one, zero, and plus one—SynapseOS packs 64 weights into a single CPU register and counts bits at "
            "lightning speed on a 2009 laptop!"
        ),
        "subtitles": [
            (0.0, 7.5, "💻 Standard AI uses 32-bit decimal numbers that bog down older laptop CPUs."),
            (7.5, 15.0, "🔢 1.58-Bit Ternary simplifies weights to {-1, 0, +1}—just like Reverse, Neutral, and Forward!"),
            (15.0, 22.5, "⚡ Using CPU POPCNT instructions, 64 weights are calculated in a single clock cycle (13x faster!)."),
            (22.5, 30.0, "🧠 And PRIME Moment Attention keeps memory tiny (262 KB) so your laptop never freezes!"),
        ],
        "quiz_q": "What are the three possible weight values in a 1.58-Bit Ternary neural network?",
        "quiz_options": [
            ("-1, 0, and +1", True),
            ("3.14159, 99.9, and 1024.0", False),
            ("Only letters A, B, and C", False),
        ],
    },
]


OFFLINE_KIWIX_ARTICLES: List[Dict[str, str]] = [
    {
        "slug": "moon_gravity",
        "title": "🌕 The Moon & Orbital Physics",
        "category": "Space & Physics",
        "summary": "Why the Moon has 1.62 m/s² gravity, how Apollo landed in 1969, and how thrusters maneuver in a vacuum.",
        "body": (
            "### 🌕 The Moon & Rocket Landings\n\n"
            "- **Surface Gravity**: `1.62 m/s²` (about **16.5%** of Earth's `9.81 m/s²`).\n"
            "- **Distance from Earth**: Average of `384,400 km` (`238,855 miles`).\n"
            "- **Atmosphere**: Effectively a vacuum (exosphere), meaning **parachutes and wings do not work**.\n\n"
            "#### How Newton's Third Law Lands a Spacecraft\n"
            "Every action has an equal and opposite reaction ($F = m \\cdot a$). When a rocket expels hot gas downward "
            "at high speed, the exhaust pushes the spacecraft upward. To touch down safely, the pilot (or AI controller) "
            "must reduce vertical velocity ($v_y$) to near `0 m/s` right as altitude ($y$) reaches `0`.\n\n"
            "#### Try It in SynapseOS\n"
            "Open **Mission 1: Moon Lander** in Kid Arcade or Student Mode and switch between **Moon (-1.62)** and **Mars (-3.72)**!"
        ),
    },
    {
        "slug": "neuroevolution_neat",
        "title": "🧬 Neuroevolution & NEAT Explained",
        "category": "AI & Robotics",
        "summary": "How Darwinian natural selection evolves neural network brains from scratch without calculus.",
        "body": (
            "### 🧬 What is NEAT (Neuroevolution of Augmenting Topologies)?\n\n"
            "Created by Kenneth Stanley and Risto Miikkulainen in 2002, **NEAT** evolves both the **synapse weights** "
            "and the **wiring structure** (adding new neurons and connections) of artificial brains.\n\n"
            "1. **Population**: Start with 50 to 150 simple neural networks.\n"
            "2. **Fitness Score**: Test every network in the physics simulator (e.g., how close did the rocket land to the flag?).\n"
            "3. **Selection & Speciation**: Group similar network shapes into *species* so new inventions are protected while they improve.\n"
            "4. **Mutation & Crossover**: Combine the highest-scoring networks and slightly tweak their weights for the next generation!"
        ),
    },
    {
        "slug": "reinforcement_learning",
        "title": "🎯 Reinforcement Learning (Rewards, Q-Learning & PPO)",
        "category": "AI & Robotics",
        "summary": "How agents learn optimal decisions through trial, error, rewards, and discount factors (γ).",
        "body": (
            "### 🎯 Reinforcement Learning (RL)\n\n"
            "In Reinforcement Learning, an **Agent** interacts with an **Environment**:\n"
            "- **State ($s_t$)**: What the agent observes right now (position, speed, pole angle).\n"
            "- **Action ($a_t$)**: What the agent chooses to do (push left, push right, fire thruster).\n"
            "- **Reward ($r_t$)**: Points given for good behavior (`+1` for keeping the pole balanced, `-100` for crashing).\n\n"
            "#### The Bellman Equation\n"
            "$$Q(s, a) \\leftarrow Q(s, a) + \\alpha \\left[ r + \\gamma \\max_{a'} Q(s', a') - Q(s, a) \\right]$$\n"
            "- **Learning Rate ($\\alpha$)**: How fast the agent overwrites old memories with new lessons.\n"
            "- **Discount Factor ($\\gamma$)**: How much the agent cares about future rewards versus immediate snacks!"
        ),
    },
    {
        "slug": "photosynthesis_ecosystems",
        "title": "🌿 Ecosystems, Predators & Foraging Swarms",
        "category": "Earth & Biology",
        "summary": "How biological food webs balance energy, and how Boids/Swarm AI models animal flocking.",
        "body": (
            "### 🌿 Food Webs & Swarm Intelligence\n\n"
            "In nature, energy flows from sunlight into plants (**producers**), then to herbivores (**foragers**), "
            "and finally to predators.\n\n"
            "#### Three Rules of Flocking (Craig Reynolds' Boids)\n"
            "Complex bird flocks and fish schools emerge from just three simple local rules:\n"
            "1. **Separation**: Steer to avoid crowding local flockmates.\n"
            "2. **Alignment**: Steer toward the average heading of local flockmates.\n"
            "3. **Cohesion**: Steer to move toward the average position of local flockmates.\n\n"
            "#### Try It in SynapseOS\n"
            "Switch to **Swarm Foraging** in the AI Lab Selector to watch 30 neural creatures evolve food-seeking behavior!"
        ),
    },
    {
        "slug": "linux_open_source",
        "title": "🐧 What is Linux & Open Source Software?",
        "category": "Computer Science & Linux",
        "summary": "How the Linux kernel powers supercomputers, spacecraft, Android phones, and revived classroom laptops.",
        "body": (
            "### 🐧 Linux & The Power of Open Source\n\n"
            "**Linux** is an open-source operating system kernel started by Linus Torvalds in 1991. Because its source code "
            "is free to study, improve, and share, Linux runs on:\n"
            "- **100%** of the world's top 500 supercomputers\n"
            "- NASA's **Ingenuity Mars Helicopter** and International Space Station laptops\n"
            "- **SynapseOS** on revived 2007–2017 school laptops and Chromebooks!\n\n"
            "#### Essential Safe Linux Commands\n"
            "- `ls -la`: List all files and folders in your current directory.\n"
            "- `free -h`: Check how much RAM memory is free right now.\n"
            "- `uname -a`: Inspect the Linux kernel version and CPU architecture."
        ),
    },
    {
        "slug": "binary_and_ternary",
        "title": "🔢 Binary (0, 1) vs. Balanced Ternary (-1, 0, +1)",
        "category": "Mathematics & Computing",
        "summary": "How computers represent information with bits and why 1.58-bit ternary math accelerates neural networks.",
        "body": (
            "### 🔢 Bits, Trits, and Fast CPU Math\n\n"
            "- **Binary (`Base 2`)**: Uses two digits (`0` and `1`). Each digit is called a **bit**.\n"
            "- **Balanced Ternary (`Base 3`)**: Uses three values (`-1`, `0`, `+1`). Each value is called a **trit** "
            "(carrying $\\log_2(3) \\approx 1.585$ bits of information).\n\n"
            "#### Why Ternary Helps AI on Classroom Laptops\n"
            "Multiplying millions of 32-bit floating-point numbers takes heavy electricity and GPU hardware. "
            "When neural network weights are ternary (`-1, 0, +1`), multiplication turns into simple sign flips and "
            "bit counting (`POPCNT`), running **13x faster** on standard laptop CPUs!"
        ),
    },
]


class SafeMediaSandboxWidget:
    """
    Embeddable or dialog-ready GTK3 Safe Media & Content Sandbox widget.
    Includes:
      - Tab 1: '📺 Synapse Kids TV (Animated STEM Video Lessons)'
      - Tab 2: '📚 Offline Kiwix Encyclopedia (Verified Articles)'
      - Tab 3: '📎 Teacher Shared Files & Course Worksheets'
    """

    def __init__(
        self,
        classroom_hub: Optional[Any] = None,
        speak_callback: Optional[Callable[[str], None]] = None,
    ):
        self.classroom_hub = classroom_hub
        self.speak_callback = speak_callback
        self.current_episode_idx = 0
        self.is_playing = True
        self.play_elapsed_sec = 0.0
        self._last_tick = time.perf_counter()

        if GTK_AVAILABLE:
            self.widget = self._build_ui()
            GLib.timeout_add(40, self._on_anim_tick)
        else:
            self.widget = None

    @staticmethod
    def get_episodes() -> List[Dict[str, Any]]:
        return list(CURATED_VIDEO_EPISODES)

    @staticmethod
    def search_encyclopedia(query: str = "") -> List[Dict[str, str]]:
        q = query.strip().lower()
        if not q:
            return list(OFFLINE_KIWIX_ARTICLES)
        matches = []
        for art in OFFLINE_KIWIX_ARTICLES:
            hay = f"{art['title']} {art['category']} {art['summary']} {art['body']}".lower()
            if all(tok in hay for tok in q.split()):
                matches.append(art)
        return matches or list(OFFLINE_KIWIX_ARTICLES)

    def _build_ui(self) -> Gtk.Widget:
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        root.set_margin_top(8)
        root.set_margin_bottom(8)
        root.set_margin_start(8)
        root.set_margin_end(8)

        # Header banner
        banner = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        banner_lbl = Gtk.Label()
        banner_lbl.set_markup(
            "<span size='large' weight='bold' foreground='#38bdf8'>"
            "🛡️ Synapse Safe Media &amp; Offline Kiwix Sandbox"
            "</span>  "
            "<span size='small' foreground='#a7f3d0'>"
            "100% Offline • Verified STEM Videos &amp; Encyclopedia • Zero Open Web Browsing"
            "</span>"
        )
        banner_lbl.set_xalign(0)
        banner.pack_start(banner_lbl, True, True, 4)
        root.pack_start(banner, False, False, 0)

        notebook = Gtk.Notebook()
        root.pack_start(notebook, True, True, 0)

        # --- TAB 1: Synapse Kids TV (Animated STEM Video Player) ---
        tv_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        tv_box.set_margin_top(8)
        tv_box.set_margin_bottom(8)
        tv_box.set_margin_start(8)
        tv_box.set_margin_end(8)

        # Left column: Episode list + Mini-Quiz
        left_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        left_col.set_size_request(290, -1)

        ep_hdr = Gtk.Label()
        ep_hdr.set_markup("<b>📺 Verified STEM Video Episodes</b>")
        ep_hdr.set_xalign(0)
        left_col.pack_start(ep_hdr, False, False, 0)

        for idx, ep in enumerate(CURATED_VIDEO_EPISODES):
            btn = Gtk.Button(label=ep["title"])
            btn.connect("clicked", lambda _b, i=idx: self._select_episode(i))
            left_col.pack_start(btn, False, False, 0)

        # Mini-Quiz Box
        quiz_frame = Gtk.Frame(label=" 🎯 Episode Quick Check ")
        quiz_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        quiz_vbox.set_margin_top(6)
        quiz_vbox.set_margin_bottom(6)
        quiz_vbox.set_margin_start(6)
        quiz_vbox.set_margin_end(6)

        self.quiz_q_lbl = Gtk.Label()
        self.quiz_q_lbl.set_line_wrap(True)
        self.quiz_q_lbl.set_max_width_chars(34)
        self.quiz_q_lbl.set_xalign(0)
        quiz_vbox.pack_start(self.quiz_q_lbl, False, False, 0)

        self.quiz_btns_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        quiz_vbox.pack_start(self.quiz_btns_box, False, False, 0)

        self.quiz_feedback_lbl = Gtk.Label(label="")
        self.quiz_feedback_lbl.set_line_wrap(True)
        self.quiz_feedback_lbl.set_xalign(0)
        quiz_vbox.pack_start(self.quiz_feedback_lbl, False, False, 0)

        quiz_frame.add(quiz_vbox)
        left_col.pack_start(quiz_frame, True, True, 4)
        tv_box.pack_start(left_col, False, False, 0)

        # Right column: Animated Canvas + Subtitles + Transport Controls
        player_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.tv_title_lbl = Gtk.Label()
        self.tv_title_lbl.set_xalign(0)
        player_col.pack_start(self.tv_title_lbl, False, False, 0)

        self.tv_area = Gtk.DrawingArea()
        self.tv_area.set_size_request(520, 270)
        self.tv_area.connect("draw", self._on_draw_tv)
        player_col.pack_start(self.tv_area, True, True, 0)

        self.subtitle_lbl = Gtk.Label()
        self.subtitle_lbl.set_line_wrap(True)
        self.subtitle_lbl.set_xalign(0.5)
        player_col.pack_start(self.subtitle_lbl, False, False, 2)

        ctrl_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.play_btn = Gtk.Button(label="⏸ Pause")
        self.play_btn.connect("clicked", self._on_toggle_play)
        ctrl_bar.pack_start(self.play_btn, False, False, 0)

        restart_btn = Gtk.Button(label="⏮ Replay Episode")
        restart_btn.connect("clicked", self._on_restart_ep)
        ctrl_bar.pack_start(restart_btn, False, False, 0)

        narrate_btn = Gtk.Button(label="🔊 Read Aloud Lesson")
        narrate_btn.connect("clicked", self._on_narrate_ep)
        ctrl_bar.pack_start(narrate_btn, False, False, 0)

        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        ctrl_bar.pack_start(self.progress_bar, True, True, 4)

        player_col.pack_start(ctrl_bar, False, False, 0)
        tv_box.pack_start(player_col, True, True, 0)

        notebook.append_page(tv_box, Gtk.Label(label="📺 Synapse Kids TV (STEM Video Player)"))

        # --- TAB 2: Offline Kiwix / Kid Encyclopedia ---
        kiwix_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        kiwix_box.set_margin_top(8)
        kiwix_box.set_margin_bottom(8)
        kiwix_box.set_margin_start(8)
        kiwix_box.set_margin_end(8)

        search_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        search_lbl = Gtk.Label()
        search_lbl.set_markup("<b>🔍 Offline Kiwix Search:</b>")
        search_row.pack_start(search_lbl, False, False, 0)

        self.kiwix_entry = Gtk.Entry()
        self.kiwix_entry.set_placeholder_text("Search verified science, space, AI, biology, or Linux articles...")
        self.kiwix_entry.connect("changed", self._on_kiwix_search_changed)
        search_row.pack_start(self.kiwix_entry, True, True, 0)

        read_art_btn = Gtk.Button(label="🔊 Read Article Aloud")
        read_art_btn.connect("clicked", self._on_read_article_aloud)
        search_row.pack_start(read_art_btn, False, False, 0)

        kiwix_box.pack_start(search_row, False, False, 0)

        kiwix_pane = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.art_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.art_list_box.set_size_request(260, -1)
        kiwix_pane.pack1(self.art_list_box, False, False)

        art_scroll = Gtk.ScrolledWindow()
        self.art_view = Gtk.TextView()
        self.art_view.set_editable(False)
        self.art_view.set_cursor_visible(False)
        self.art_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.art_view.set_left_margin(12)
        self.art_view.set_right_margin(12)
        self.art_view.set_top_margin(10)
        art_scroll.add(self.art_view)
        kiwix_pane.pack2(art_scroll, True, False)

        kiwix_box.pack_start(kiwix_pane, True, True, 0)
        notebook.append_page(kiwix_box, Gtk.Label(label="📚 Offline Kiwix Encyclopedia"))

        # --- TAB 3: Teacher Shared Files & Course Worksheets ---
        files_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        files_box.set_margin_top(8)
        files_box.set_margin_bottom(8)
        files_box.set_margin_start(8)
        files_box.set_margin_end(8)

        files_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        files_lbl = Gtk.Label()
        files_lbl.set_markup("<b>📎 Teacher-Attached Course Files &amp; Worksheets (Local LAN)</b>")
        files_lbl.set_xalign(0)
        files_top.pack_start(files_lbl, True, True, 0)

        refresh_files_btn = Gtk.Button(label="🔄 Refresh Shared Files")
        refresh_files_btn.connect("clicked", lambda _b: self._populate_shared_files())
        files_top.pack_start(refresh_files_btn, False, False, 0)
        files_box.pack_start(files_top, False, False, 0)

        files_pane = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.shared_files_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.shared_files_list.set_size_request(250, -1)
        files_pane.pack1(self.shared_files_list, False, False)

        file_scroll = Gtk.ScrolledWindow()
        self.shared_file_view = Gtk.TextView()
        self.shared_file_view.set_editable(False)
        self.shared_file_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.shared_file_view.set_left_margin(10)
        self.shared_file_view.set_top_margin(8)
        file_scroll.add(self.shared_file_view)
        files_pane.pack2(file_scroll, True, False)

        files_box.pack_start(files_pane, True, True, 0)
        notebook.append_page(files_box, Gtk.Label(label="📎 Teacher Course Files"))

        self._select_episode(0)
        self._populate_kiwix_articles(OFFLINE_KIWIX_ARTICLES)
        self._populate_shared_files()
        return root

    def _select_episode(self, idx: int) -> None:
        self.current_episode_idx = idx % len(CURATED_VIDEO_EPISODES)
        self.play_elapsed_sec = 0.0
        self.is_playing = True
        ep = CURATED_VIDEO_EPISODES[self.current_episode_idx]
        if GTK_AVAILABLE and hasattr(self, "tv_title_lbl"):
            self.tv_title_lbl.set_markup(
                f"<span size='large' weight='bold' foreground='#fde047'>{GLib.markup_escape_text(ep['title'])}</span>  "
                f"<span size='small' foreground='#94a3b8'>[{GLib.markup_escape_text(ep['category'])}]</span>"
            )
            self.quiz_q_lbl.set_markup(f"<b>{GLib.markup_escape_text(ep['quiz_q'])}</b>")
            self.quiz_feedback_lbl.set_text("")
            for child in self.quiz_btns_box.get_children():
                self.quiz_btns_box.remove(child)
            for opt_text, is_correct in ep["quiz_options"]:
                b = Gtk.Button(label=opt_text)
                b.connect("clicked", self._on_quiz_answer, is_correct)
                self.quiz_btns_box.pack_start(b, False, False, 0)
            self.quiz_btns_box.show_all()
            self._update_subtitle_and_progress()
            self.tv_area.queue_draw()

    def _on_quiz_answer(self, _btn, is_correct: bool) -> None:
        if is_correct:
            self.quiz_feedback_lbl.set_markup(
                "<span foreground='#4ade80' weight='bold'>🌟 Correct! Great scientific thinking!</span>"
            )
        else:
            self.quiz_feedback_lbl.set_markup(
                "<span foreground='#fbbf24' weight='bold'>💡 Not quite—watch the animation clues and try again!</span>"
            )

    def _on_toggle_play(self, _btn) -> None:
        self.is_playing = not self.is_playing
        self.play_btn.set_label("⏸ Pause" if self.is_playing else "▶ Play")

    def _on_restart_ep(self, _btn) -> None:
        self.play_elapsed_sec = 0.0
        self.is_playing = True
        self.play_btn.set_label("⏸ Pause")
        self._update_subtitle_and_progress()

    def _on_narrate_ep(self, _btn) -> None:
        ep = CURATED_VIDEO_EPISODES[self.current_episode_idx]
        if self.speak_callback:
            self.speak_callback(ep["narration"])

    def _update_subtitle_and_progress(self) -> None:
        ep = CURATED_VIDEO_EPISODES[self.current_episode_idx]
        dur = float(ep["duration_sec"])
        t = self.play_elapsed_sec % dur
        sub_text = ep["narration"]
        for t0, t1, txt in ep["subtitles"]:
            if t0 <= t <= t1:
                sub_text = txt
                break
        self.subtitle_lbl.set_markup(
            f"<span size='medium' weight='bold' foreground='#f8fafc' background='#0f172a'>  {GLib.markup_escape_text(sub_text)}  </span>"
        )
        frac = min(1.0, max(0.0, t / dur))
        self.progress_bar.set_fraction(frac)
        self.progress_bar.set_text(f"{int(t)}s / {int(dur)}s")

    def _on_anim_tick(self) -> bool:
        now = time.perf_counter()
        dt = min(0.1, max(0.0, now - self._last_tick))
        self._last_tick = now
        if self.is_playing and hasattr(self, "tv_area") and self.tv_area.get_mapped():
            self.play_elapsed_sec = (self.play_elapsed_sec + dt * 2.2) % 30.0
            self._update_subtitle_and_progress()
            self.tv_area.queue_draw()
        return True

    def _on_draw_tv(self, widget, cr) -> bool:
        w = max(320, widget.get_allocated_width())
        h = max(180, widget.get_allocated_height())
        t = self.play_elapsed_sec

        # Deep space / classroom blackboard background
        cr.set_source_rgb(0.05, 0.08, 0.14)
        cr.rectangle(0, 0, w, h)
        cr.fill()

        idx = self.current_episode_idx
        if idx == 0:
            # Ep 1: Animated Moon Lander Descent with Gravity & Thrust Vectors
            # Stars
            cr.set_source_rgb(0.85, 0.9, 1.0)
            for s in range(18):
                sx = (s * 73) % w
                sy = (s * 41) % int(h * 0.65)
                cr.arc(sx, sy, 1.5, 0, 2 * math.pi)
                cr.fill()
            # Lunar surface + landing pad
            ground_y = h * 0.82
            cr.set_source_rgb(0.28, 0.32, 0.38)
            cr.rectangle(0, ground_y, w, h - ground_y)
            cr.fill()
            pad_x = w * 0.5
            cr.set_source_rgb(0.98, 0.82, 0.18)
            cr.rectangle(pad_x - 55, ground_y - 4, 110, 6)
            cr.fill()

            # Descending rocket
            progress = min(1.0, (t % 15.0) / 13.0)
            ry = 35 + (ground_y - 60) * (1.0 - (1.0 - progress) ** 1.6)
            rx = pad_x + math.sin(t * 1.4) * (1.0 - progress) * 45.0

            # Flame when slowing down
            if progress < 0.95:
                flame_len = 16 + 12 * abs(math.sin(t * 12))
                cr.set_source_rgb(1.0, 0.55, 0.1)
                cr.move_to(rx - 9, ry + 18)
                cr.line_to(rx + 9, ry + 18)
                cr.line_to(rx, ry + 18 + flame_len)
                cr.close_path()
                cr.fill()

            # Rocket hull
            cr.set_source_rgb(0.22, 0.78, 0.98)
            cr.rectangle(rx - 14, ry - 14, 28, 30)
            cr.fill()

            # HUD telemetry overlay
            vy = round((1.0 - progress) * 8.5, 1)
            cr.set_source_rgb(0.4, 0.95, 0.6)
            cr.select_font_face("Sans", 0, 1)
            cr.set_font_size(13)
            cr.move_to(16, 26)
            cr.show_text(f"Altitude Y: {int(max(0, ground_y - 25 - ry))} m   |   Downward Speed Vy: {vy} m/s")
        elif idx == 1:
            # Ep 2: Animated Neural Network pulsing signals
            layers = [3, 4, 2]
            xs = [w * 0.2, w * 0.5, w * 0.8]
            nodes = []
            for l_idx, count in enumerate(layers):
                col = []
                for n_idx in range(count):
                    ny = h * (0.22 + 0.56 * (n_idx / max(1, count - 1)))
                    col.append((xs[l_idx], ny))
                nodes.append(col)

            # Draw synapses with pulsing signal dots
            for l_idx in range(len(layers) - 1):
                for i, (x1, y1) in enumerate(nodes[l_idx]):
                    for j, (x2, y2) in enumerate(nodes[l_idx + 1]):
                        positive = ((i + j + l_idx) % 2 == 0)
                        if positive:
                            cr.set_source_rgba(0.2, 0.9, 0.5, 0.65)
                        else:
                            cr.set_source_rgba(0.95, 0.35, 0.35, 0.55)
                        cr.set_line_width(2.2)
                        cr.move_to(x1, y1)
                        cr.line_to(x2, y2)
                        cr.stroke()

                        # Traveling pulse
                        pulse = (t * 0.9 + (i * 0.2) + (j * 0.15)) % 1.0
                        px = x1 + (x2 - x1) * pulse
                        py = y1 + (y2 - y1) * pulse
                        cr.set_source_rgb(1.0, 0.92, 0.3)
                        cr.arc(px, py, 4.0, 0, 2 * math.pi)
                        cr.fill()

            # Draw neuron circles
            labels = ["Sensors (X, Y, Vy)", "Hidden Layer (Synapses)", "Actions (Thrust / Steer)"]
            for l_idx, col in enumerate(nodes):
                for (nx, ny) in col:
                    cr.set_source_rgb(0.15, 0.65, 0.95)
                    cr.arc(nx, ny, 13, 0, 2 * math.pi)
                    cr.fill()
                cr.set_source_rgb(0.9, 0.95, 1.0)
                cr.set_font_size(12)
                cr.move_to(xs[l_idx] - 55, h - 16)
                cr.show_text(labels[l_idx])
        elif idx == 2:
            # Ep 3: Raycast Self-Driving Car scanning road walls
            road_y1, road_y2 = h * 0.22, h * 0.78
            cr.set_source_rgb(0.2, 0.24, 0.3)
            cr.rectangle(20, road_y1, w - 40, road_y2 - road_y1)
            cr.fill()
            cr.set_source_rgb(0.95, 0.75, 0.2)
            cr.set_line_width(3)
            cr.move_to(20, road_y1)
            cr.line_to(w - 20, road_y1)
            cr.move_to(20, road_y2)
            cr.line_to(w - 20, road_y2)
            cr.stroke()

            cx = 70 + ((t * 45) % (w - 180))
            cy = (road_y1 + road_y2) * 0.5 + math.sin(t * 2.0) * 28.0
            # 5 LIDAR beams
            for angle_deg in (-50, -25, 0, 25, 50):
                rad = math.radians(angle_deg)
                beam_len = 95 + 25 * math.cos(rad)
                bx = cx + math.cos(rad) * beam_len
                by = max(road_y1 + 4, min(road_y2 - 4, cy + math.sin(rad) * beam_len))
                cr.set_source_rgba(0.2, 0.95, 0.55, 0.85)
                cr.set_line_width(2.0)
                cr.move_to(cx, cy)
                cr.line_to(bx, by)
                cr.stroke()
                cr.arc(bx, by, 4, 0, 2 * math.pi)
                cr.fill()

            # Car body
            cr.set_source_rgb(0.95, 0.3, 0.35)
            cr.rectangle(cx - 18, cy - 11, 36, 22)
            cr.fill()
        else:
            # Ep 4: 1.58-Bit Ternary {-1, 0, +1} & POPCNT Bit-Slicing
            cr.set_source_rgb(0.35, 0.9, 0.98)
            cr.set_font_size(14)
            cr.move_to(24, 34)
            cr.show_text("1.58-Bit Ternary Bit-Sliced POPCNT Engine (64 Weights per CPU Register)")
            trits = [-1, +1, 0, +1, -1, +1, +1, 0, -1, +1, 0, +1]
            box_w = (w - 60) / len(trits)
            active_slot = int(t * 4) % len(trits)
            for i, val in enumerate(trits):
                bx = 30 + i * box_w
                by = h * 0.42
                if val == 1:
                    cr.set_source_rgb(0.18, 0.82, 0.48)
                elif val == -1:
                    cr.set_source_rgb(0.92, 0.32, 0.36)
                else:
                    cr.set_source_rgb(0.35, 0.4, 0.48)
                cr.rectangle(bx + 2, by, box_w - 6, 48)
                cr.fill()
                if i == active_slot:
                    cr.set_source_rgb(1.0, 0.9, 0.2)
                    cr.set_line_width(3)
                    cr.rectangle(bx + 2, by, box_w - 6, 48)
                    cr.stroke()
                cr.set_source_rgb(1.0, 1.0, 1.0)
                cr.set_font_size(14)
                cr.move_to(bx + box_w * 0.28, by + 30)
                cr.show_text(f"{val:+d}" if val != 0 else " 0")

            cr.set_source_rgb(0.65, 0.95, 0.75)
            cr.move_to(24, h * 0.78)
            cr.show_text("⚡ CPU POPCNT Throughput: 12.99x Faster than FP32  |  PRIME Memory: 262 KB Fixed L2 State")

        return False

    def _populate_kiwix_articles(self, articles: List[Dict[str, str]]) -> None:
        if not GTK_AVAILABLE or not hasattr(self, "art_list_box"):
            return
        for child in self.art_list_box.get_children():
            self.art_list_box.remove(child)
        for art in articles:
            btn = Gtk.Button(label=f"{art['title']}\n[{art['category']}]")
            btn.connect("clicked", lambda _b, a=art: self._show_article(a))
            self.art_list_box.pack_start(btn, False, False, 0)
        self.art_list_box.show_all()
        if articles:
            self._show_article(articles[0])

    def _show_article(self, art: Dict[str, str]) -> None:
        self._current_article = art
        buf = self.art_view.get_buffer()
        text = f"{art['title']}\nCategory: {art['category']}\n{'=' * 56}\n\n{art['body']}"
        buf.set_text(text)

    def _on_kiwix_search_changed(self, entry) -> None:
        results = self.search_encyclopedia(entry.get_text())
        self._populate_kiwix_articles(results)

    def _on_read_article_aloud(self, _btn) -> None:
        art = getattr(self, "_current_article", OFFLINE_KIWIX_ARTICLES[0])
        if self.speak_callback:
            self.speak_callback(f"{art['title']}. {art['summary']}")

    def _populate_shared_files(self) -> None:
        if not GTK_AVAILABLE or not hasattr(self, "shared_files_list") or not self.classroom_hub:
            return
        for child in self.shared_files_list.get_children():
            self.shared_files_list.remove(child)
        files = self.classroom_hub.list_attached_files()
        for fmeta in files:
            btn = Gtk.Button(label=f"📄 {fmeta['name']} ({fmeta['size_kb']} KB)")
            btn.connect("clicked", lambda _b, fn=fmeta["name"]: self._show_shared_file(fn))
            self.shared_files_list.pack_start(btn, False, False, 0)
        self.shared_files_list.show_all()
        if files:
            self._show_shared_file(files[0]["name"])

    def _show_shared_file(self, filename: str) -> None:
        if not self.classroom_hub:
            return
        content = self.classroom_hub.read_attached_file(filename)
        buf = self.shared_file_view.get_buffer()
        buf.set_text(f"📎 Classroom Shared File: {filename}\n{'=' * 52}\n\n{content}")


def show_safe_media_dialog(
    parent_window: Optional[Any] = None,
    classroom_hub: Optional[Any] = None,
    speak_callback: Optional[Callable[[str], None]] = None,
) -> Optional[Any]:
    """Opens the Safe Media & Offline Kiwix Sandbox in a modal/non-modal classroom dialog."""
    if not GTK_AVAILABLE:
        return None
    dlg = Gtk.Dialog(
        title="🛡️ SynapseOS Safe Media & Offline Kiwix Encyclopedia",
        transient_for=parent_window,
        flags=0,
    )
    dlg.set_default_size(940, 560)
    dlg.add_button("Close Safe Media Sandbox", Gtk.ResponseType.CLOSE)
    sandbox = SafeMediaSandboxWidget(classroom_hub=classroom_hub, speak_callback=speak_callback)
    content = dlg.get_content_area()
    content.pack_start(sandbox.widget, True, True, 0)
    dlg.show_all()
    dlg.connect("response", lambda d, _r: d.destroy())
    return dlg
