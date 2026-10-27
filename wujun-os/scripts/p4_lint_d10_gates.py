#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "ledger/P4_D10三道门裁决.csv"
MD = ROOT / "ledger/P4_D10三道门裁决.md"


def main():
    if not CSV.is_file() or not MD.is_file():
        print("缺少三道门裁决文件")
        return 1
    rows = list(csv.DictReader(CSV.open(encoding="utf-8")))
    if len(rows) != 3:
        print(f"期望 3 道门，实际 {len(rows)}")
        return 1
    if not rows[0].get("overall"):
        print("缺 overall 裁决")
        return 1
    print(f"D10 gates lint OK: overall={rows[0]['overall']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
