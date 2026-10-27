#!/usr/bin/env python3
"""P4 关系表 lint：每对必有关系类型；冲突 open 须有 pair 引用"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REL = ROOT / "ledger/P4_卡对关系表.csv"
CON = ROOT / "ledger/P4_冲突台账.csv"
ALLOWED = {
    "同义重复",
    "同一机制、不同应用",
    "层次递进",
    "条件不同",
    "时间变化",
    "实质冲突",
    "独有论点",
    "指纹误配",
}


def main():
    if not REL.is_file():
        print("缺少 P4_卡对关系表.csv")
        return 1
    rows = list(csv.DictReader(REL.open(encoding="utf-8")))
    errs = []
    for r in rows:
        if r["relation_type"] not in ALLOWED:
            errs.append(f"非法关系: {r['pair_id']} {r['relation_type']}")
        if not r.get("review_status"):
            errs.append(f"缺 review_status: {r['pair_id']}")
    if CON.is_file():
        pairs = {r["pair_id"] for r in rows}
        for c in csv.DictReader(CON.open(encoding="utf-8")):
            if c["pair_id"] not in pairs:
                errs.append(f"冲突引用未知 pair: {c['conflict_id']}")
            if c["status"] == "open" and not c.get("note"):
                errs.append(f"冲突缺 note: {c['conflict_id']}")
    if errs:
        for e in errs[:15]:
            print("FAIL:", e)
        return 1
    print(f"P4 relations lint OK: {len(rows)} 对")
    return 0


if __name__ == "__main__":
    sys.exit(main())
