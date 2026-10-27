#!/usr/bin/env python3
"""s06_flags.py — G7 非原著/风险行标注统计"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from wujun_units import build_catalog

PATTERNS = {
    "image_link": re.compile(r"!\[.*?\]\(.*?\)"),
    "html_anchor": re.compile(r"<a\s|</a>|id=\"|</br>|<img"),
    "promo": re.compile(r"订阅|扫码|关注|新书|招募|投票"),
    "instruction": re.compile(r"请你|欢迎留言|作业|打卡"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="src_frozen")
    ap.add_argument("--out", default="logs/g7.md")
    args = ap.parse_args()
    cat = build_catalog(args.src)
    counts = {k: 0 for k in PATTERNS}
    per_book = {c: {k: 0 for k in PATTERNS} for c in cat["books"]}
    for code, book in cat["books"].items():
        for i, line in enumerate(book["lines"], 1):
            for name, pat in PATTERNS.items():
                if pat.search(line):
                    counts[name] += 1
                    per_book[code][name] += 1
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("# G7 标记统计\n\n")
        f.write("| 类型 | 行数 |\n|---|---|\n")
        for k, v in counts.items():
            f.write(f"| {k} | {v} |\n")
        f.write("\n## 分书\n\n")
        for code, row in sorted(per_book.items()):
            f.write(f"- {code}: {row}\n")
    print(f"s06_flags: 已统计 G7 标记 -> {args.out}")
    sys.exit(0)


if __name__ == "__main__":
    main()
