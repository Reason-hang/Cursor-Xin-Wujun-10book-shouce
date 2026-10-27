#!/usr/bin/env python3
"""T-P4-11：抽查 20 张（归属 + 转述），独立于盲重标样本"""
import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSIGN = ROOT / "ledger/P4_归属表.csv"
OUT = ROOT / "ledger/P4_抽查20张.csv"
REPORT = ROOT / "ledger/P4_抽查20张_T-P4-11.md"
SEED = 20261028


def load_claim(card_id: str) -> str:
    for p in ROOT.glob("cards/*/*.json"):
        doc = json.loads(p.read_text(encoding="utf-8"))
        for c in doc.get("cards", []):
            if c["card_id"] == card_id:
                return c.get("claim", "")
    return ""


def main():
    pool = [r for r in csv.DictReader(ASSIGN.open(encoding="utf-8")) if r["status"] == "draft"]
    rng = random.Random(SEED)
    pick = rng.sample(pool, 20)
    rows = []
    for i, r in enumerate(pick, 1):
        rows.append(
            {
                "seq": i,
                "card_id": r["card_id"],
                "unit_id": r["unit_id"],
                "primary_pillar": r["primary_pillar"],
                "claim": load_claim(r["card_id"])[:200],
                "归属明显错误": "",
                "转述失真": "",
                "reviewer": "待用户",
                "note": "",
            }
        )
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    REPORT.write_text(
        "\n".join(
            [
                "# T-P4-11｜抽查 20 张（2026-10-27）",
                "",
                f"| 样本 | 20（seed={SEED}，与盲重标样本 disjoint 不保证） |",
                f"| 表 | `{OUT.name}` |",
                "",
                "## AC-4.8",
                "",
                "- 填 `归属明显错误` / `转述失真`：Y/N；**明显错误 ≤3** 张通过。",
                "- Agent 预检：仅填表结构，**不代填 Y/N**（除下方草稿备注）。",
                "",
                "**下一工单**：T-P4-12 K 卡冻结（κ≥0.6 且抽查通过后）",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"T-P4-11: wrote {OUT}")


if __name__ == "__main__":
    main()
