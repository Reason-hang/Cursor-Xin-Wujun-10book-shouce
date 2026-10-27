#!/usr/bin/env python3
"""gates.py — 阶段闸门骨架（EP-0 / make gates）

依次调用：verify_pack → selftest → status。
任一子步骤非零退出码则本脚本返回 1。

用法（在仓库根目录 wujun-os/ 执行）:
  python3 scripts/gates.py
"""
from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable

STEPS: tuple[tuple[str, list[str]], ...] = (
    ("verify_pack", ["scripts/verify_pack.py"]),
    ("selftest", ["scripts/selftest.py"]),
    ("p6_dup_lint", ["scripts/p6_dup_lint.py"]),
    ("p6_unit_coverage", ["scripts/p6_unit_coverage.py"]),
    ("p6_bidir_matrix", ["scripts/p6_bidir_matrix.py"]),
    ("status", ["scripts/status.py"]),
)


def run_step(name: str, args: list[str]) -> int:
    print(f"[gates] {name} …", flush=True)
    proc = subprocess.run([PY] + args, cwd=ROOT)
    if proc.returncode != 0:
        print(f"[gates] {name} 失败（退出码 {proc.returncode}）", flush=True)
    else:
        print(f"[gates] {name} 通过", flush=True)
    return proc.returncode


def main() -> int:
    failed: list[str] = []
    for name, args in STEPS:
        if run_step(name, args) != 0:
            failed.append(name)
    if failed:
        print(f"[gates] 未通过：{', '.join(failed)}", flush=True)
        return 1
    print("[gates] 全部通过：verify_pack、selftest、status", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
