#!/usr/bin/env python3
"""为不在分诊表中的结构性单元（目录、发刊词等）落盘 X 处置壳，闭合 cards 缺口。"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "cards"


def load_units():
    return {u["unit_id"]: u for u in json.loads((ROOT / "data/units_index.json").read_text(encoding="utf-8"))["units"]}


def load_triage_ids():
    import csv

    return {r["unit_id"] for r in csv.DictReader(open(ROOT / "ledger/分诊表.csv", encoding="utf-8"))}


def main():
    dry = "--dry-run" in sys.argv
    units = load_units()
    triage_ids = load_triage_ids()
    created = skipped = 0
    for uid, u in sorted(units.items()):
        if uid in triage_ids:
            continue
        path = CARDS / u["book_code"] / f"{uid}.json"
        if path.is_file():
            skipped += 1
            continue
        title = u.get("title") or ""
        if "目录" in title:
            x_sub, rule = "X6", "结构性目录，不抽 K"
        elif any(k in title for k in ("发刊词", "收藏", "第二季来啦", "复习和书单")):
            x_sub, rule = "X7", "导航/元信息单元，不抽 K"
        else:
            x_sub, rule = "X8", "未入分诊表的结构性或边缘单元"
        doc = {
            "unit_id": uid,
            "book_code": u["book_code"],
            "title": title,
            "batch": "P3-meta-shell",
            "disposition_unit": "X",
            "layer": "—",
            "cards": [
                {
                    "card_id": f"P3meta-{uid}-X01",
                    "speaker": "—",
                    "claim": f"排除 {x_sub}：{rule}",
                    "type": "判断",
                    "disposition": x_sub,
                    "pillar_hints": [],
                    "capability_tags": [],
                    "stable": "稳定",
                }
            ],
            "note": "p3_meta_shell 自动生成；P2 分诊表未收录",
        }
        if dry:
            created += 1
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        created += 1
    print(f"P3-meta-shell: created={created} skipped_existing={skipped} dry={dry}")


if __name__ == "__main__":
    main()
