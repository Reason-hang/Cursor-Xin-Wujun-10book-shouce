#!/usr/bin/env python3
"""为 P6 锚点修探针队列生成 claim 子串探针建议（不修改锚点表）。"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "ledger/P6_锚点修探针队列.csv"
OUT = ROOT / "ledger/P6_锚点修探针建议.md"
BOOKS = ROOT / "src_frozen"


def find_claim(card_id: str) -> str:
    for p in Path(ROOT / "cards").rglob("*.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        for c in d.get("cards", []):
            if c["card_id"] == card_id:
                return c.get("claim", "")
    return ""


def suggest_probe(claim: str) -> str:
    claim = claim.replace("：", "").replace("，", "")
    for n in (12, 10, 8):
        if len(claim) >= n:
            sub = claim[:n]
            if sub.strip():
                return sub
    return claim[:8] if claim else ""


def locate_book(unit_id: str) -> list[Path]:
    code = unit_id.split("-")[0]
    return list(BOOKS.glob(f"*{code}*")) or list(BOOKS.glob("*.md"))


def main() -> int:
    lines = ["# P6 锚点修探针建议（未执行 make，仅建议）\n\n"]
    rows = list(csv.DictReader(QUEUE.open(encoding="utf-8")))
    for r in rows:
        if r.get("status") != "pending":
            continue
        cid, uid = r["card_id"], r["unit_id"]
        claim = find_claim(cid)
        probe = suggest_probe(claim)
        hits = []
        for bp in locate_book(uid):
            t = bp.read_text(encoding="utf-8", errors="ignore")
            if probe and probe in t:
                hits.append(bp.name)
        lines.append(f"## {cid}\n\n")
        lines.append(f"- claim：`{claim[:80]}…`\n")
        lines.append(f"- 建议 probe（≤12 字）：`{probe}`\n")
        lines.append(f"- 命中书文件：{hits[:3] or '（未命中，需人工选段）'}\n")
        lines.append(f"- 命令模板：`python3 scripts/anchor_tool.py make --book src_frozen/<书> --probe \"{probe}\" --words ... --id {cid}`\n\n")
    OUT.write_text("".join(lines), encoding="utf-8")
    print(f"p6 anchor suggest → {OUT} ({len(rows)} items)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
