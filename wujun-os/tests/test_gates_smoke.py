#!/usr/bin/env python3
"""gates / validate_pillars 冒烟测试（不依赖 pillars.yaml 落库）。"""
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable


class GatesSmoke(unittest.TestCase):
    def test_validate_pillars_missing_exits_2(self):
        missing = os.path.join(ROOT, "spec", "_pillars_missing_smoke.yaml")
        self.assertFalse(os.path.exists(missing))
        proc = subprocess.run(
            [PY, "scripts/validate_pillars.py", "--path", missing],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("缺少", proc.stderr)

    def test_gate_scripts_compile(self):
        for rel in ("scripts/gates.py", "scripts/validate_pillars.py"):
            proc = subprocess.run([PY, "-m", "py_compile", rel], cwd=ROOT)
            self.assertEqual(proc.returncode, 0, rel)


if __name__ == "__main__":
    unittest.main()
