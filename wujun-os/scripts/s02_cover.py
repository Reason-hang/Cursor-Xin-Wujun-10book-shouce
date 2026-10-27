#!/usr/bin/env python3
"""s02_cover.py — G2 行覆盖 / G3 汉字守恒"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from wujun_units import build_catalog, cjk


def check_cover(cat: dict) -> tuple[int, list[str]]:
    issues = []
    for code, book in cat["books"].items():
        lines = book["lines"]
        n = len(lines)
        owner = [None] * n
        for u in [x for x in cat["units"] if x["book_code"] == code]:
            for li in range(u["line_start"] - 1, u["line_end"]):
                if li < 0 or li >= n:
                    issues.append(f"{code} {u['unit_id']} 行越界 {li+1}")
                    continue
                if owner[li] is not None and owner[li] != u["unit_id"]:
                    issues.append(f"{code} 行 {li+1} 重叠 {owner[li]} vs {u['unit_id']}")
                owner[li] = u["unit_id"]
        for i, line in enumerate(lines):
            if line.strip() and owner[i] is None:
                issues.append(f"{code} 行 {i+1} 未归属单元（非空）")
    unit_cjk = sum(u["chars"] for u in cat["units"])
    file_cjk = cat["totals"]["file_chars"]
    # 单元 chars 不含各单元标题行汉字；差值 = 标题行 + 首个标题前前言（v2 G3 前置 26,936）
    structural_cjk = file_cjk - unit_cjk
    expected_structural = 26936
    if structural_cjk != expected_structural:
        issues.append(
            f"G3 汉字不守恒：文件 {file_cjk} != 单元正文 {unit_cjk} + 结构区 {structural_cjk}（期望结构区 {expected_structural}）"
        )
    return len(issues), issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="src_frozen")
    ap.add_argument("--out", default="logs/g2g3.md")
    ap.add_argument("--baseline-diff", type=int, default=0, help="期望 G3 差值（基线 0）")
    args = ap.parse_args()
    cat = build_catalog(args.src)
    n_bad, issues = check_cover(cat)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("# G2/G3 行覆盖与汉字守恒\n\n")
        f.write(f"- 单元汉字合计（正文行，不含标题行内重复计）: {sum(u['chars'] for u in cat['units']):,}\n")
        f.write(f"- 全书汉字: {cat['totals']['file_chars']:,}\n")
        f.write(f"- 问题数: {n_bad}\n\n")
        if issues:
            f.write("## 问题\n\n" + "\n".join(f"- {x}" for x in issues[:200]) + "\n")
    print(f"s02_cover: G2/G3 问题 {n_bad}；日志 {args.out}")
    if issues[:5]:
        for x in issues[:5]:
            print(" ", x)
    sys.exit(1 if n_bad else 0)


if __name__ == "__main__":
    main()
