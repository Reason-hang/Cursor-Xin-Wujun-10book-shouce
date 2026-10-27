#!/usr/bin/env python3
"""T-P4-09：L2/L3 数量核对（§5.3.3 目标/预警/红线）"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L2 = ROOT / "ledger/P4_L2定稿.csv"
L3 = ROOT / "ledger/P4_L3模型清单.csv"
D10 = ROOT / "ledger/P4_D10三道门裁决.csv"
OUT = ROOT / "ledger/P4_数量核对表.csv"
REPORT = ROOT / "ledger/P4_数量核对_T-P4-09.md"

BANDS = {
    "L2_active": {"target_lo": 22, "target_hi": 28, "warn": 28, "red": 32},
    "L3": {"target_lo": 32, "target_hi": 44, "warn": 44, "red": 50},
    "L1": {"target_lo": 9, "target_hi": 10, "warn": 10, "red": 10},
}


def band_status(n: int, key: str) -> str:
    b = BANDS[key]
    if n > b["red"]:
        return "red"
    if n > b["warn"]:
        return "warn"
    if n < b["target_lo"]:
        return "below_target"
    if n <= b["target_hi"]:
        return "in_target"
    return "above_target_ok"


def main():
    l2_rows = list(csv.DictReader(L2.open(encoding="utf-8")))
    l3_rows = list(csv.DictReader(L3.open(encoding="utf-8")))
    active_l2 = sum(1 for r in l2_rows if r["status"] == "active")
    l3_n = len(l3_rows)
    l1_codes = {r["l1_code"] for r in l2_rows}
    d10_overall = ""
    if D10.is_file():
        d10_overall = next(csv.DictReader(D10.open(encoding="utf-8"))).get("overall", "")

    # D10 未确认前按 10 柱计；若 merge 则 L1=9
    l1_n = 10 if d10_overall != "merge_D10_to_D08" else 9
    l1_note = "10柱（D10 三道门 fail，待你确认是否降为 9）" if d10_overall == "fail" else f"L1={l1_n}"

    metrics = [
        ("L1_pillar", l1_n, "L1", l1_note),
        ("L2_active", active_l2, "L2_active", "薄簇降级后 active L2"),
        ("L3", l3_n, "L3", "机械聚类初稿，低于目标待 P4 拆簇"),
    ]
    rows = []
    for name, n, key, note in metrics:
        rows.append(
            {
                "metric": name,
                "count": n,
                "target_lo": BANDS[key]["target_lo"],
                "target_hi": BANDS[key]["target_hi"],
                "warn_line": BANDS[key]["warn"],
                "red_line": BANDS[key]["red"],
                "status": band_status(n, key),
                "note": note,
            }
        )

    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    red = [r for r in rows if r["status"] == "red"]
    warn = [r for r in rows if r["status"] == "warn"]
    REPORT.write_text(
        "\n".join(
            [
                "# T-P4-09｜数量核对（2026-10-27）",
                "",
                f"| 指标 | 数量 | 状态 |",
                f"|---|---|---|",
                *[f"| {r['metric']} | {r['count']} | {r['status']} |" for r in rows],
                "",
                f"- 触红线：**{len(red)}**；触预警：**{len(warn)}**",
                f"- D10 裁决：`{d10_overall or '—'}`（见 P4_D10三道门裁决.md）",
                "",
                "## 处置",
                "",
                "- L2/L3 **below_target**：P5 前需拆大簇或补命名，非红线违规。",
                "- 不超红线即可进入 T-P4-10 盲重标。",
                "",
                "**下一工单**：T-P4-10 盲重标（≥60 张，κ≥0.6）",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"T-P4-09: L2={active_l2} L3={l3_n} red={len(red)}")


if __name__ == "__main__":
    main()
