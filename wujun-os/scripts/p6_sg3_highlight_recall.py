#!/usr/bin/env python3
"""T-P6-05 / G10③：来信3 全量单元划重点召回（对照冻结 K + 锚点段）。"""
import csv
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import wujun_units  # noqa: E402

ASSIGN = ROOT / "ledger/P4_归属表.csv"
LEDGER = ROOT / "ledger/溯源与处置台账.md"
CARDS = ROOT / "cards"
SRC = ROOT / "src_frozen"
OUT = ROOT / "ledger/P6_SG3划重点召回_全量.md"
OUT_CSV = ROOT / "ledger/P6_SG3划重点召回_未覆盖.csv"
THRESH = 0.15
PASS_RATE = 0.95

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


def load_ledger() -> dict[str, tuple[str, int, int]]:
    by_card: dict[str, tuple[str, int, int]] = {}
    if not LEDGER.is_file():
        return by_card
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line or "卡ID" in line:
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 8:
            continue
        cid, book, cs, ce = c[0], c[1], int(c[4]), int(c[5])
        by_card[cid] = (book, cs, ce)
    return by_card


def cards_for_unit(unit_id: str) -> list[dict]:
    p = CARDS / unit_id.split("-")[0] / f"{unit_id}.json"
    if not p.is_file():
        return []
    return json.loads(p.read_text(encoding="utf-8")).get("cards", [])


def k_ids_for_unit(unit_id: str) -> list[str]:
    ids = []
    for r in csv.DictReader(ASSIGN.open(encoding="utf-8")):
        if r.get("status") == "draft" and r["unit_id"] == unit_id:
            ids.append(r["card_id"])
    return ids


def covered(item: str, cards: list[dict], seg_texts: list[str]) -> tuple[bool, str]:
    tok = cjk_tokens(item)
    for card in cards:
        claim = card.get("claim", "")
        if claim and jaccard(tok, cjk_tokens(claim)) >= THRESH:
            return True, card.get("card_id", "?")
    for seg in seg_texts:
        if jaccard(tok, cjk_tokens(seg)) >= THRESH:
            return True, "锚点段"
    return False, "—"


def main() -> int:
    ledger = load_ledger()
    book_cache: dict[str, str] = {}
    catalog = wujun_units.build_catalog(str(SRC))
    sg3 = catalog["per_book_units"].get("SG3", [])

    rows = []
    miss = []
    hit = total = 0
    units_with_hl = 0

    for i, ent in enumerate(sg3, 1):
        uid = f"SG3-U{i:04d}"
        highlights = extract_highlights(ent["text"])
        if not highlights:
            continue
        units_with_hl += 1
        cards = cards_for_unit(uid)
        seg_texts = []
        for cid in k_ids_for_unit(uid):
            if cid not in ledger:
                continue
            book, cs, ce = ledger[cid]
            if book not in book_cache:
                book_cache[book] = (SRC / book).read_text(encoding="utf-8")
            seg_texts.append(book_cache[book][cs:ce])
        for i, h in enumerate(highlights, 1):
            total += 1
            ok, via = covered(h, cards, seg_texts)
            hit += int(ok)
            rows.append((uid, i, ok, via, h[:100]))
            if not ok:
                miss.append((uid, i, h[:120]))

    rate = hit / total if total else 0.0
    verdict = "通过" if rate >= PASS_RATE else "未通过"

    with OUT.open("w", encoding="utf-8") as f:
        f.write("# P6 SG3 划重点召回（G10③ / T-P6-05）\n\n")
        f.write(f"- SG3 单元（catalog）: {len(sg3)}\n")
        f.write(f"- 含划重点块单元: {units_with_hl}\n")
        f.write(f"- 要点数: {total}；覆盖: {hit}\n")
        f.write(f"- **召回率: {rate:.2%}**（门槛 ≥{PASS_RATE:.0%}）\n\n")
        f.write("| unit_id | # | 覆盖 | 依据 | 要点摘要 |\n")
        f.write("|---|---|---|---|---|\n")
        for uid, i, ok, via, h in rows[:500]:
            f.write(f"| {uid} | {i} | {'Y' if ok else 'N'} | {via} | {h}… |\n")
        if len(rows) > 500:
            f.write(f"\n（表截断 500 行，全量未覆盖见 CSV，共 {len(rows)} 要点）\n")
        f.write(f"\n判定: **{verdict}**\n")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["unit_id", "bullet_no", "highlight_excerpt"])
        w.writerows(miss)

    print(f"p6 sg3 highlight recall: {hit}/{total} = {rate:.2%} -> {verdict}")
    return 0 if rate >= PASS_RATE else 1


if __name__ == "__main__":
    raise SystemExit(main())
