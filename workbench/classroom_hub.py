"""
SynapseOS Local Classroom Hub (Offline LAN Broadcast, Course & File Sharing,
Schedule Manager, and Real-Time Student 'Hands-Up' Q&A).

Designed for 100% Potato Hardware compatibility (2007-2017 laptops & Chromebooks):
- Zero external Python dependencies (uses standard library `socket`, `json`, `threading`, `os`).
- Works over Offline Classroom LAN (UDP Broadcast on port 50505) AND local shared state
  (`/tmp/synapse_classroom_hub.json`) so teachers and students can test on 1 PC or 30 PCs
  with zero internet connection required.
"""

import json
import os
import shutil
import socket
import threading
import time
from typing import Any, Callable, Dict, List, Optional


DEFAULT_HUB_STATE_PATH = "/tmp/synapse_classroom_hub.json"
DEFAULT_SHARED_FILES_DIR = "/tmp/synapse_classroom_files"
LAN_UDP_PORT = 50505


DEFAULT_SCHEDULE: List[Dict[str, str]] = [
    {
        "period": "Period 1 (08:30 - 09:15)",
        "title": "Warm-Up: Meet Lumi & Rocket Landing Physics",
        "lab_id": "moon_lander",
        "mode": "Kid Arcade (Level 1-2)",
        "notes": "Students practice gentle thrust control and ask Lumi how gravity affects velocity."
    },
    {
        "period": "Period 2 (09:20 - 10:05)",
        "title": "Neuroevolution Lab: Evolving Self-Driving Sensor Cars",
        "lab_id": "raycast_car",
        "mode": "Student Mode (Sliders)",
        "notes": "Tune Population Size (120) and Mutation Power (0.45) to clear 5 checkpoints."
    },
    {
        "period": "Period 3 (10:15 - 11:00)",
        "title": "Safe Media Research: How Neural Networks & Rockets Work",
        "lab_id": "safe_media",
        "mode": "Safe Media & Kiwix Sandbox",
        "notes": "Watch Episode 1 & read the offline Kiwix article on Reinforcement Learning."
    },
    {
        "period": "Period 4 (11:05 - 11:50)",
        "title": "Python AI Studio: Inspecting Rewards & Ternary POPCNT Speed",
        "lab_id": "cartpole_rl",
        "mode": "Teacher / Python Studio",
        "notes": "Compare PPO policy gradients and inspect the 1.58-bit Ternary + PRIME C engine."
    },
]


DEFAULT_COURSES: List[Dict[str, Any]] = [
    {
        "course_id": "course_rocket_101",
        "title": "Course 1: Lunar Lander & Gravity Control (Grades 4-8)",
        "lab_id": "moon_lander",
        "target_mode": "kid",
        "description": "Learn how thrust, fuel, and sensor inputs help an AI land safely on the Moon.",
        "starter_code": (
            "# Course 1: Custom Lunar Lander Fitness Function\n"
            "def compute_reward(dist_to_pad, velocity, fuel_used, landed):\n"
            "    reward = 100.0 * (1.0 - dist_to_pad)\n"
            "    reward -= 40.0 * abs(velocity)\n"
            "    reward -= 0.2 * fuel_used\n"
            "    if landed:\n"
            "        reward += 200.0\n"
            "    return reward\n"
        ),
        "attached_files": ["lunar_mission_worksheet.md"],
        "timestamp": "Built-in Curriculum",
    },
    {
        "course_id": "course_autonomous_driving",
        "title": "Course 2: Self-Driving Raycast Cars & LIDAR Sensors (Grades 6-12)",
        "lab_id": "raycast_car",
        "target_mode": "student",
        "description": "Use 5 raycast distance beams to steer an autonomous vehicle around a track using NEAT.",
        "starter_code": (
            "# Course 2: 5-Beam Raycast Steering Policy\n"
            "def steer_from_rays(ray_left, ray_fl, ray_center, ray_fr, ray_right):\n"
            "    # Steer toward the widest open distance beam\n"
            "    turn = (ray_right + 0.6 * ray_fr) - (ray_left + 0.6 * ray_fl)\n"
            "    throttle = 1.0 if ray_center > 0.35 else 0.4\n"
            "    return turn, throttle\n"
        ),
        "attached_files": ["lidar_sensor_guide.md"],
        "timestamp": "Built-in Curriculum",
    },
    {
        "course_id": "course_prime_ternary",
        "title": "Course 3: Tiny AI on Old Laptops — 1.58-Bit Ternary & PRIME Attention",
        "lab_id": "prime_attention",
        "target_mode": "teacher",
        "description": "Explore how bit-sliced POPCNT ternary weights {-1, 0, +1} and O(D^2) PRIME moments run 13x faster on CPUs.",
        "starter_code": (
            "# Course 3: Bit-Sliced Ternary Dot Product Concept\n"
            "# Instead of FP32 multiply-accumulate, we use bitwise AND + POPCNT:\n"
            "def ternary_dot_concept(pos_mask, neg_mask, act_pos, act_neg):\n"
            "    pos_hits = bin((pos_mask & act_pos) | (neg_mask & act_neg)).count('1')\n"
            "    neg_hits = bin((pos_mask & act_neg) | (neg_mask & act_pos)).count('1')\n"
            "    return pos_hits - neg_hits\n"
        ),
        "attached_files": ["potato_ai_architecture.md"],
        "timestamp": "Built-in Curriculum",
    },
]


class ClassroomHubManager:
    """
    Manages Teacher <-> Student Offline LAN communication:
    - Broadcasting lessons, code snippets, schedules, and attached course files
    - Real-time Student "✋ Hands-Up & Q&A" queue with Teacher reply notifications
    - Live Student Roster (which lab/level each student PC is running)
    """

    def __init__(
        self,
        state_path: str = DEFAULT_HUB_STATE_PATH,
        shared_files_dir: str = DEFAULT_SHARED_FILES_DIR,
        enable_udp: bool = True,
    ):
        self.state_path = state_path
        self.shared_files_dir = shared_files_dir
        self.enable_udp = enable_udp
        self._lock = threading.Lock()
        self.hostname = socket.gethostname()
        self.local_ip = self._detect_local_ip()
        self._listeners: List[Callable[[Dict[str, Any]], None]] = []
        self._stop_event = threading.Event()

        os.makedirs(self.shared_files_dir, exist_ok=True)
        self._ensure_default_state()

        if self.enable_udp:
            self._start_udp_listener()

    @staticmethod
    def _detect_local_ip() -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.1)
            s.connect(("10.255.255.255", 1))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def _ensure_default_state(self) -> None:
        # Create sample worksheet files in shared_files_dir
        sample_files = {
            "lunar_mission_worksheet.md": (
                "# Lunar Lander Mission Worksheet\n\n"
                "1. **Goal**: Land gently between the two yellow flags with vertical speed < 2.5 m/s.\n"
                "2. **Experiment**: Set Gravity to Moon (-1.62) first, then try Mars (-3.72).\n"
                "3. **Question for Lumi**: Why does a higher mutation rate cause some rockets to spin?\n"
            ),
            "lidar_sensor_guide.md": (
                "# Autonomous Car LIDAR Raycast Guide\n\n"
                "- Each green beam measures the distance (`0.0` to `1.0`) to the nearest wall.\n"
                "- The NEAT neural network takes 5 raycast inputs + speed and outputs steering & throttle.\n"
            ),
            "potato_ai_architecture.md": (
                "# Running Modern AI on 2009 Laptops\n\n"
                "- **SQLite FTS5 (`<1ms`)**: Instant offline retrieval without loading heavy neural weights.\n"
                "- **1.58-Bit Ternary (`trit64`)**: Packs 64 weights into two `uint64_t` masks using CPU `POPCNT`.\n"
                "- **PRIME Moment Attention**: Replaces growing KV caches with a fixed `262 KB` L2-resident state.\n"
            ),
        }
        for fname, content in sample_files.items():
            fpath = os.path.join(self.shared_files_dir, fname)
            if not os.path.exists(fpath):
                try:
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(content)
                except Exception:
                    pass

        if not os.path.exists(self.state_path):
            initial_state = {
                "updated_at": time.time(),
                "teacher_host": f"{self.hostname} ({self.local_ip})",
                "schedule": list(DEFAULT_SCHEDULE),
                "courses": list(DEFAULT_COURSES),
                "active_broadcast": {
                    "id": "welcome_broadcast",
                    "title": "Welcome to SynapseOS Classroom Hub!",
                    "message": "Today's focus: Evolve a Lunar Lander in Kid Arcade or Student Mode. Click '✋ Raise Hand' anytime you need help!",
                    "lab_id": "moon_lander",
                    "code_snippet": DEFAULT_COURSES[0]["starter_code"],
                    "attached_files": ["lunar_mission_worksheet.md"],
                    "timestamp": time.strftime("%H:%M:%S"),
                },
                "hands_up_queue": [
                    {
                        "id": "hand_demo_1",
                        "student_name": "Maya (Station-04)",
                        "host": "macbook-2009-04.local",
                        "lab_id": "moon_lander",
                        "level": "Level 2: Autopilot",
                        "question": "My rocket hovers above the pad instead of touching down. Which slider should I lower?",
                        "status": "open",
                        "teacher_reply": "",
                        "timestamp": time.strftime("%H:%M:%S"),
                    }
                ],
                "students_roster": {
                    "Station-01 (2009 MacBook Pro)": {
                        "student_name": "Djiby (Station-01)",
                        "ip": self.local_ip,
                        "active_lab": "moon_lander",
                        "mode": "Kid Arcade (Level 2)",
                        "best_score": "+218.4 (Landed!)",
                        "status": "Active",
                        "last_seen": time.strftime("%H:%M:%S"),
                    },
                    "Station-04 (ThinkPad X220)": {
                        "student_name": "Maya (Station-04)",
                        "ip": "192.168.1.104",
                        "active_lab": "moon_lander",
                        "mode": "Kid Arcade (Level 2)",
                        "best_score": "+142.0",
                        "status": "✋ Hand Raised",
                        "last_seen": time.strftime("%H:%M:%S"),
                    },
                    "Station-07 (Chromebook 2GB)": {
                        "student_name": "Leo (Station-07)",
                        "ip": "192.168.1.107",
                        "active_lab": "raycast_car",
                        "mode": "Student Sliders",
                        "best_score": "+310.5 (5 Laps)",
                        "status": "Active",
                        "last_seen": time.strftime("%H:%M:%S"),
                    },
                },
            }
            self._save_state(initial_state)

    def _load_state(self) -> Dict[str, Any]:
        with self._lock:
            try:
                if os.path.exists(self.state_path):
                    with open(self.state_path, "r", encoding="utf-8") as f:
                        return json.load(f)
            except Exception:
                pass
            return {
                "updated_at": time.time(),
                "teacher_host": f"{self.hostname} ({self.local_ip})",
                "schedule": list(DEFAULT_SCHEDULE),
                "courses": list(DEFAULT_COURSES),
                "active_broadcast": {},
                "hands_up_queue": [],
                "students_roster": {},
            }

    def _save_state(self, state: Dict[str, Any]) -> None:
        state["updated_at"] = time.time()
        with self._lock:
            try:
                tmp_path = f"{self.state_path}.tmp"
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(state, f, indent=2)
                os.replace(tmp_path, self.state_path)
            except Exception:
                pass

    def _broadcast_udp_packet(self, packet_type: str, payload: Dict[str, Any]) -> None:
        if not self.enable_udp:
            return
        msg = json.dumps({"type": packet_type, "payload": payload, "sender": self.local_ip}).encode("utf-8")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(0.05)
            # Send to LAN broadcast and localhost loopback
            for target in ("255.255.255.255", "127.0.0.1"):
                try:
                    sock.sendto(msg[:8192], (target, LAN_UDP_PORT))
                except Exception:
                    pass
            sock.close()
        except Exception:
            pass

    def _start_udp_listener(self) -> None:
        def _listen():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                if hasattr(socket, "SO_REUSEPORT"):
                    try:
                        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                    except Exception:
                        pass
                sock.bind(("", LAN_UDP_PORT))
                sock.settimeout(0.5)
            except Exception:
                return

            while not self._stop_event.is_set():
                try:
                    data, _addr = sock.recvfrom(16384)
                    pkt = json.loads(data.decode("utf-8"))
                    self._handle_incoming_udp(pkt)
                except socket.timeout:
                    continue
                except Exception:
                    continue
            try:
                sock.close()
            except Exception:
                pass

        t = threading.Thread(target=_listen, daemon=True)
        t.start()

    def _handle_incoming_udp(self, pkt: Dict[str, Any]) -> None:
        ptype = pkt.get("type", "")
        payload = pkt.get("payload", {})
        state = self._load_state()
        changed = False

        if ptype == "teacher_broadcast":
            state["active_broadcast"] = payload
            changed = True
        elif ptype == "raise_hand":
            queue = state.setdefault("hands_up_queue", [])
            if not any(h.get("id") == payload.get("id") for h in queue):
                queue.insert(0, payload)
                changed = True
        elif ptype == "reply_hand":
            for h in state.get("hands_up_queue", []):
                if h.get("id") == payload.get("id"):
                    h["teacher_reply"] = payload.get("teacher_reply", "")
                    h["status"] = payload.get("status", "answered")
                    changed = True
        elif ptype == "student_heartbeat":
            station_key = payload.get("station_key", "Student-PC")
            state.setdefault("students_roster", {})[station_key] = payload
            changed = True

        if changed:
            self._save_state(state)
            for cb in list(self._listeners):
                try:
                    cb(state)
                except Exception:
                    pass

    def register_listener(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        if callback not in self._listeners:
            self._listeners.append(callback)

    # ------------------------------------------------------------------
    # Teacher Features: Schedule, File Attachments, Course Upload & Broadcast
    # ------------------------------------------------------------------
    def get_state(self) -> Dict[str, Any]:
        return self._load_state()

    def get_schedule(self) -> List[Dict[str, str]]:
        return self._load_state().get("schedule", list(DEFAULT_SCHEDULE))

    def add_schedule_item(self, period: str, title: str, lab_id: str, mode: str, notes: str = "") -> List[Dict[str, str]]:
        state = self._load_state()
        sched = state.setdefault("schedule", [])
        sched.append({
            "period": period.strip() or f"Period {len(sched) + 1}",
            "title": title.strip() or "AI Lab Session",
            "lab_id": lab_id.strip() or "moon_lander",
            "mode": mode.strip() or "Student Mode",
            "notes": notes.strip(),
        })
        self._save_state(state)
        return sched

    def remove_schedule_item(self, index: int) -> List[Dict[str, str]]:
        state = self._load_state()
        sched = state.get("schedule", [])
        if 0 <= index < len(sched):
            sched.pop(index)
            self._save_state(state)
        return sched

    def attach_file(self, source_path: str) -> Optional[str]:
        """Copies a teacher's local file into the shared classroom attachments folder."""
        if not source_path or not os.path.isfile(source_path):
            return None
        fname = os.path.basename(source_path)
        dest = os.path.join(self.shared_files_dir, fname)
        try:
            if os.path.abspath(source_path) != os.path.abspath(dest):
                shutil.copy2(source_path, dest)
            return fname
        except Exception:
            return None

    def list_attached_files(self) -> List[Dict[str, Any]]:
        files = []
        try:
            for fname in sorted(os.listdir(self.shared_files_dir)):
                fpath = os.path.join(self.shared_files_dir, fname)
                if os.path.isfile(fpath):
                    size_kb = round(os.path.getsize(fpath) / 1024.0, 1)
                    files.append({"name": fname, "path": fpath, "size_kb": size_kb})
        except Exception:
            pass
        return files

    def read_attached_file(self, filename: str) -> str:
        fpath = os.path.join(self.shared_files_dir, os.path.basename(filename))
        if not os.path.isfile(fpath):
            return f"File '{filename}' not found in classroom hub."
        try:
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                return f.read(16384)
        except Exception as e:
            return f"Could not read file: {e}"

    def upload_course(
        self,
        title: str,
        lab_id: str,
        description: str,
        starter_code: str = "",
        attached_files: Optional[List[str]] = None,
        target_mode: str = "student",
    ) -> Dict[str, Any]:
        state = self._load_state()
        course = {
            "course_id": f"course_{int(time.time() * 1000)}",
            "title": title.strip() or "Custom Classroom Module",
            "lab_id": lab_id.strip() or "moon_lander",
            "target_mode": target_mode,
            "description": description.strip(),
            "starter_code": starter_code,
            "attached_files": list(attached_files or []),
            "timestamp": time.strftime("%Y-%m-%d %H:%M"),
        }
        state.setdefault("courses", []).insert(0, course)
        self._save_state(state)
        return course

    def broadcast_to_classroom(
        self,
        title: str,
        message: str,
        lab_id: str = "moon_lander",
        code_snippet: str = "",
        attached_files: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """1-Click LAN Broadcast from Teacher to all Student PCs."""
        state = self._load_state()
        bcast = {
            "id": f"bcast_{int(time.time() * 1000)}",
            "title": title.strip() or "Teacher Classroom Broadcast",
            "message": message.strip(),
            "lab_id": lab_id.strip() or "moon_lander",
            "code_snippet": code_snippet,
            "attached_files": list(attached_files or []),
            "teacher_host": f"{self.hostname} ({self.local_ip})",
            "timestamp": time.strftime("%H:%M:%S"),
        }
        state["active_broadcast"] = bcast
        self._save_state(state)
        self._broadcast_udp_packet("teacher_broadcast", bcast)
        return bcast

    # ------------------------------------------------------------------
    # Student Features: Real-Time "✋ Raise Hand / Q&A" & Heartbeat
    # ------------------------------------------------------------------
    def raise_hand(
        self,
        student_name: str,
        question: str,
        lab_id: str = "moon_lander",
        level: str = "Kid Arcade",
    ) -> Dict[str, Any]:
        """Student clicks '✋ Raise Hand / Ask Teacher' to alert the teacher on LAN."""
        state = self._load_state()
        entry = {
            "id": f"hand_{int(time.time() * 1000)}",
            "student_name": student_name.strip() or f"Student ({self.hostname})",
            "host": f"{self.hostname} ({self.local_ip})",
            "lab_id": lab_id,
            "level": level,
            "question": question.strip() or "I need help with this lab step, please!",
            "status": "open",
            "teacher_reply": "",
            "timestamp": time.strftime("%H:%M:%S"),
        }
        state.setdefault("hands_up_queue", []).insert(0, entry)
        # Also update student status in roster
        station_key = f"{entry['student_name']}"
        state.setdefault("students_roster", {})[station_key] = {
            "student_name": entry["student_name"],
            "ip": self.local_ip,
            "active_lab": lab_id,
            "mode": level,
            "best_score": "Working...",
            "status": "✋ Hand Raised",
            "last_seen": entry["timestamp"],
        }
        self._save_state(state)
        self._broadcast_udp_packet("raise_hand", entry)
        return entry

    def reply_to_hand(self, hand_id: str, teacher_reply: str) -> Optional[Dict[str, Any]]:
        """Teacher sends an instant answer/hint back to a student's raised hand."""
        state = self._load_state()
        target = None
        for h in state.get("hands_up_queue", []):
            if h.get("id") == hand_id:
                h["teacher_reply"] = teacher_reply.strip()
                h["status"] = "answered"
                target = h
                break
        if target:
            # Update roster status
            sname = target.get("student_name", "")
            if sname in state.get("students_roster", {}):
                state["students_roster"][sname]["status"] = "✅ Answered by Teacher"
            self._save_state(state)
            self._broadcast_udp_packet("reply_hand", target)
        return target

    def update_student_telemetry(
        self,
        student_name: str,
        active_lab: str,
        mode: str,
        best_score: str,
        status: str = "Active",
    ) -> None:
        state = self._load_state()
        payload = {
            "station_key": student_name,
            "student_name": student_name,
            "ip": self.local_ip,
            "active_lab": active_lab,
            "mode": mode,
            "best_score": best_score,
            "status": status,
            "last_seen": time.strftime("%H:%M:%S"),
        }
        state.setdefault("students_roster", {})[student_name] = payload
        self._save_state(state)
        self._broadcast_udp_packet("student_heartbeat", payload)
