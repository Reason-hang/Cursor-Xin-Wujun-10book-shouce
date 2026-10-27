#!/usr/bin/env python3
"""审计无卡单元，生成来信 A 层补批清单与首批 batch md。"""
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "cards"
BATCH_DIR = ROOT / "batches/P3a"
P3B_ORDER = ["GG", "WJ2", "SG3", "SG1"]
CHUNK = 12


def main():
    units = {u["unit_id"]: u for u in json.loads((ROOT / "data/units_index.json").read_text(encoding="utf-8"))["units"]}
    cards = {p.stem for p in CARDS.rglob("*.json")}
    triage = {r["unit_id"]: r for r in csv.DictReader(open(ROOT / "ledger/分诊表.csv", encoding="utf-8"))}
    missing_a = []
    for uid, r in triage.items():
        if uid in cards:
            continue
        if r["layer"] != "A":
            continue
        if r["book_code"] not in P3B_ORDER:
            continue
        missing_a.append(r)
    missing_a.sort(key=lambda r: (r["book_code"], r["unit_id"]))
    by_book = defaultdict(list)
    for r in missing_a:
        by_book[r["book_code"]].append(r)

    lines = [
        "# P3 来信 A 层缺口补批索引",
        "",
        f"- 缺口单元（分诊 A 层、无卡）：**{len(missing_a)}**",
        f"- 书序：{' → '.join(P3B_ORDER)}",
        "",
        "| batch_id | 书码 | 单元 |",
        "|---|---|---:|",
    ]
    batch_ids = []
    for code in P3B_ORDER:
        rows = by_book.get(code, [])
        for i in range(0, len(rows), CHUNK):
            bi = i // CHUNK + 1
            block = rows[i : i + CHUNK]
            bid = f"B-P3a-{code}-A-{bi:02d}"
            batch_ids.append((bid, code, block))
            lines.append(f"| {bid} | {code} | {len(block)} |")
            md = BATCH_DIR / f"{bid}.md"
            ch = sum(int(r["chars"]) for r in block)
            body = [
                f"# {bid}（P3a 补 · {code} · A 层来信/互动）",
                "",
                f"- 汉字: {ch}",
                f"- 单元: {len(block)}",
                "",
                "| unit_id | 标题 | 汉字 |",
                "|---|---|---:|",
            ]
            for r in block:
                body.append(f"| {r['unit_id']} | {r['title'][:50]} | {r['chars']} |")
            md.write_text("\n".join(body) + "\n", encoding="utf-8")

    (BATCH_DIR / "INDEX_来信A层补批.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    audit = ROOT / "ledger/P3_缺口审计.md"
    audit.write_text(
        "\n".join(
            [
                "# P3 缺口审计（自动生成）",
                "",
                f"| 无卡单元（units_index） | {sum(1 for u in units if u not in cards)} |",
                f"| 来信 A 层待补批 | {len(missing_a)} |",
                f"| 首批工单 | {batch_ids[0][0] if batch_ids else '—'} |",
                "",
                "下一命令：`make p3a-probes BATCH=B-P3a-GG-A-01`（示例）",
                "",
                "详见 `batches/P3a/INDEX_来信A层补批.md`。",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"P3-gap-plan: A层缺口={len(missing_a)} 批次数={len(batch_ids)} -> {audit}")


if __name__ == "__main__":
    main()
