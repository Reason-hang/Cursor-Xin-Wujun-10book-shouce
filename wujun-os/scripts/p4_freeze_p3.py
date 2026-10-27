#!/usr/bin/env python3
"""P4-01：冻结 P3 产物快照（锚点表哈希、卡面计数、分诊对齐）"""
import hashlib
import json
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def count_anchor_rows(p: Path) -> int:
    n = 0
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.startswith("| P") and "卡ID" not in line and "---" not in line:
            n += 1
    return n


def main():
    cards = list((ROOT / "cards").glob("*/*.json"))
    p3a = ROOT / "ledger/锚点表_P3a.md"
    p3b = ROOT / "ledger/锚点表_P3b.md"
    triage = ROOT / "ledger/分诊表.csv"
    state = json.loads((ROOT / "state/state.json").read_text(encoding="utf-8"))

    report = {
        "date": date.today().isoformat(),
        "ticket": "T-P4-01",
        "cards_json_count": len(cards),
        "anchors_p3a": count_anchor_rows(p3a),
        "anchors_p3b": count_anchor_rows(p3b),
        "sha256_p3a_ledger": sha256_file(p3a),
        "sha256_p3b_ledger": sha256_file(p3b),
        "sha256_triage": sha256_file(triage),
        "state_units_done": state["progress"].get("units_done"),
        "state_step": state.get("step"),
    }

    out = ROOT / "ledger/P4_P3产物冻结_2026-10-27.md"
    lines = [
        "# P4-01｜P3 产物冻结快照（2026-10-27）",
        "",
        "| 项 | 值 |",
        "|---|---|",
        f"| 工单 | T-P4-01 |",
        f"| `cards/*/*.json` | **{report['cards_json_count']}** |",
        f"| 锚点 P3a | **{report['anchors_p3a']}**（期望 315） |",
        f"| 锚点 P3b B 层 | **{report['anchors_p3b']}**（期望 170） |",
        f"| SHA-256 `锚点表_P3a.md` | `{report['sha256_p3a_ledger']}` |",
        f"| SHA-256 `锚点表_P3b.md` | `{report['sha256_p3b_ledger']}` |",
        f"| SHA-256 `分诊表.csv` | `{report['sha256_triage']}` |",
        f"| state.units_done | {report['state_units_done']} |",
        "",
        "## 验收（P4-01）",
        "",
        "- P3a/P3b 锚点行数与 `make p3a-verify-anchors` / `make p3b-verify-anchors` 一致",
        "- 本文件哈希写入 pack 后作为 P4 回溯基线",
        "- **下一工单**：T-P4-02 概念键归一（`data/concept_keys.csv`）",
        "",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    snap = ROOT / "data/p3_freeze_snapshot.json"
    snap.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"P4-01: {out}")
    print(f"  cards={report['cards_json_count']} p3a={report['anchors_p3a']} p3b={report['anchors_p3b']}")


if __name__ == "__main__":
    os.chdir(ROOT)
    main()
