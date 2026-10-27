#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L2 = ROOT / "ledger/P4_L2定稿.csv"
THIN = ROOT / "ledger/P4_薄簇处置.csv"


def main():
    rows = list(csv.DictReader(L2.open(encoding="utf-8")))
    thin_codes = {r["l2_code"] for r in rows if r["status"] == "thin_downgrade"}
    listed = {r["l2_code"] for r in csv.DictReader(THIN.open(encoding="utf-8"))} if THIN.is_file() else set()
    errs = []
    if thin_codes != listed:
        errs.append(f"薄簇表与定稿不一致: 定稿{thin_codes} 表{listed}")
    active = sum(1 for r in rows if r["status"] == "active")
    if active < 15 or active > 32:
        errs.append(f"active L2={active} 偏离目标区间 22-28（预警）")
    if errs:
        for e in errs:
            print("FAIL:", e)
        return 1
    print(f"P4 L2 final lint OK: active={active} thin={len(thin_codes)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
