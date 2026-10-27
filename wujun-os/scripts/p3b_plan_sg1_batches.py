#!/usr/bin/env python3
"""P3b 补批：SG1 高信号单元（分诊 x_candidate=Y）装箱 3–5 万字/批。

SG1 裁决 A 后执行；不修改分诊 layer，仅生成批次工单与 B-P3b-SG1-*.md。
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from s10_batcher import chunks

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN_C, MAX_C = 30000, 50000


def main():
    path = os.path.join(ROOT, "ledger/分诊表.csv")
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    hi = [
        r
        for r in rows
        if r["book_code"] == "SG1" and r.get("x_candidate") == "Y"
    ]
    hi.sort(key=lambda r: r["unit_id"])
    units = [
        {
            "unit_id": r["unit_id"],
            "title": r["title"],
            "chars": int(r["chars"]),
            "x_sub": r.get("x_sub", ""),
            "layer": r["layer"],
            "is_series": bool(r.get("series_gid")),
        }
        for r in hi
    ]
    out_root = os.path.join(ROOT, "batches/P3b")
    os.makedirs(out_root, exist_ok=True)
    index = []
    for bi, (block, ch) in enumerate(chunks(units, MIN_C, MAX_C), 1):
        bid = f"B-P3b-SG1-{bi:03d}"
        fpath = os.path.join(out_root, f"{bid}.md")
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(f"# {bid}（P3b · SG1 · 高信号补批）\n\n")
            f.write(
                "- 来源：SG1 裁决 **A**；`ledger/T-SG1-P3b_工单.md`\n"
                f"- 汉字: {ch}\n- 单元: {len(block)}\n"
                "- 口径：分诊 `x_candidate=Y`（当前 layer 多为 C，抽 K 后走 P4 增量）\n\n"
            )
            f.write("| unit_id | 标题 | 汉字 | x_sub | layer |\n|---|---|---:|---|---|\n")
            for u in block:
                f.write(
                    f"| {u['unit_id']} | {u['title'][:48]} | {u['chars']} | "
                    f"{u['x_sub'] or '—'} | {u['layer']} |\n"
                )
        index.append((bid, ch, len(block)))
    idx_path = os.path.join(out_root, "INDEX_SG1_补批.md")
    with open(idx_path, "w", encoding="utf-8") as f:
        f.write("# P3b SG1 高信号补批索引\n\n")
        f.write(f"- 单元（x_candidate=Y）: **{len(units)}**\n")
        f.write(f"- 批次数: **{len(index)}**\n\n")
        f.write("| batch_id | 汉字 | 单元 |\n|---|---:|---:|\n")
        for bid, ch, n in index:
            f.write(f"| {bid} | {ch} | {n} |\n")
    print(f"SG1 P3b: {len(index)} 批 / {len(units)} 单元 -> {idx_path}")


if __name__ == "__main__":
    main()
