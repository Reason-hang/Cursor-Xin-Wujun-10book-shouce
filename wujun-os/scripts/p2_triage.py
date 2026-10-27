#!/usr/bin/env python3
"""p2_triage.py — P2 分诊表生成 + 强制规则核对（T-P2-04/05）

用法:
  python3 scripts/p2_triage.py --src src_frozen --cards logs/unit_cards.md
  python3 scripts/p2_triage.py --verify-only
"""
import argparse
import csv
import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from wujun_units import build_catalog, QA, INTERACT

BOOK_A = {"JS", "GJ", "JJ", "FZ", "TD", "SX"}  # 六本成书
SKEL = re.compile(
    r"^(?:前言|序言|发刊词|后记|导读|小结|复盘|系统学习|结课)"
    r"|^总结[：:丨]"
    r"|(?:复盘|小结)$"
)
TRAVEL = re.compile(r"游记|旅行|日记\d|澳大利亚日记")
EDU = re.compile(r"高考|升学|留学|学校|大学|孩子|教育|家长|亲子")
HISTORY = re.compile(r"史|传记|公元|王朝|战役")
INTERACT_TITLE = re.compile(r"周末互动|周末放送|回信精选")


def series_key(title: str) -> str:
    t = re.sub(r"[（(][上下中一二三四五][）)]", "", title)
    t = re.sub(r"[上下]篇", "", t)
    return t.strip()


def series_gid(key: str) -> str:
    h = hashlib.sha1(key.encode("utf-8")).hexdigest()[:8]
    return f"SG-{h}"


def load_unit_card_flags(path: str) -> dict:
    """Parse s09 markdown table for 领域直连 / 划重点."""
    flags = {}
    if not os.path.isfile(path):
        return flags
    for line in open(path, encoding="utf-8"):
        if not line.startswith("|") or "-U" not in line:
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 11:
            continue
        uid = c[0]
        flags[uid] = {"domain": c[8] == "Y", "highlight": c[9] == "Y", "utype": c[2]}
    return flags


def x_candidate(title: str, utype: str) -> tuple[str, str]:
    if TRAVEL.search(title) or utype == "游记":
        return "Y", "X3"
    if EDU.search(title) or utype == "教育":
        return "Y", "X5"
    if HISTORY.search(title) and utype != "问答":
        return "Y", "X4"
    return "", ""


def assign_layer(u: dict, card: dict, title: str) -> tuple[str, str]:
    """Return layer, rule_tag."""
    if u["is_qa"]:
        return "B", "forced:问答→B"
    if u["is_interact"] or INTERACT_TITLE.search(title):
        return "A", "forced:互动/精选→A"
    if SKEL.search(title):
        return "A", "forced:骨架→A"
    if card.get("domain"):
        return "A", "forced:领域直连→A"
    if u["book_code"] in BOOK_A:
        return "A", "成书默认→A"
    return "C", "来信默认→C"


def build_rows(src: str, cards_path: str):
    cat = build_catalog(src)
    card_flags = load_unit_card_flags(cards_path)
    rows = []
    for u in cat["units"]:
        if u["cls"] != "C":
            continue
        uid = u["unit_id"]
        title = u["title"]
        cf = card_flags.get(uid, {})
        layer, rule = assign_layer(u, cf, title)
        xc, xsub = x_candidate(title, cf.get("utype", ""))
        spk = "Y" if (u["is_interact"] or INTERACT_TITLE.search(title) or u["is_qa"]) else ""
        sg = ""
        if u["is_series"]:
            sg = series_gid(series_key(title))
        rows.append(
            {
                "unit_id": uid,
                "book_code": u["book_code"],
                "title": title[:60],
                "layer": layer,
                "rule": rule,
                "x_candidate": xc,
                "x_sub": xsub,
                "series_gid": sg,
                "speaker_risk": spk,
                "chars": u["chars"],
            }
        )
    return rows


def verify(rows: list[dict], cat: dict) -> list[str]:
    errs = []
    by_id = {r["unit_id"]: r for r in rows}
    for u in cat["units"]:
        if u["cls"] != "C":
            continue
        r = by_id.get(u["unit_id"])
        if not r:
            errs.append(f"缺失分诊: {u['unit_id']}")
            continue
        title = u["title"]
        if u["is_qa"] and r["layer"] != "B":
            errs.append(f"AC-2.4 问答非B: {u['unit_id']}")
        if (u["is_interact"] or INTERACT_TITLE.search(title)) and r["layer"] != "A":
            errs.append(f"AC-2.4 互动非A: {u['unit_id']}")
        if SKEL.search(title) and r["layer"] != "A":
            errs.append(f"AC-2.4 骨架非A: {u['unit_id']}")
    # domain: re-check from rows that have forced domain
    for r in rows:
        if r["rule"] == "forced:领域直连→A" and r["layer"] != "A":
            errs.append(f"AC-2.4 领域直连非A: {r['unit_id']}")
    series_units = [u for u in cat["units"] if u["cls"] == "C" and u["is_series"]]
    for u in series_units:
        if not by_id[u["unit_id"]]["series_gid"]:
            errs.append(f"AC-2.3 系列无组: {u['unit_id']}")
    if len(series_units) < 85:
        errs.append(f"AC-2.3 系列单元过少: {len(series_units)}")
    return errs


def write_outputs(rows: list[dict], out_csv: str, out_md: str):
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
    fields = [
        "unit_id",
        "book_code",
        "layer",
        "rule",
        "x_candidate",
        "x_sub",
        "series_gid",
        "speaker_risk",
        "chars",
        "title",
    ]
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    from collections import Counter

    lc = Counter(r["layer"] for r in rows)
    ch = {k: sum(r["chars"] for r in rows if r["layer"] == k) for k in lc}
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("# P2 分诊表（脚本初稿 · T-P2-04）\n\n")
        f.write(f"- 内容单元: **{len(rows)}**\n")
        f.write(f"- A/B/C: {lc.get('A',0)} / {lc.get('B',0)} / {lc.get('C',0)}\n")
        f.write(f"- 汉字: A {ch.get('A',0):,} · B {ch.get('B',0):,} · C {ch.get('C',0):,}\n")
        f.write(f"- X 候选: {sum(1 for r in rows if r['x_candidate']=='Y')}\n")
        f.write(f"- 系列单元有组: {sum(1 for r in rows if r['series_gid'])}\n\n")
        f.write("机器可读: `ledger/分诊表.csv`\n\n")
        f.write("## 各层字数\n\n| 层 | 单元 | 汉字 |\n|---|---:|---:|\n")
        for k in ("A", "B", "C"):
            f.write(f"| {k} | {lc.get(k,0)} | {ch.get(k,0):,} |\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="src_frozen")
    ap.add_argument("--cards", default="logs/unit_cards.md")
    ap.add_argument("--out-csv", default="ledger/分诊表.csv")
    ap.add_argument("--out-md", default="ledger/分诊表.md")
    ap.add_argument("--verify-only", action="store_true")
    args = ap.parse_args()
    if args.verify_only:
        if not os.path.isfile(args.out_csv):
            print("缺分诊表，先运行不带 --verify-only", file=sys.stderr)
            sys.exit(2)
        rows = list(csv.DictReader(open(args.out_csv, encoding="utf-8")))
        cat = build_catalog(args.src)
        errs = verify(rows, cat)
        if errs:
            for e in errs[:20]:
                print(e)
            print(f"共 {len(errs)} 项问题")
            sys.exit(1)
        print(f"分诊核对通过: {len(rows)} 单元; 系列组 {sum(1 for r in rows if r['series_gid'])}")
        sys.exit(0)

    rows = build_rows(args.src, args.cards)
    write_outputs(rows, args.out_csv, args.out_md)
    cat = build_catalog(args.src)
    errs = verify(rows, cat)
    if errs:
        for e in errs[:15]:
            print(e, file=sys.stderr)
        sys.exit(1)
    print(f"p2_triage: {len(rows)} 行 -> {args.out_csv}")
    sys.exit(0)


if __name__ == "__main__":
    main()
