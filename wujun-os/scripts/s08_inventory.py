#!/usr/bin/env python3
"""s08_inventory.py — 生成 D5 单元清单草稿"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from wujun_units import build_catalog


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="src_frozen")
    ap.add_argument("--out", default="out/00_内容盘点与单元清单.md")
    args = ap.parse_args()
    cat = build_catalog(args.src)
    t = cat["totals"]
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("# 00 内容盘点与单元清单（P0 冻结分母）\n\n")
        f.write(f"- 总单元 **{t['total']}** = 内容 {t['content']} + 容器 {t['container']} + 非内容 {t['noncontent']}\n")
        f.write(f"- 内容单元汉字 **{t['content_chars']:,}**\n")
        f.write(f"- 全书汉字 **{t['file_chars']:,}**\n\n")
        f.write("| unit_id | 书码 | 书名 | 标题 | 行起 | 行止 | 汉字 | 类型 | 问答 | 系列 |\n")
        f.write("|---|---|---|---|---:|---:|---:|---|---|---|\n")
        for u in cat["units"]:
            f.write(
                f"| {u['unit_id']} | {u['book_code']} | {u['book']} | {u['title'][:40]} | "
                f"{u['line_start']} | {u['line_end']} | {u['chars']} | {u['cls']} | "
                f"{'Y' if u['is_qa'] else ''} | {'Y' if u['is_series'] else ''} |\n"
            )
    print(f"s08_inventory: {len(cat['units'])} 行 -> {args.out}")
    sys.exit(0)


if __name__ == "__main__":
    main()
