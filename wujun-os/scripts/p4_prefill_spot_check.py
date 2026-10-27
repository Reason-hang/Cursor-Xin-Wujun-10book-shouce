#!/usr/bin/env python3
"""Agent 预填抽查 20 张（claim 级快检，用户可改）"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "ledger/P4_抽查20张.csv"


def main():
    rows = list(csv.DictReader(PATH.open(encoding="utf-8")))
    for r in rows:
        if not (r.get("归属明显错误") or "").strip():
            r["归属明显错误"] = "N"
        if not (r.get("转述失真") or "").strip():
            r["转述失真"] = "N"
        r["reviewer"] = "Agent预填-待用户确认"
        r["note"] = "仅读 claim 快检；未对锚点段逐字核对"
    with PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    err = sum(1 for r in rows if r["归属明显错误"] == "Y")
    print(f"prefill spot-check: 归属错误 Y={err}/20")


if __name__ == "__main__":
    main()
