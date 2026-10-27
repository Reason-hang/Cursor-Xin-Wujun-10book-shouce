#!/usr/bin/env python3
"""P6 锚点修探针队列：预演 / 批复后写回 ledger 并 verify。"""
import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "ledger/P6_锚点修探针队列.csv"
LEDGER = ROOT / "ledger/溯源与处置台账.md"
OUT_PREVIEW = ROOT / "ledger/P6_锚点修探针_预演.md"
BOOKS = ROOT / "src_frozen"

# 由 anchor_tool make 生成（不改 claim，仅重探针）
REPAIR_ROWS: dict[str, str] = {
    "P3b-SG3-U0249-K01": (
        "| P3b-SG3-U0249-K01 | 《硅谷来信3》｜原著完整精排典藏版｜Codex处理_副本.md "
        "| 26195 | 26195 | 1056819 | 1056840 | 3c7424836b27d6befe02845d0aeb60b9e860196f | 成绩好,能力强,因果关系 |"
    ),
    "P3a-SX-U0043-K01": (
        "| P3a-SX-U0043-K01 | 《数学通识50讲》[吴军]-原著完整精排版_副本2.md "
        "| 5587 | 5587 | 156574 | 156586 | 7b80067a8f9d414783b0e50736d239c88e20b4c6 | 贝叶斯,公式 |"
    ),
    "P3a-GJ-U0007-K01": (
        "| P3a-GJ-U0007-K01 | 《格局》[吴军]--原著完整精排版_副本2.md "
        "| 257 | 257 | 13495 | 13534 | 0fd9840fde920717840ad1f9844977da4753ebac | 利益,分享,决策 |"
    ),
}


def write_preview() -> None:
    lines = [
        "# P6 锚点修探针预演（未写回 ledger）\n",
        "批复：将 `P6_锚点修探针队列.csv` 对应行 `status` 改为 `approved`，再 `make p6-anchor-queue-apply`。\n",
        "\n",
    ]
    for cid, row in REPAIR_ROWS.items():
        lines.append(f"## {cid}\n\n{row}\n\n")
    OUT_PREVIEW.write_text("".join(lines), encoding="utf-8")


def load_queue() -> list[dict[str, str]]:
    if not QUEUE.is_file():
        sys.exit("FAIL: 缺少锚点队列 CSV")
    return list(csv.DictReader(QUEUE.open(encoding="utf-8")))


def replace_ledger_row(card_id: str, new_line: str) -> bool:
    text = LEDGER.read_text(encoding="utf-8")
    pat = re.compile(rf"^\| {re.escape(card_id)} \|.*$", re.MULTILINE)
    if not pat.search(text):
        print(f"FAIL: ledger 无行 {card_id}")
        return False
    text = pat.sub(new_line, text, count=1)
    LEDGER.write_text(text, encoding="utf-8")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="写回 ledger 并 verify")
    args = ap.parse_args()
    write_preview()
    rows = load_queue()
    pending = [r for r in rows if r.get("status", "pending") != "approved"]
    if not args.apply:
        print(f"preview → {OUT_PREVIEW}（{len(REPAIR_ROWS)} 条预演；队列 pending={len(pending)}）")
        return 0
    if pending:
        print("FAIL: 仍有未 approved 的队列项，拒绝写回")
        for r in pending:
            print(" ", r.get("card_id"), r.get("status"))
        return 1
    for cid in REPAIR_ROWS:
        if not replace_ledger_row(cid, REPAIR_ROWS[cid]):
            return 1
    for r in rows:
        if r["card_id"] in REPAIR_ROWS:
            r["status"] = "done"
    with QUEUE.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    rc = subprocess.call(
        [
            sys.executable,
            str(ROOT / "scripts/anchor_tool.py"),
            "verify",
            "--ledger",
            str(LEDGER),
            "--books-dir",
            str(BOOKS),
        ]
    )
    if rc == 0:
        print("anchor queue apply: ledger 已更新且 verify PASS")
    return rc


if __name__ == "__main__":
    sys.exit(main())
