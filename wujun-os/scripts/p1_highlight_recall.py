#!/usr/bin/env python3
"""p1_highlight_recall.py — 来信3 试点单元「划重点」召回（T-P1-07）

用法:
  python3 scripts/p1_highlight_recall.py \\
    --units ledger/P1_选样表.json \\
    --cards-dir cards \\
    --src src_frozen \\
    --ledger ledger/锚点表_试点.md \\
    --out ledger/P1_划重点召回.md

覆盖判定：划重点条目若存在卡 ID 登记（cards 中 external_recall=划重点 且 claim 含要点关键词），
或锚点段与划重点句 Jaccard(4字词) ≥0.15，则计为覆盖。
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import wujun_units  # noqa: E402


def load_book(path: str) -> str:
    return open(path, encoding="utf-8").read()

HIGHLIGHT = re.compile(r"^###\s+划重点\s*$", re.M)
BULLET = re.compile(r"^[0-9]+[、.．]\s*(.+)$")


def cjk_tokens(s: str, n=4):
    s = re.sub(r"\s+", "", s)
    return {s[i : i + n] for i in range(len(s) - n + 1)} if len(s) >= n else set()


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def extract_highlights(unit_text: str) -> list[str]:
    m = list(HIGHLIGHT.finditer(unit_text))
    if not m:
        return []
    start = m[-1].end()
    block = unit_text[start:]
    end = block.find("\n* * *")
    if end > 0:
        block = block[:end]
    items = []
    for line in block.split("\n"):
        line = line.strip()
        bm = BULLET.match(line)
        if bm:
            items.append(bm.group(1).strip())
    return items


def load_cards(cards_dir: str, unit_id: str) -> list[dict]:
    code = unit_id.split("-")[0]
    path = os.path.join(cards_dir, code, f"{unit_id}.json")
    if not os.path.isfile(path):
        return []
    data = json.load(open(path, encoding="utf-8"))
    return data.get("cards", [])


def anchor_segments(ledger_path: str, books_dir: str, unit_id: str) -> list[str]:
    cache = {}
    segs = []
    prefix = f"P1-{unit_id}-"
    for line in open(ledger_path, encoding="utf-8"):
        if not line.startswith("|"):
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 8 or not c[0].startswith(prefix):
            continue
        book, cs, ce = c[1], int(c[4]), int(c[5])
        if book not in cache:
            cache[book] = load_book(os.path.join(books_dir, book))
        segs.append(cache[book][cs:ce])
    return segs


def covered(item: str, cards: list[dict], segs: list[str], thresh=0.15) -> tuple[bool, str]:
    tok = cjk_tokens(item)
    for card in cards:
        claim = card.get("claim", "")
        if jaccard(tok, cjk_tokens(claim)) >= thresh:
            return True, card.get("card_id", "?")
    for seg in segs:
        if jaccard(tok, cjk_tokens(seg)) >= thresh:
            return True, "锚点段"
    return False, "—"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", default="ledger/P1_选样表.json")
    ap.add_argument("--cards-dir", default="cards")
    ap.add_argument("--src", default="src_frozen")
    ap.add_argument("--ledger", default="ledger/锚点表_试点.md")
    ap.add_argument("--out", default="ledger/P1_划重点召回.md")
    args = ap.parse_args()

    sel = json.load(open(args.units, encoding="utf-8"))
    catalog = wujun_units.build_catalog(args.src)
    by_id = {u["unit_id"]: u for u in catalog["units"]}
    sg3_units = [u for u in sel["units"] if u.startswith("SG3-")]

    rows = []
    hit = total = 0
    for uid in sg3_units:
        ent = by_id.get(uid)
        if not ent:
            continue
        seq = ent["seq"] - 1
        text = catalog["per_book_units"]["SG3"][seq]["text"]
        highlights = extract_highlights(text)
        cards = load_cards(args.cards_dir, uid)
        segs = anchor_segments(args.ledger, args.src, uid)
        for i, h in enumerate(highlights, 1):
            total += 1
            ok, via = covered(h, cards, segs)
            hit += int(ok)
            rows.append((uid, i, ok, via, h[:80]))

    rate = hit / total if total else 0.0
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("# P1 来信3 划重点召回（T-P1-07）\n\n")
        f.write(f"- 样本单元: {', '.join(sg3_units)}\n")
        f.write(f"- 要点数: {total}；覆盖: {hit}\n")
        f.write(f"- **召回率: {rate:.2%}**（门槛 ≥90%）\n\n")
        f.write("| unit_id | # | 覆盖 | 依据 | 要点摘要 |\n")
        f.write("|---|---|---|---|---|\n")
        for uid, i, ok, via, h in rows:
            f.write(f"| {uid} | {i} | {'Y' if ok else 'N'} | {via} | {h}… |\n")
        f.write("\n")
        verdict = "通过" if rate >= 0.9 else "未通过"
        f.write(f"判定: **{verdict}**\n")

    print(f"划重点召回: {hit}/{total} = {rate:.2%} -> {verdict}")
    sys.exit(0 if rate >= 0.9 else 1)


if __name__ == "__main__":
    main()
