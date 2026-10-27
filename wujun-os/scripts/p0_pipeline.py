#!/usr/bin/env python3
"""p0_pipeline.py — 串行跑 P0 闸门 S01–S08"""
import subprocess
import sys

PY = sys.executable
STEPS = [
    ([PY, "scripts/s01_split.py"], "S01 split"),
    ([PY, "scripts/s02_cover.py"], "S02 G2/G3"),
    ([PY, "scripts/s03_numbering.py"], "S03 G4"),
    ([PY, "scripts/s04_toc.py"], "S04 G5"),
    ([PY, "scripts/s05_dups.py"], "S05 G6"),
    ([PY, "scripts/s06_flags.py"], "S06 G7"),
    ([PY, "scripts/s07_sample.py"], "S07 G8"),
    ([PY, "scripts/s08_inventory.py"], "S08 D5"),
]


def main():
    for cmd, name in STEPS:
        r = subprocess.run(cmd)
        if r.returncode != 0:
            print(f"p0_pipeline: 失败 {name} (exit {r.returncode})")
            sys.exit(r.returncode)
        print(f"p0_pipeline: OK {name}")
    print("p0_pipeline: 全部通过")
    sys.exit(0)


if __name__ == "__main__":
    main()
