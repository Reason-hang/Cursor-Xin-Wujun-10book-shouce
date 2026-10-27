#!/usr/bin/env python3
"""s04_toc.py — G5 目录对账（弱证据 + 谷歌作者目录）"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from wujun_units import build_catalog


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="src_frozen")
    ap.add_argument("--out", default="logs/g5.md")
    args = ap.parse_args()
    cat = build_catalog(args.src)
    cat_text = ""
    for u in cat["per_book_units"]["GG"]:
        if u["title"].startswith("收藏丨全年课程目录"):
            cat_text = u["text"]
            break
    covered = sorted({int(x) for x in re.findall(r"第\s*0*(\d{1,3})\s*封信", cat_text)}) if cat_text else []
    missing = sorted(set(range(1, 224)) - set(covered))
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("# G5 目录对账\n\n")
        f.write(f"## 谷歌作者目录（G5b）\n\n- 覆盖 {len(covered)}/223\n- 缺号 {missing}\n\n")
        f.write("## G5a 自动目录\n\n- 弱证据：6 本自动目录与标题一致性由前置探测记录；差集在 P0 台账定性。\n")
    print(f"s04_toc: 作者目录覆盖 {len(covered)}/223；缺 {missing}；{args.out}")
    sys.exit(0)


if __name__ == "__main__":
    main()
