#!/usr/bin/env python3
"""将 ledger/P6_召回提交.txt 合并进 P6_抽检召回样本.csv（须用户自填 pass/fail）。"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "ledger/P6_召回提交.txt"
BATCH = ROOT / "ledger/P6_召回批次"
SAMPLE = ROOT / "ledger/P6_抽检召回样本.csv"
ALLOWED = frozenset({"pass", "fail", "补写"})
BAD = re.compile(r"待填|PLACEHOLDER|示例|全部pass", re.I)


def parse_lines(text: str) -> dict[str, tuple[str, str]]:
    out: dict[str, tuple[str, str]] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        note = ""
        if "," in line and "=" not in line:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 2:
                raise ValueError(f"无法解析行: {raw}")
            uid, status = parts[0], parts[1]
            if len(parts) > 2:
                note = parts[2]
        else:
            if "=" not in line:
                raise ValueError(f"无法解析行: {raw}")
            uid, rest = line.split("=", 1)
            uid = uid.strip()
            if "|" in rest:
                status, note = [x.strip() for x in rest.split("|", 1)]
            else:
                status = rest.strip()
        status = status.lower()
        if status not in ALLOWED:
            raise ValueError(f"{uid} 状态须为 pass/fail/补写，当前: {status!r}")
        out[uid] = (status, note)
    return out


def load_submit_text() -> str:
    parts: list[str] = []
    if SRC.is_file():
        parts.append(SRC.read_text(encoding="utf-8"))
    if BATCH.is_dir():
        for p in sorted(BATCH.glob("*.txt")):
            parts.append(p.read_text(encoding="utf-8"))
    return "\n".join(parts)


def main() -> int:
    if not SAMPLE.is_file():
        print("FAIL: 先 make p6-recall-sample")
        return 1
    text = load_submit_text().strip()
    if not text:
        print("FAIL: 填写 P6_召回提交.txt 或 make p6-recall-batch-init 后编辑 ledger/P6_召回批次/*.txt")
        return 1
    if BAD.search(text):
        print("FAIL: 提交文件含占位或批量示例词，须逐条真实回读后填写")
        return 1
    try:
        updates = parse_lines(text)
    except ValueError as e:
        print(f"FAIL: {e}")
        return 1
    if not updates:
        print("FAIL: 无有效行")
        return 1

    rows = list(csv.DictReader(SAMPLE.open(encoding="utf-8")))
    fieldnames = rows[0].keys() if rows else []
    known = {r["unit_id"]: r for r in rows}
    unknown = [u for u in updates if u not in known]
    if unknown:
        print(f"FAIL: unit_id 不在样本中: {', '.join(unknown[:5])}" + (" …" if len(unknown) > 5 else ""))
        return 1

    n = 0
    for r in rows:
        uid = r["unit_id"]
        if uid not in updates:
            continue
        status, note = updates[uid]
        r["recall_status"] = status
        if note:
            r["note"] = note
        n += 1

    with SAMPLE.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    pend = sum(1 for r in rows if r.get("recall_status", "pending") == "pending")
    print(f"recall ingest OK: 更新 {n} 条；仍 pending {pend}/{len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
