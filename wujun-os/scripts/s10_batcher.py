#!/usr/bin/env python3
"""s10_batcher.py — 按汉字装箱批次（3–5 万/批，系列不拆）

用法:
  python3 scripts/s10_batcher.py --src src_frozen --min-chars 30000 --max-chars 50000 --out batches/B-P2

未分诊阶段：仅按书序+字数装箱，读法层待 P2 人工标注后重跑可加 --triage。
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from wujun_units import build_catalog, BOOK_ORDER


def series_key(title: str) -> str:
    t = re.sub(r"[（(][上下中一二三四五][）)]", "", title)
    return t.strip()


def chunks(units, min_c, max_c):
    """units: list of dict with unit_id, chars, title, is_series"""
    batches = []
    cur, cur_chars = [], 0
    i = 0
    while i < len(units):
        u = units[i]
        block = [u]
        block_chars = u["chars"]
        if u["is_series"]:
            sk = series_key(u["title"])
            j = i + 1
            while j < len(units) and units[j]["is_series"] and series_key(units[j]["title"]) == sk:
                block.append(units[j])
                block_chars += units[j]["chars"]
                j += 1
            i = j
        else:
            i += 1

        if cur and cur_chars + block_chars > max_c and cur_chars >= min_c:
            batches.append((cur, cur_chars))
            cur, cur_chars = [], 0
        cur.extend(block)
        cur_chars += block_chars
        if cur_chars >= max_c:
            batches.append((cur, cur_chars))
            cur, cur_chars = [], 0
    if cur:
        batches.append((cur, cur_chars))
    return batches


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="src_frozen")
    ap.add_argument("--min-chars", type=int, default=30000)
    ap.add_argument("--max-chars", type=int, default=50000)
    ap.add_argument("--out", default="batches/B-P2")
    args = ap.parse_args()
    cat = build_catalog(args.src)
    units = [u for u in cat["units"] if u["cls"] == "C"]
    os.makedirs(args.out, exist_ok=True)
    all_batches = []
    for code in BOOK_ORDER:
        book_units = [u for u in units if u["book_code"] == code]
        if not book_units:
            continue
        for bi, (block, ch) in enumerate(chunks(book_units, args.min_chars, args.max_chars), 1):
            bid = f"B-P2-{code}-{bi:03d}"
            path = os.path.join(args.out, f"{bid}.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"# 批次 {bid}\n\n")
                f.write(f"- 书码: {code}\n")
                f.write(f"- 汉字: {ch}\n")
                f.write(f"- 单元数: {len(block)}\n\n")
                f.write("| unit_id | 标题 | 汉字 |\n|---|---|---:|\n")
                for u in block:
                    f.write(f"| {u['unit_id']} | {u['title'][:50]} | {u['chars']} |\n")
            all_batches.append((bid, code, ch, len(block)))

    idx = os.path.join(args.out, "INDEX.md")
    with open(idx, "w", encoding="utf-8") as f:
        f.write("# P2 批次索引（S10 初装箱）\n\n")
        f.write(f"- 批次数: **{len(all_batches)}**\n")
        f.write(f"- 字数窗: {args.min_chars}–{args.max_chars}\n\n")
        f.write("| batch_id | 书码 | 汉字 | 单元数 |\n|---|---|---:|---:|\n")
        for bid, code, ch, n in all_batches:
            f.write(f"| {bid} | {code} | {ch} | {n} |\n")
    print(f"s10: {len(all_batches)} 批 -> {args.out}/INDEX.md")
    sys.exit(0)


if __name__ == "__main__":
    main()
