#!/usr/bin/env python3
"""AC-6.3：抽检召回样本状态 lint（全 pass 才达标）。"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "ledger/P6_抽检召回样本.csv"


def main() -> int:
    if not SAMPLE.is_file():
        print("FAIL: 缺少抽检样本 CSV")
        return 1
    rows = list(csv.DictReader(SAMPLE.open(encoding="utf-8")))
    pending = sum(1 for r in rows if r.get("recall_status", "pending") == "pending")
    fail = sum(1 for r in rows if r.get("recall_status") == "fail")
    pass_n = sum(1 for r in rows if r.get("recall_status") == "pass")
    print(f"p6 recall lint: total={len(rows)} pass={pass_n} fail={fail} pending={pending}")
    if pending:
        print("AC-6.3 未闭环：仍有 pending（见 P6_抽检召回工作册.md）")
        return 0  # 预检不阻断 gates；P7 前改为 return 1
    if fail:
        print("AC-6.3：存在 fail，需补写后重跑")
        return 1
    print("AC-6.3 recall: 样本 100% pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
