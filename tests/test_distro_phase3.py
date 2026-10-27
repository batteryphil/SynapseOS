"""
Unit & Integration Tests for SynapseOS Phase 3:
  - Debian 12 (Bookworm) Minimal Potato Package Manifest
  - LZ4 ZRAM (`zramswap`) & Kernel Sysctl (`99-synapse-potato.conf`)
  - Zero-RAM Display-Manager-Free Auto-Login (`autologin.conf`, `.bash_profile`, `.xinitrc`)
  - Openbox XML (`menu.xml`, `rc.xml`), Autostart & Tint2 Panel (`tint2rc`)
  - `build-iso.sh --dry-run` Validation
"""

import unittest
import os
import subprocess
import xml.etree.ElementTree as ET

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DISTRO_DIR = os.path.join(PROJECT_ROOT, "distro")


class TestDistroPhase3(unittest.TestCase):
    def test_debian12_potato_package_manifest(self):
        pkg_file = os.path.join(DISTRO_DIR, "packages.list")
        self.assertTrue(os.path.exists(pkg_file))
        with open(pkg_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Required potato & AI workbench packages
        for req in [
            "linux-image-amd64",
            "live-boot",
            "zram-tools",
            "xserver-xorg-core",
            "xinit",
            "openbox",
            "tint2",
            "pcmanfm",
            "python3-gi",
            "python3-gi-cairo",
            "gir1.2-gtk-3.0"
        ]:
            self.assertIn(req, content, f"Missing required package: {req}")

        # Ensure zero bloated desktop managers or snapd
        for bloat in ["gnome-shell", "plasma-desktop", "snapd", "gdm3"]:
            self.assertNotIn(bloat, content, f"Bloated package {bloat} must not be in potato manifest")

    def test_zram_and_sysctl_potato_tuning(self):
        zram_path = os.path.join(DISTRO_DIR, "config", "zramswap")
        sysctl_path = os.path.join(DISTRO_DIR, "config", "99-synapse-potato.conf")
        self.assertTrue(os.path.exists(zram_path))
        self.assertTrue(os.path.exists(sysctl_path))

        with open(zram_path, "r", encoding="utf-8") as f:
            zram = f.read()
        self.assertIn("ALGO=lz4", zram)
        self.assertIn("PERCENT=50", zram)

        with open(sysctl_path, "r", encoding="utf-8") as f:
            sysctl = f.read()
        self.assertIn("vm.swappiness = 25", sysctl)
        self.assertIn("vm.page-cluster = 0", sysctl)
        self.assertIn("kernel.sched_autogroup_enabled = 1", sysctl)

        # Verify SIMD / ZRAM-safe inference options in CortexEngine
        from cortex.engine import CortexEngine
        eng = CortexEngine()
        opts = eng.get_inference_options()
        self.assertIn("num_thread", opts)
        self.assertIn("num_ctx", opts)
        self.assertIn(opts["num_ctx"], (256, 1024, 2048, 4096))

    def test_openbox_xml_validity_and_autostart(self):
        menu_xml = os.path.join(DISTRO_DIR, "skel", ".config", "openbox", "menu.xml")
        rc_xml = os.path.join(DISTRO_DIR, "skel", ".config", "openbox", "rc.xml")
        autostart = os.path.join(DISTRO_DIR, "skel", ".config", "openbox", "autostart")
        tint2rc = os.path.join(DISTRO_DIR, "skel", ".config", "tint2", "tint2rc")

        for p in (menu_xml, rc_xml, autostart, tint2rc):
            self.assertTrue(os.path.exists(p), f"Missing desktop config: {p}")

        # Parse XML files to verify well-formed syntax
        ET.parse(menu_xml)
        ET.parse(rc_xml)

        with open(autostart, "r", encoding="utf-8") as f:
            auto_txt = f.read()
        self.assertIn("synapse-studio", auto_txt)
        self.assertIn("tint2", auto_txt)

    def test_zero_dm_autologin_pipeline(self):
        autologin = os.path.join(DISTRO_DIR, "config", "autologin.conf")
        bash_prof = os.path.join(DISTRO_DIR, "skel", ".bash_profile")
        xinitrc = os.path.join(DISTRO_DIR, "skel", ".xinitrc")

        for p in (autologin, bash_prof, xinitrc):
            self.assertTrue(os.path.exists(p), f"Missing autologin file: {p}")

        with open(autologin, "r", encoding="utf-8") as f:
            self.assertIn("--autologin synapse", f.read())

        with open(xinitrc, "r", encoding="utf-8") as f:
            xinit_txt = f.read()
            self.assertIn("exec openbox", xinit_txt)
            self.assertIn("preload_model", xinit_txt)

    def test_buildbit_potato_kernels(self):
        from workbench.labs.c_sim_bridge import benchmark_buildbit_potato_kernels
        res = benchmark_buildbit_potato_kernels(dim=512, n_tokens=16)
        self.assertTrue(res.get("available"))
        self.assertTrue(res.get("trit_exact_match"))
        self.assertGreater(res.get("trit_speedup", 0.0), 2.0)
        self.assertGreater(res.get("prime_tok_per_sec", 0.0), 1000.0)


    def test_build_iso_dry_run(self):
        script = os.path.join(DISTRO_DIR, "build-iso.sh")
        res = subprocess.run([script, "--dry-run"], capture_output=True, text=True, timeout=10)
        self.assertEqual(res.returncode, 0, f"build-iso.sh --dry-run failed: {res.stderr}")
        self.assertIn("SynapseOS-Debian12-Potato-x86_64.iso", res.stdout)


if __name__ == "__main__":
    unittest.main()

