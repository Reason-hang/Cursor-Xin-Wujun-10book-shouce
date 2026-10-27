#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ledger/P4_数量核对表.csv"


def main():
    if not OUT.is_file():
        print("缺少数量核对表")
        return 1
    rows = list(csv.DictReader(OUT.open(encoding="utf-8")))
    red = [r for r in rows if r["status"] == "red"]
    if red:
        for r in red:
            print(f"FAIL 红线: {r['metric']}={r['count']}>{r['red_line']}")
        return 1
    print(f"P4 count lint OK: {len(rows)} 项，无红线")
    return 0


if __name__ == "__main__":
    sys.exit(main())
