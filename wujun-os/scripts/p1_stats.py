#!/usr/bin/env python3
"""p1_stats.py — 试点能力标签可标注率、归属歧义率（T-P1-08）"""
import argparse
import json
import os
import sys

CAP = {"思", "做", "沟", "判"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", default="ledger/P1_选样表.json")
    ap.add_argument("--cards-dir", default="cards")
    ap.add_argument("--out", default="ledger/P1_试点统计.md")
    args = ap.parse_args()
    units = json.load(open(args.units, encoding="utf-8"))["units"]
    cards_n = 0
    tagged = 0
    ambiguous = 0
    multi_pillar = 0
    rows = []
    for uid in units:
        code = uid.split("-")[0]
        path = os.path.join(args.cards_dir, code, f"{uid}.json")
        if not os.path.isfile(path):
            continue
        data = json.load(open(path, encoding="utf-8"))
        for c in data.get("cards", []):
            if c.get("disposition") == "X3":
                continue
            cards_n += 1
            tags = set(c.get("capability_tags") or [])
            if tags and tags <= CAP:
                tagged += 1
            elif not tags and c.get("type") in ("—",):
                tagged += 1
            hints = c.get("pillar_hints") or []
            if len(hints) >= 2:
                multi_pillar += 1
            if len(hints) > 1 and len(set(h[0:3] for h in hints if h.startswith("D"))) > 1:
                ambiguous += 1
            rows.append((c["card_id"], tags, hints))

    rate = tagged / cards_n if cards_n else 0
    amb_rate = ambiguous / cards_n if cards_n else 0
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("# P1 试点统计（T-P1-08）\n\n")
        f.write(f"- 有效卡数（不含 X3 占位）: {cards_n}\n")
        f.write(f"- 能力标签可标注: {tagged} → **{rate:.1%}**\n")
        f.write(f"- 跨簇 pillar_hints（≥2 且跨 D 前缀）: {ambiguous} → 归属歧义率 **{amb_rate:.1%}**\n")
        f.write(f"- 多支柱提示（≥2）: {multi_pillar}\n\n")
        f.write("| 卡ID | 能力标签 | pillar_hints |\n|---|---|---|\n")
        for cid, tags, hints in rows:
            f.write(f"| {cid} | {','.join(sorted(tags)) or '—'} | {','.join(hints)} |\n")
    print(f"能力标签可标注率 {rate:.1%}；归属歧义率 {amb_rate:.1%}")
    sys.exit(0)


if __name__ == "__main__":
    main()
