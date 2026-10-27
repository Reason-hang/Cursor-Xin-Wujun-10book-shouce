#!/usr/bin/env python3
"""P3b 二次补批：x_candidate=Y 且尚无 P3b-K 卡（多为 C 层）→ 按书装箱 3–5 万字/批。"""
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from s10_batcher import chunks

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "batches/P3b"
LEDGER = ROOT / "ledger/P3b_C层高信号缺口审计.md"
BOOKS = ["GG", "WJ2", "SG3"]
MIN_C, MAX_C = 30000, 50000
CARD_K = re.compile(r"^P3b-.+-K\d{2}$")


def card_ids_from_file(d: dict) -> list[str]:
    out: list[str] = []
    if d.get("card_id"):
        out.append(str(d["card_id"]))
    for c in d.get("cards") or []:
        if c.get("card_id"):
            out.append(str(c["card_id"]))
    return out


def unit_has_p3b_k(unit_id: str, by_unit: dict[str, list[str]]) -> bool:
    return any(CARD_K.match(c) for c in by_unit.get(unit_id, []))


def next_batch_index(code: str) -> int:
    n = 0
    for p in BATCH_DIR.glob(f"B-P3b-{code}-*.md"):
        m = re.match(rf"B-P3b-{code}-(\d{{3}})\.md$", p.name)
        if m:
            n = max(n, int(m.group(1)))
    return n + 1


def main():
    triage = list(csv.DictReader(open(ROOT / "ledger/分诊表.csv", encoding="utf-8")))
    by_unit: dict[str, list[str]] = defaultdict(list)
    for p in (ROOT / "cards").rglob("*.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        uid = p.stem
        by_unit[uid].extend(card_ids_from_file(d))

    gap = [
        r
        for r in triage
        if r.get("x_candidate") == "Y"
        and r["book_code"] in BOOKS
        and not unit_has_p3b_k(r["unit_id"], by_unit)
    ]
    gap.sort(key=lambda r: (r["book_code"], r["unit_id"]))
    by_book: dict[str, list] = defaultdict(list)
    for r in gap:
        by_book[r["book_code"]].append(r)

    index_rows: list[tuple[str, str, int, int]] = []
    for code in BOOKS:
        rows = by_book.get(code, [])
        if not rows:
            continue
        bi = next_batch_index(code)
        units = [
            {
                "unit_id": r["unit_id"],
                "title": r["title"],
                "chars": int(r["chars"]),
                "layer": r["layer"],
                "is_series": bool(r.get("series_gid")),
            }
            for r in rows
        ]
        for block, ch in chunks(units, MIN_C, MAX_C):
            bid = f"B-P3b-{code}-{bi:03d}"
            bi += 1
            path = BATCH_DIR / f"{bid}.md"
            body = [
                f"# {bid}（P3b · {code} · C 层高信号补批）",
                "",
                "- 来源：`x_candidate=Y` 且无 P3b-K 卡",
                f"- 汉字: {ch}",
                f"- 单元: {len(block)}",
                "",
                "| unit_id | 标题 | 汉字 | layer |",
                "|---|---|---:|---|",
            ]
            for u in block:
                body.append(
                    f"| {u['unit_id']} | {u['title'][:50]} | {u['chars']} | {u['layer']} |"
                )
            path.write_text("\n".join(body) + "\n", encoding="utf-8")
            index_rows.append((bid, code, ch, len(block)))

    idx = BATCH_DIR / "INDEX_P3b_C层高信号补批.md"
    lines = [
        "# P3b C 层高信号二次补批索引",
        "",
        f"- 缺口单元（x_candidate=Y、无 P3b-K）：**{len(gap)}**",
        f"- 书序：{' → '.join(BOOKS)}",
        f"- 本轮新批：**{len(index_rows)}**",
        "",
        "| batch_id | 书码 | 汉字 | 单元 |",
        "|---|---|---:|---:|",
    ]
    for bid, code, ch, n in index_rows:
        lines.append(f"| {bid} | {code} | {ch} | {n} |")
    idx.write_text("\n".join(lines) + "\n", encoding="utf-8")

    layer_ct = defaultdict(int)
    for r in gap:
        layer_ct[r["layer"]] += 1
    LEDGER.write_text(
        "\n".join(
            [
                "# P3b C 层高信号缺口审计",
                "",
                f"| 缺口合计 | **{len(gap)}** |",
                f"| GG | {len(by_book.get('GG', []))} |",
                f"| WJ2 | {len(by_book.get('WJ2', []))} |",
                f"| SG3 | {len(by_book.get('SG3', []))} |",
                f"| layer 分布 | {dict(layer_ct)} |",
                "",
                f"索引：`batches/P3b/INDEX_P3b_C层高信号补批.md`",
                "",
                "执行：`make p3b-probes BATCH=…` → 填 manifest → `make p3b-commit` → P4 增量。",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"P3b gap: {len(gap)} units -> {len(index_rows)} batches ({idx})")


if __name__ == "__main__":
    main()
