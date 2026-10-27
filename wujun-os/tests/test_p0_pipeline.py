#!/usr/bin/env python3
"""P0 口径：build_catalog（src_frozen）与 pillars 校验（无 mock）。"""
from __future__ import annotations

import glob
import importlib.util
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
SRC_FROZEN = os.path.join(ROOT, "src_frozen")
PY = sys.executable

if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)


def _src_frozen_exists() -> bool:
    return os.path.isdir(SRC_FROZEN)


def _src_frozen_book_count() -> int:
    return len(glob.glob(os.path.join(SRC_FROZEN, "*.md")))


def _venv_has_pyyaml() -> bool:
    return importlib.util.find_spec("yaml") is not None


class P0Pipeline(unittest.TestCase):
    @unittest.skipUnless(_src_frozen_exists(), "缺少 src_frozen/")
    def test_build_catalog_on_src_frozen(self):
        from wujun_units import build_catalog

        if _src_frozen_book_count() != 10:
            self.skipTest("src_frozen 不是 10 本原文，跳过 build_catalog 总数断言")

        cat = build_catalog(SRC_FROZEN)
        self.assertEqual(cat["totals"]["total"], 1742)

    @unittest.skipUnless(_venv_has_pyyaml(), "venv 未安装 PyYAML")
    def test_validate_pillars(self):
        proc = subprocess.run(
            [PY, "scripts/validate_pillars.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        combined = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 0, combined)
        self.assertIn("validate_pillars: 通过", proc.stdout)


if __name__ == "__main__":
    unittest.main()
