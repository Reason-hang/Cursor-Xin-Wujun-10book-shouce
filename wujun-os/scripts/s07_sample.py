#!/usr/bin/env python3
"""s07_sample.py — G8 反向抽查（固定种子）"""
import argparse
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from wujun_units import build_catalog, cjk


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="src_frozen")
    ap.add_argument("--out", default="logs/g8.md")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--positions", type=int, default=100)
    ap.add_argument("--units", type=int, default=60)
    args = ap.parse_args()
    cat = build_catalog(args.src)
    rng = random.Random(args.seed)
    issues = []
    # 随机字符位置 -> 应落在某书某单元
    for code, book in cat["books"].items():
        text = book["text"]
        if not text:
            continue
        n = min(args.positions // 10, max(1, len(text) // 5000))
        for _ in range(n):
            pos = rng.randint(0, max(0, len(text) - 1))
            line = text.count("\n", 0, pos) + 1
            hit = [u for u in cat["units"] if u["book_code"] == code and u["line_start"] <= line <= u["line_end"]]
            if not hit:
                issues.append(f"{code} 行 {line} 未命中单元（位置抽查）")
    sample_units = rng.sample(cat["units"], min(args.units, len(cat["units"])))
    for u in sample_units:
        book = cat["books"][u["book_code"]]
        lines = book["lines"]
        s, e = u["line_start"] - 1, u["line_end"]
        recount = sum(cjk(lines[li]) for li in range(s + 1, e))
        if recount != u["chars"]:
            issues.append(f"{u['unit_id']} 字数不一致：索引 {u['chars']} 复算 {recount}")
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("# G8 反向抽查\n\n")
        f.write(f"- 种子 {args.seed}\n- 问题 {len(issues)}\n\n")
        if issues:
            f.write("## 差异\n\n" + "\n".join(f"- {x}" for x in issues[:100]) + "\n")
    print(f"s07_sample: 问题 {len(issues)}；{args.out}")
    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
