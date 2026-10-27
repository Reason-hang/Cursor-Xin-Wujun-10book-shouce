#!/usr/bin/env python3
"""s03_numbering.py — G4 编号连续"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from wujun_units import build_catalog


def numbering(units, pat):
    nums = []
    for u in units:
        m = re.search(pat, u["title"])
        if m:
            nums.append(int(m.groups()[-1]))
    cnt = collections.Counter(nums)
    mx = max(nums) if nums else 0
    return {
        "count": len(nums),
        "max": mx,
        "missing": sorted(set(range(1, mx + 1)) - set(nums)),
        "dup": sorted(k for k, v in cnt.items() if v > 1),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="src_frozen")
    ap.add_argument("--out", default="logs/g4.md")
    args = ap.parse_args()
    cat = build_catalog(args.src)
    pb = {}
    for code in ("SG1", "WJ2", "SG3", "GG"):
        us = [u for u in cat["units"] if u["book_code"] == code]
        pb[f"{code}_letters"] = numbering(us, r"第\s*0*(\d+)\s*封信")
    pb["WJ2_weekend_qa"] = numbering(
        [u for u in cat["units"] if u["book_code"] == "WJ2"], r"周末问答\s*0*(\d+)"
    )
    pb["SG3_qa"] = numbering(
        [u for u in cat["units"] if u["book_code"] == "SG3"], r"答读者问\s*0*(\d+)"
    )
    pb["GG_qa"] = numbering(
        [u for u in cat["units"] if u["book_code"] == "GG"], r"答读者问\s*0*(\d+)"
    )
    issues = []
    for k, v in pb.items():
        if v["dup"]:
            issues.append(f"{k} 重号 {v['dup']}")
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("# G4 编号\n\n")
        for k, v in pb.items():
            f.write(f"## {k}\n\n- 计数 {v['count']} max {v['max']}\n- 缺号 {v['missing']}\n- 重号 {v['dup']}\n\n")
    print(f"s03_numbering: 重号问题 {len([i for i in issues])}；缺号已记入 {args.out}")
    sys.exit(1 if any(v["dup"] for v in pb.values()) else 0)


if __name__ == "__main__":
    main()
