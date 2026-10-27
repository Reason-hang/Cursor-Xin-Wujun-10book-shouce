#!/usr/bin/env python3
"""s14_overlap.py — 两次抽卡锚点重合率（P1 / P6）

用法（在 wujun-os/ 下）:
  python3 scripts/s14_overlap.py --a ledger/锚点表_试点.md --b ledger/锚点表_试点_blind2.md

规则（spec v2 §7.5）：同一书文件内，两锚点字符区间重叠比例
  overlap = len(intersect) / len(union) >= 0.5 视为同一论点。
重合率 = 配对的同一论点数 / 两次论点总数（|A|+|B|−matched，即并集基数）。
"""
import argparse
import re
import sys


def parse_ledger(path):
    rows = []
    for line in open(path, encoding="utf-8"):
        if not line.startswith("|"):
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 8 or not re.fullmatch(r"\d+", c[2]):
            continue
        rows.append(
            {
                "id": c[0],
                "book": c[1],
                "cs": int(c[4]),
                "ce": int(c[5]),
            }
        )
    return rows


def unit_key(card_id):
    m = re.match(r"P1-([A-Z0-9]+-U\d+)", card_id)
    return m.group(1) if m else card_id


def span_overlap(a, b):
    if a["book"] != b["book"]:
        return 0.0
    inter = max(0, min(a["ce"], b["ce"]) - max(a["cs"], b["cs"]))
    if inter <= 0:
        return 0.0
    union = max(a["ce"], b["ce"]) - min(a["cs"], b["cs"])
    return inter / union if union else 0.0


def match_passes(a_rows, b_rows, thresh=0.5):
    by_unit_a = {}
    for r in a_rows:
        by_unit_a.setdefault(unit_key(r["id"]), []).append(r)
    by_unit_b = {}
    for r in b_rows:
        by_unit_b.setdefault(unit_key(r["id"]), []).append(r)

    matched = 0
    details = []
    units = sorted(set(by_unit_a) | set(by_unit_b))
    for u in units:
        la, lb = by_unit_a.get(u, []), by_unit_b.get(u, [])
        used_b = set()
        for ra in la:
            best_j, best_o = -1, 0.0
            for j, rb in enumerate(lb):
                if j in used_b:
                    continue
                o = span_overlap(ra, rb)
                if o >= thresh and o > best_o:
                    best_o, best_j = o, j
            if best_j >= 0:
                used_b.add(best_j)
                matched += 1
                details.append((u, ra["id"], lb[best_j]["id"], f"{best_o:.2f}"))
            else:
                details.append((u, ra["id"], "—", "未配对"))
        for j, rb in enumerate(lb):
            if j not in used_b:
                details.append((u, "—", rb["id"], "未配对"))

    union_n = len(a_rows) + len(b_rows) - matched
    rate = matched / union_n if union_n else 0.0
    return rate, matched, union_n, len(a_rows), len(b_rows), details


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, help="首轮锚点表")
    ap.add_argument("--b", required=True, help="双盲第二轮锚点表")
    ap.add_argument("--thresh", type=float, default=0.5)
    args = ap.parse_args()
    a_rows = parse_ledger(args.a)
    b_rows = parse_ledger(args.b)
    if not a_rows or not b_rows:
        print("锚点表为空或无法解析", file=sys.stderr)
        sys.exit(2)
    rate, matched, union_n, na, nb, details = match_passes(a_rows, b_rows, args.thresh)
    print(f"S14 重合率: {rate:.4f}（配对 {matched} / 并集 {union_n}；首轮 {na}，盲抽 {nb}）")
    for u, ida, idb, note in details:
        if note == "未配对":
            print(f"  [{u}] {ida} ↔ {idb} ({note})")
    verdict = "通过" if rate >= 0.7 else ("修规则补试点" if rate >= 0.5 else "停线·降级评估")
    print(f"判定: {verdict}（阈值 ≥0.7）")
    sys.exit(0 if rate >= 0.7 else 1)


if __name__ == "__main__":
    main()
