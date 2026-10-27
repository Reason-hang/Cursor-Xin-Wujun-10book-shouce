#!/usr/bin/env python3
"""p1_select.py — T-P1-01 按 v2 §7.5 选约 14 类试点单元（固定种子，可复跑）

用法（在 wujun-os/ 根目录）:
  python3 scripts/p1_select.py --src src_frozen --index data/units_index.json --out ledger/P1_选样表.md
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from wujun_units import build_catalog, cjk, paras

SLOTS = [
    (1, "格局：沟通类 1 篇", "GJ", lambda u, t: "沟通" in u["title"] or "沟通" in t, {"min_chars": 500}),
    (2, "富足：可重复成功", "FZ", lambda u, t: "可重复" in u["title"] or "可重复" in t[:2000], {}),
    (2, "富足：做减法/本章小结", "FZ", lambda u, t: "减法" in u["title"] or "本章小结" in u["title"], {}),
    (3, "境界：经验与理性", "JJ", lambda u, t: ("经验" in u["title"] and "理性" in u["title"]) or ("经验" in t[:1500] and "理性" in t[:3000]), {}),
    (4, "见识：伪工作", "JS", lambda u, t: "伪工作" in u["title"] or "伪工作" in t[:2500], {}),
    (5, "态度：书信 1 封", "TD", lambda u, t: u["cls"] == "C" and u["seq"] in (2, 3, 4), {}),
    (6, "数学通识：1 讲", "SX", lambda u, t: u["cls"] == "C" and (re.search(r"\d+｜", u["title"]) or "讲" in u["title"]), {"prefer_seq": 10}),
    (7, "谷歌：第 008 封（三条边）", "GG", lambda u, t: "第008封信" in u["title"] or "三条边" in u["title"], {}),
    (8, "谷歌：回信精选", "GG", lambda u, t: u["is_interact"] or "回信精选" in u["title"], {}),
    (9, "谷歌：答读者问", "GG", lambda u, t: u["is_qa"], {}),
    (10, "来信1：考拉/袋鼠", "SG1", lambda u, t: "考拉" in t or "袋鼠" in t, {"min_chars": 800}),
    (12, "来信2：稀缺或超越免费", "WJ2", lambda u, t: "稀缺" in u["title"] or "超越免费" in u["title"] or "稀缺" in t[:2000], {}),
    (12, "来信2：系列 016/017", "WJ2", lambda u, t: re.search(r"第\s*0*16\s*封", u["title"]) or re.search(r"第\s*0*17\s*封", u["title"]), {"pair": "016-017"}),
    (13, "来信3：划重点 ×2", "SG3", lambda u, t: "\n### 划重点" in t or "\n## 划重点" in t, {"count": 2}),
    (14, "认命或大概率", None, lambda u, t: "认命" in t or "大概率" in t, {"min_chars": 400}),
]


def unit_text(cat, u):
    book = cat["books"][u["book_code"]]
    lines = book["lines"]
    s, e = u["line_start"] - 1, u["line_end"]
    return "\n".join(lines[s:e])


def pick_one(cat, code, pred, opts, used: set):
    cands = []
    for u in cat["units"]:
        if u["unit_id"] in used:
            continue
        if code and u["book_code"] != code:
            continue
        if u["cls"] == "N":
            continue
        t = unit_text(cat, u)
        if not pred(u, t):
            continue
        mc = opts.get("min_chars", 0)
        if u["chars"] < mc:
            continue
        score = u["chars"]
        if opts.get("prefer_seq") and u["seq"] == opts["prefer_seq"]:
            score += 1_000_000
        cands.append((score, u))
    if not cands:
        return None
    cands.sort(key=lambda x: -x[0])
    return cands[0][1]


def find_dup_pair(cat):
    P = {c: paras(cat["books"][c]["text"]) for c in ("SG1", "GG")}
    inter = set(P["SG1"]) & set(P["GG"])
    if not inter:
        return None, None
    snippet = max(inter, key=lambda s: cjk(s))
    def unit_hits(code):
        for u in cat["units"]:
            if u["book_code"] != code or u["cls"] == "N":
                continue
            if snippet[:40] in unit_text(cat, u):
                return u
        return None
    return unit_hits("SG1"), unit_hits("GG")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="src_frozen")
    ap.add_argument("--index", default="data/units_index.json")
    ap.add_argument("--out", default="ledger/P1_选样表.md")
    args = ap.parse_args()
    cat = build_catalog(args.src)
    used: set[str] = set()
    rows = []

    for slot, label, code, pred, opts in SLOTS:
        n = opts.get("count", 1)
        for _ in range(n):
            u = pick_one(cat, code, pred, opts, used)
            if not u:
                rows.append((slot, label, "—", "未匹配", "需人工补选"))
                continue
            used.add(u["unit_id"])
            rows.append((slot, label, u["unit_id"], u["title"][:60], f"{u['book_code']} L{u['line_start']}-{u['line_end']} {u['chars']}字"))

    sg, gg = find_dup_pair(cat)
    if sg and gg:
        for u in (sg, gg):
            if u["unit_id"] not in used:
                used.add(u["unit_id"])
        rows.append((11, "来信1↔谷歌重复段单元对", f"{sg['unit_id']} + {gg['unit_id']}", f"{sg['title'][:30]} / {gg['title'][:30]}", "双出处登记"))
    else:
        rows.append((11, "来信1↔谷歌重复段单元对", "—", "未匹配", "需人工补选"))

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("# P1 试点选样表（T-P1-01）\n\n")
        f.write("依据 v2 §7.5；**请用户过目确认**后执行 T-P1-02 抽卡。\n\n")
        f.write("| # | 样本类型 | unit_id | 标题 | 备注 |\n|---|---|---|---|---|\n")
        for r in rows:
            f.write(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} |\n")
        f.write(f"\n- 已选不重复单元数：**{len(used)}**\n")
        f.write("- Gate-P0 缺号：WJ2 周末问答 05、SG3 答读者问 48（默认沿用前置说明登记）\n")

    meta = {"units": sorted(used), "rows": len(rows)}
    sidecar = args.out.replace(".md", ".json")
    json.dump(meta, open(sidecar, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"p1_select: {len(used)} 个单元 -> {args.out}")
    missing = [r for r in rows if r[2] == "—"]
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
