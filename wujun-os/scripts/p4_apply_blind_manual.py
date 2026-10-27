#!/usr/bin/env python3
"""将 data/p4_blind_manual.json 合并进 P4_盲重标样本.csv 的 primary_blind_manual 列"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "ledger/P4_盲重标样本.csv"
MANUAL = ROOT / "data/p4_blind_manual.json"


def main():
    overrides = json.loads(MANUAL.read_text(encoding="utf-8")).get("overrides", {})
    rows = list(csv.DictReader(SAMPLE.open(encoding="utf-8")))
    for r in rows:
        cid = r["card_id"]
        r["primary_blind_manual"] = overrides.get(cid, r["primary_original"])
        r["agree_manual"] = "Y" if r["primary_blind_manual"] == r["primary_original"] else "N"
    fields = list(rows[0].keys())
    with SAMPLE.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    n = sum(1 for r in rows if r["agree_manual"] == "Y")
    print(f"applied manual: {len(rows)} cards, agree with original {n}/{len(rows)}")


if __name__ == "__main__":
    main()
