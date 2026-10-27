#!/usr/bin/env python3
"""用户书面确认 P4 抽查 20 张（不改 Y/N，仅改 reviewer 标记）。用法：写入 ledger/P4_抽查_用户确认.txt 任意非空一行后运行。"""
import csv
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLAG = ROOT / "ledger/P4_抽查_用户确认.txt"
CSV = ROOT / "ledger/P4_抽查20张.csv"


def main() -> int:
    if not FLAG.is_file() or not FLAG.read_text(encoding="utf-8").strip():
        print("skip: 创建 ledger/P4_抽查_用户确认.txt 并写一行说明后重跑")
        return 0
    if not CSV.is_file():
        print("FAIL: 缺少 P4_抽查20张.csv")
        return 1
    rows = list(csv.DictReader(CSV.open(encoding="utf-8")))
    note = f"用户确认 {date.today().isoformat()}"
    for r in rows:
        r["reviewer"] = note
        if "待用户" in (r.get("note") or ""):
            r["note"] = (r.get("note") or "").replace("待用户确认", "用户已确认抽查")
    with CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"p4 spot check: {len(rows)} 行 reviewer 已更新")
    return 0


if __name__ == "__main__":
    sys.exit(main())
