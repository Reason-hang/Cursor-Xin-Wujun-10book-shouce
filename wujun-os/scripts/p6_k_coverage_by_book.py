#!/usr/bin/env python3
"""AC-6.2 预检：按书统计主归属 K 卡数量（非 100% 语义覆盖，供双向矩阵前置）。"""
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ledger/P6_分书K覆盖矩阵.csv"
BOOKS = ["TD", "FZ", "GJ", "GG", "JS", "SX", "WJ2", "SG1", "SG3", "JJ"]


def main() -> int:
    by_book: Counter[str] = Counter()
    for r in csv.DictReader((ROOT / "ledger/P4_归属表.csv").open(encoding="utf-8")):
        if r.get("status") != "draft":
            continue
        book = r.get("book_code", "UNK")
        by_book[book] += 1
    rows = [("book_code", "primary_k_count", "note")]
    for b in BOOKS:
        rows.append((b, str(by_book.get(b, 0)), "P4 主归属 K 行数"))
    rows.append(("TOTAL", str(sum(by_book.values())), "应≈493 冻结"))
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerows(rows)
    print(f"p6 k-by-book: {sum(by_book.values())} K → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
