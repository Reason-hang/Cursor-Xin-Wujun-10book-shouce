#!/usr/bin/env python3
"""按书拆分 130 条召回为 ledger/P6_召回批次/*.txt（便于分批填写）。"""
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "ledger/P6_抽检召回样本.csv"
BATCH = ROOT / "ledger/P6_召回批次"


def main() -> int:
    if not SAMPLE.is_file():
        print("FAIL: 先 make p6-recall-sample")
        return 1
    rows = list(csv.DictReader(SAMPLE.open(encoding="utf-8")))
    by_book: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_book[r["book_code"]].append(r)
    BATCH.mkdir(parents=True, exist_ok=True)
    readme = [
        "# P6 召回按书分批（AC-6.3）",
        "",
        "每本书一个 `.txt`：去掉行首 `#` 并在 `=` 后填 `pass` 或 `fail`。",
        "保存后：`make p6-recall-ingest`（会合并本目录全部 `.txt` 与 `P6_召回提交.txt`）。",
        "",
        "| 书码 | 文件 | 条数 |",
        "|---|---|---:|",
    ]
    for book in sorted(by_book):
        items = sorted(by_book[book], key=lambda x: x["unit_id"])
        lines = [
            f"# {book} 召回批次（{len(items)} 条）",
            "# 格式：unit_id=pass|fail",
            "",
        ]
        for r in items:
            title = (r.get("title") or "")[:40]
            lines.append(f"# {r['unit_id']}=  # {title}")
        path = BATCH / f"{book}.txt"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        readme.append(f"| {book} | `{book}.txt` | {len(items)} |")
    (BATCH / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
    print(f"recall batch init → {BATCH}（{len(by_book)} 书，{len(rows)} 条）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
