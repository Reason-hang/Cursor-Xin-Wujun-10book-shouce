#!/usr/bin/env python3
"""AC-6.2 预检：分诊表单元数 vs P0 内容单元（s09）。"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def count_unit_cards() -> int:
    n = 0
    for p in Path(ROOT / "cards").rglob("*.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        n += len(d.get("cards", []))
    return n


def main() -> int:
    triage = list(csv.DictReader((ROOT / "ledger/分诊表.csv").open(encoding="utf-8")))
    cards_n = count_unit_cards()
    tri_n = len(triage)
    # P0 口径：分诊覆盖所有内容单元；卡片为已抽 K 子集
    if tri_n < 1690:
        print(f"FAIL: 分诊 {tri_n} 行，低于预期 ~1697")
        return 1
    print(f"p6 unit coverage: 分诊 {tri_n} 单元；论点卡 {cards_n} 张（K 冻结 493）")
    print("说明：100% 核心论点覆盖需双向矩阵（AC-6.2 全量），本脚本仅数量预检。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
