#!/usr/bin/env python3
"""P3b C 层：按分诊表为无卡单元写入处置壳（不生成 K 主张/锚点）

- layer=C 且无 cards/<book>/<unit>.json 时落盘
- disposition_unit: X* 用分诊 x_sub；否则 C 层默认 M（并入/低信号，P4 再定）
- 不覆盖已有 K 卡（P3a/P3b 已抽）
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "cards"
VALID_X = {"X1", "X2", "X3", "X4", "X5", "X6", "X7", "X8"}


def load_units_index():
    data = json.loads((ROOT / "data/units_index.json").read_text(encoding="utf-8"))
    return {u["unit_id"]: u for u in data["units"]}


def main():
    dry = "--dry-run" in sys.argv
    units = load_units_index()
    rows = list(csv.DictReader(open(ROOT / "ledger/分诊表.csv", encoding="utf-8")))
    c_rows = [r for r in rows if r["layer"] == "C"]
    created = skipped = 0
    for r in c_rows:
        uid = r["unit_id"]
        if not uid in units:
            continue
        book = r["book_code"]
        path = CARDS / book / f"{uid}.json"
        if path.is_file():
            skipped += 1
            continue
        x_sub = (r.get("x_sub") or "").strip()
        if x_sub in VALID_X:
            disp_u, disp_c = "X", x_sub
            stable = "稳定"
        else:
            disp_u, disp_c = "M", "M"
            stable = "待P4"
        u = units[uid]
        doc = {
            "unit_id": uid,
            "book_code": book,
            "title": u["title"],
            "batch": "P3c-triage",
            "disposition_unit": disp_u,
            "layer": "C",
            "cards": [],
            "triage_rule": r.get("rule", ""),
            "note": f"C层壳；x_candidate={r.get('x_candidate','')}",
        }
        if disp_u == "X":
            doc["cards"] = [{
                "card_id": f"P3c-{uid}-X01",
                "speaker": "—",
                "claim": f"分诊排除 {x_sub}：{r.get('rule','')}",
                "type": "判断",
                "disposition": disp_c,
                "pillar_hints": [],
                "capability_tags": [],
                "stable": stable,
            }]
        if dry:
            created += 1
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        created += 1
    print(f"P3c: created={created} skipped_existing={skipped} dry={dry}")
    if created and not dry:
        print("提示：运行后请 make pack；P4 前核对 X 壳与 p2_x_readback 抽样")


if __name__ == "__main__":
    main()
