#!/usr/bin/env python3
"""s05_dups.py — G6 重复段落扫描"""
import argparse
import collections
import itertools
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from wujun_units import build_catalog, cjk

CJK = re.compile(r"[\u4e00-\u9fff]")


def paras(text):
    out = []
    for l in text.split("\n"):
        s = l.strip()
        if cjk(s) >= 40 and not re.match(r"^([-*]\s*\[|!\[|>|#)", s):
            out.append(s)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="src_frozen")
    ap.add_argument("--out", default="logs/g6.md")
    ap.add_argument("--baseline", default="spec/baseline_facts.json")
    args = ap.parse_args()
    cat = build_catalog(args.src)
    P = {c: paras(cat["books"][c]["text"]) for c in cat["books"]}
    inbook = {c: sum(1 for v in collections.Counter(p).values() if v > 1) for c, p in P.items()}
    pairs, tp, tc = {}, 0, 0
    for a, b in itertools.combinations(sorted(P), 2):
        inter = set(P[a]) & set(P[b])
        if inter:
            pairs[f"{a}<->{b}"] = {"paragraphs": len(inter), "chars": sum(cjk(x) for x in inter)}
            tp += len(inter)
            tc += sum(cjk(x) for x in inter)
    import json

    base = json.load(open(args.baseline, encoding="utf-8")).get("probe", {})
    bad = []
    if base.get("dup_cross", {}).get("paragraphs") != tp:
        bad.append(("dup_cross.paragraphs", base.get("dup_cross", {}).get("paragraphs"), tp))
    if base.get("dup_cross", {}).get("chars") != tc:
        bad.append(("dup_cross.chars", base.get("dup_cross", {}).get("chars"), tc))
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("# G6 重复扫描\n\n")
        f.write(f"- 跨书段落 {tp}，汉字 {tc}\n\n")
        for k, v in sorted(pairs.items()):
            f.write(f"- {k}: {v['paragraphs']} 段 / {v['chars']} 字\n")
        f.write("\n## 书内重复簇数\n\n")
        for c, n in sorted(inbook.items()):
            if n:
                f.write(f"- {c}: {n}\n")
        if bad:
            f.write("\n## 与基线不一致\n\n" + "\n".join(f"- {a}: 基线 {x} 本次 {y}" for a, x, y in bad))
    print(f"s05_dups: 跨书 {tp} 段；基线不一致 {len(bad)}；{args.out}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
