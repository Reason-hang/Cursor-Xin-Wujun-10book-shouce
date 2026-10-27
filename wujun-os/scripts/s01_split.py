#!/usr/bin/env python3
"""s01_split.py — 切分单元并落盘索引（S01）
用法: python3 scripts/s01_split.py --src src_frozen --out data/units_index.json
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from wujun_units import build_catalog


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="src_frozen")
    ap.add_argument("--out", default="data/units_index.json")
    args = ap.parse_args()
    cat = build_catalog(args.src)
    payload = {
        "src": args.src,
        "totals": cat["totals"],
        "units": cat["units"],
    }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    t = cat["totals"]
    print(
        f"s01_split: 单元 {t['total']} = 内容 {t['content']} + 容器 {t['container']} + 非内容 {t['noncontent']}；"
        f"内容汉字 {t['content_chars']:,}；-> {args.out}"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
