#!/usr/bin/env python3
"""P6：汇总各章 AC-5.8 必检议题覆盖表 → ledger/P6_必检112项汇总.csv。"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "drafts/p5"
OUT = ROOT / "ledger/P6_必检112项汇总.csv"
MUST_CHECK_EXPECT = 112

CHAPTER_RE = re.compile(r"^D(\d{2})$")


def chapter_sort_key(path: Path) -> tuple[int, str]:
    m = CHAPTER_RE.match(path.parent.name)
    return (int(m.group(1)) if m else 99, path.name)


def parse_row(line: str) -> dict[str, str] | None:
    stripped = line.strip()
    if not stripped.startswith("| D"):
        return None
    if "必检议题" in stripped or "---" in stripped:
        return None
    cells = [c.strip() for c in stripped.strip("|").split("|")]
    if len(cells) < 6:
        return None
    l2 = cells[0]
    if "-" not in l2:
        return None
    chapter = l2.split("-", 1)[0]
    return {
        "chapter": chapter,
        "L2": l2,
        "topic": cells[2],
        "outcome": cells[3],
        "location": cells[4],
        "evidence_k": cells[5],
    }


def collect_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    paths = sorted(DRAFT.glob("D*/AC-5.8_*必检议题覆盖表.md"), key=chapter_sort_key)
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            row = parse_row(line)
            if row:
                rows.append(row)
    return rows


def main() -> int:
    rows = collect_rows()
    if len(rows) != MUST_CHECK_EXPECT:
        print(f"FAIL: 汇总 {len(rows)} 行，期望 {MUST_CHECK_EXPECT}")
        return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["chapter", "L2", "topic", "outcome", "location", "evidence_k"]
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"p6 must-check rollup: {len(rows)} rows → {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
