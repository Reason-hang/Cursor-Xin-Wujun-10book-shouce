#!/usr/bin/env python3
"""L3 聚合 lint：每张 draft K 恰映射一 L3；每 L2≤4 L3"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSIGN = ROOT / "ledger/P4_归属表.csv"
MAP = ROOT / "ledger/P4_卡到L3映射.csv"
L3 = ROOT / "ledger/P4_L3模型清单.csv"
L2 = ROOT / "ledger/P4_L2清单.csv"


def main():
    draft = [r["card_id"] for r in csv.DictReader(ASSIGN.open(encoding="utf-8")) if r["status"] == "draft"]
    mapping = list(csv.DictReader(MAP.open(encoding="utf-8")))
    mapped = {r["card_id"]: r["l3_id"] for r in mapping}
    errs = []
    for c in draft:
        if c not in mapped:
            errs.append(f"未映射 L3: {c}")
    if len(mapped) != len(set(mapped.keys())):
        errs.append("映射卡 ID 重复")
    l2_counts = {}
    for r in csv.DictReader(L2.open(encoding="utf-8")):
        if int(r["l3_count"]) > 4:
            errs.append(f"L2 超 4 L3: {r['l2_code']}")
    l3n = sum(1 for _ in csv.DictReader(L3.open(encoding="utf-8")))
    if l3n > 50:
        errs.append(f"L3 数 {l3n} 超红线 50（预警）")
    if errs:
        for e in errs[:15]:
            print("FAIL:", e)
        return 1
    print(f"P4 L3 lint OK: {l3n} L3, {len(draft)} K mapped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
