#!/usr/bin/env python3
"""p3b_plan_batches.py — P3b 四书来信 B 层装箱（3–5 万字/批）

书序（v2.1）：GG → WJ2 → SG3（SG1 无 B 层单元）
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from s10_batcher import chunks

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P3B_ORDER = ["GG", "WJ2", "SG3"]
MIN_C, MAX_C = 30000, 50000


def main():
    rows = list(csv.DictReader(open(os.path.join(ROOT, "ledger/分诊表.csv"), encoding="utf-8")))
    b_rows = [r for r in rows if r["layer"] == "B" and r["book_code"] in P3B_ORDER]
    out_root = os.path.join(ROOT, "batches/P3b")
    os.makedirs(out_root, exist_ok=True)
    index = []
    for code in P3B_ORDER:
        book = [r for r in b_rows if r["book_code"] == code]
        units = [
            {
                "unit_id": r["unit_id"],
                "title": r["title"],
                "chars": int(r["chars"]),
                "is_series": bool(r.get("series_gid")),
            }
            for r in book
        ]
        for bi, (block, ch) in enumerate(chunks(units, MIN_C, MAX_C), 1):
            bid = f"B-P3b-{code}-{bi:03d}"
            path = os.path.join(out_root, f"{bid}.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"# {bid}（P3b · {code} · B 层）\n\n")
                f.write(f"- 汉字: {ch}\n- 单元: {len(block)}\n\n")
                f.write("| unit_id | 标题 | 汉字 |\n|---|---|---:|\n")
                for u in block:
                    f.write(f"| {u['unit_id']} | {u['title'][:50]} | {u['chars']} |\n")
            index.append((bid, code, ch, len(block)))
    idx_path = os.path.join(out_root, "INDEX.md")
    with open(idx_path, "w", encoding="utf-8") as f:
        f.write("# P3b 批次索引（谷歌 · 来信2 · 来信3 · B 层）\n\n")
        f.write(f"- 书序: {' → '.join(P3B_ORDER)}\n")
        f.write(f"- B 层单元合计: {len(b_rows)}\n")
        f.write(f"- 批次数: **{len(index)}**\n\n")
        f.write("| batch_id | 书码 | 汉字 | 单元 |\n|---|---|---:|---:|\n")
        for bid, code, ch, n in index:
            f.write(f"| {bid} | {code} | {ch} | {n} |\n")
    print(f"P3b: {len(index)} 批 -> {idx_path}")


if __name__ == "__main__":
    main()
