#!/usr/bin/env python3
"""s13_kwscan.py — 概念关键词反查（S13 / G10）

用法: python3 scripts/s13_kwscan.py --src src_frozen --watchlist data/concept_watchlist.csv --out logs/g10_kw.md
"""
import argparse
import csv
import os
import re
import sys
from collections import defaultdict


def load_watchlist(path):
    concepts = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            concepts.append(
                (
                    row["concept"].strip(),
                    row.get("pillar_hint", ""),
                    row.get("note", ""),
                )
            )
    return concepts


def scan_file(path, concepts):
    text = open(path, encoding="utf-8").read()
    hits = []
    for word, hint, note in concepts:
        if not word or word not in text:
            continue
        for m in re.finditer(word, text):
            pos = m.start()
            line = text.count("\n", 0, pos) + 1
            ctx_s = max(0, pos - 20)
            ctx_e = min(len(text), pos + len(word) + 30)
            ctx = text[ctx_s:ctx_e].replace("\n", " ")
            hits.append((word, hint, note, line, ctx))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="src_frozen")
    ap.add_argument("--watchlist", default="data/concept_watchlist.csv")
    ap.add_argument("--out", default="logs/g10_kw.md")
    args = ap.parse_args()
    concepts = load_watchlist(args.watchlist)
    all_hits = []
    for name in sorted(os.listdir(args.src)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(args.src, name)
        for h in scan_file(path, concepts):
            all_hits.append((name,) + h)

    by_group = defaultdict(list)
    for book, word, hint, note, line, ctx in all_hits:
        grp = note if note.startswith("回归组") else note or "其他"
        by_group[grp].append((book, word, hint, line, ctx))

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("# G10 关键词反查（S13）\n\n")
        f.write(f"- 词表: `{args.watchlist}`\n")
        f.write(f"- 源: `{args.src}/`\n")
        f.write(f"- 命中段落数: **{len(all_hits)}**\n\n")
        for grp in sorted(by_group):
            f.write(f"## {grp}\n\n")
            f.write("| 书 | 词 | 支柱提示 | 行 | 上下文摘要 | 去向 |\n")
            f.write("|---|---|---|---|---|---|\n")
            for book, word, hint, line, ctx in sorted(by_group[grp], key=lambda x: (x[0], x[3])):
                dest = "待 P1 回归判定·试点卡或台账登记"
                if "试点" in grp or word in ("伪工作", "沟通", "划重点"):
                    dest = "已纳入 P1 选样或 SG3 召回样本"
                f.write(f"| {book} | {word} | {hint} | {line} | {ctx[:60]}… | {dest} |\n")
            f.write("\n")
    print(f"已写入 {args.out}；命中 {len(all_hits)} 处")
    sys.exit(0)


if __name__ == "__main__":
    main()
