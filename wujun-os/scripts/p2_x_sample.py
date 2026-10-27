#!/usr/bin/env python3
"""p2_x_sample.py — 抽取 X 候选回读样本（T-P2-08 准备，≥30）"""
import csv
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    path = os.path.join(ROOT, "ledger/分诊表.csv")
    rows = [r for r in csv.DictReader(open(path, encoding="utf-8")) if r["x_candidate"] == "Y"]
    random.seed(42)
    n = min(30, len(rows))
    pick = random.sample(rows, n)
    out = os.path.join(ROOT, "ledger/P2_X候选抽样30.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("# P2 X 候选抽样（待回读）\n\n")
        f.write(f"- 池大小: {len(rows)}；本批抽取: **{n}**\n\n")
        f.write("| # | unit_id | x_sub | title | 回读结论 |\n")
        f.write("|---:|---|---|---|---|\n")
        for i, r in enumerate(pick, 1):
            f.write(f"| {i} | {r['unit_id']} | {r['x_sub']} | {r['title'][:40]} | 待填 |\n")
    print(f"已写入 {out}（{n} 条）")


if __name__ == "__main__":
    main()
