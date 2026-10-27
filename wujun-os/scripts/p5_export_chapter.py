#!/usr/bin/env python3
"""P5：按章导出 L2/L3 与 K 卡清单（§14.7 写作输入）"""
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pillar", help="如 D06")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    p = args.pillar.upper()
    l2 = [r for r in csv.DictReader((ROOT / "ledger/P4_L2定稿.csv").open(encoding="utf-8")) if r["l1_code"] == p]
    l3 = [r for r in csv.DictReader((ROOT / "ledger/P4_L3模型清单.csv").open(encoding="utf-8")) if r["l1_code"] == p]
    krows = [r for r in csv.DictReader((ROOT / "ledger/P4_归属表.csv").open(encoding="utf-8")) if r["primary_pillar"].startswith(p + "-")]
    out_dir = Path(args.out) if args.out else ROOT / f"drafts/p5/{p}"
    out_dir.mkdir(parents=True, exist_ok=True)
    idx = out_dir / "INDEX.md"
    lines = [
        f"# P5｜第 {p[1:]} 章（{p}）写作输入",
        "",
        f"| K 卡（主归属 {p}） | **{len(krows)}** |",
        f"| L2 active | {sum(1 for x in l2 if x['status']=='active')} |",
        f"| L3 节点 | {len(l3)} |",
        "",
        "## L2",
        "",
    ]
    for r in l2:
        lines.append(f"- `{r['l2_code']}` {r['status']} K={r['k_count']}")
    lines += ["", "## L3 → 建议拆为多张 M 卡", ""]
    for r in l3:
        lines.append(f"- `{r['l3_id']}` {r['l2_code']} K={r['k_count']}")
    lines += ["", "## K 卡索引", "", "| card_id | unit | pillar |", "|---|---|---|"]
    for r in krows:
        lines.append(f"| {r['card_id']} | {r['unit_id']} | {r['primary_pillar']} |")
    idx.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"p5 export: {p} -> {idx} ({len(krows)} K)")


if __name__ == "__main__":
    main()
