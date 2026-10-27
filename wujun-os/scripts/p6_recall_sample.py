#!/usr/bin/env python3
"""T-P6-03：生成 P6 抽检召回样本清单（成书 15/本、来信 10/本，确定性种子）。"""
import csv
import hashlib
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRIAGE = ROOT / "ledger/分诊表.csv"
ASSIGN = ROOT / "ledger/P4_归属表.csv"
OUT = ROOT / "ledger/P6_抽检召回样本.csv"

BOOK_SAMPLE = {
    "TD": 15,
    "FZ": 15,
    "GJ": 15,
    "GG": 15,
    "JS": 15,
    "SX": 15,
    "WJ2": 10,
    "SG1": 10,
    "SG3": 10,
    "JJ": 10,
}
# 成书在分诊表多为 A 层；来信/GG 含 B/C
BOOK_LAYERS: dict[str, tuple[str, ...]] = {
    "TD": ("A",),
    "FZ": ("A",),
    "GJ": ("A",),
    "JS": ("A",),
    "SX": ("A",),
    "JJ": ("A",),
    "GG": ("A", "B", "C"),
    "WJ2": ("A", "B", "C"),
    "SG1": ("A", "C"),
    "SG3": ("A", "B", "C"),
}


def seed_for(book: str) -> int:
    h = hashlib.sha256(f"P6-recall-{book}".encode()).hexdigest()
    return int(h[:8], 16)


def eligible_units_by_book() -> dict[str, list[dict]]:
    by_book: dict[str, list[dict]] = {b: [] for b in BOOK_SAMPLE}
    for r in csv.DictReader(TRIAGE.open(encoding="utf-8")):
        b = r["book_code"]
        if b in by_book and r.get("layer") in BOOK_LAYERS.get(b, ("A", "B", "C")):
            by_book[b].append(r)
    return by_book


def main() -> int:
    pool = eligible_units_by_book()
    rows = []
    for book, n in BOOK_SAMPLE.items():
        candidates = sorted(pool[book], key=lambda x: x["unit_id"])
        rng = random.Random(seed_for(book))
        pick = candidates if len(candidates) <= n else rng.sample(candidates, n)
        short = len(pick) < n
        for r in sorted(pick, key=lambda x: x["unit_id"]):
            rows.append(
                {
                    "book_code": book,
                    "unit_id": r["unit_id"],
                    "title": r.get("title", "")[:80],
                    "layer": r.get("layer", ""),
                    "recall_status": "pending",
                    "note": (
                        f"回读原文对照手册/K；池仅 {len(candidates)} 条"
                        if short
                        else "回读原文对照手册/K；漏则补写或登记降级"
                    ),
                }
            )
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"p6 recall sample: {len(rows)} 条 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
