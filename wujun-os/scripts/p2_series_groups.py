#!/usr/bin/env python3
"""汇总系列组（AC-2.3）"""
import csv
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    path = os.path.join(ROOT, "ledger/分诊表.csv")
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    groups = defaultdict(list)
    for r in rows:
        if r["series_gid"]:
            groups[r["series_gid"]].append(r["unit_id"])
    out = os.path.join(ROOT, "ledger/P2_系列组表.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("# P2 系列组表\n\n")
        f.write(f"- 组数: **{len(groups)}**\n")
        f.write(f"- 系列单元数: **{sum(len(v) for v in groups.values())}**\n\n")
        f.write("| series_gid | 单元数 | unit_ids |\n|---|---:|---|\n")
        for gid, uids in sorted(groups.items(), key=lambda x: -len(x[1])):
            f.write(f"| {gid} | {len(uids)} | {', '.join(uids[:4])}{'…' if len(uids)>4 else ''} |\n")
    print(f"系列组 {len(groups)} -> {out}")


if __name__ == "__main__":
    main()
