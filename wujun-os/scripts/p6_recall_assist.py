#!/usr/bin/env python3
"""T-P6-03 辅助：为 130 条抽检样本生成回读工作册（不代替人工 recall_status）。"""
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "ledger/P6_抽检召回样本.csv"
ASSIGN = ROOT / "ledger/P4_归属表.csv"
L3MAP = ROOT / "ledger/P4_卡到L3映射.csv"
CARDS = ROOT / "cards"
OUT = ROOT / "ledger/P6_抽检召回工作册.md"


def load_k_by_unit() -> dict[str, list[dict]]:
    by_unit: dict[str, list[dict]] = defaultdict(list)
    for r in csv.DictReader(ASSIGN.open(encoding="utf-8")):
        if r.get("status") != "draft":
            continue
        by_unit[r["unit_id"]].append(r)
    return by_unit


def load_l3() -> dict[str, str]:
    m: dict[str, str] = {}
    if L3MAP.is_file():
        for r in csv.DictReader(L3MAP.open(encoding="utf-8")):
            m[r["card_id"]] = r.get("l3_id", "")
    return m


def claims_from_json(unit_id: str) -> list[str]:
    book = unit_id.split("-")[0]
    p = CARDS / book / f"{unit_id}.json"
    if not p.is_file():
        return []
    d = json.loads(p.read_text(encoding="utf-8"))
    return [c.get("claim", "")[:120] for c in d.get("cards", []) if c.get("claim")]


def main() -> int:
    if not SAMPLE.is_file():
        print("FAIL: 先 make p6-recall-sample")
        return 1
    k_by_unit = load_k_by_unit()
    l3 = load_l3()
    rows = list(csv.DictReader(SAMPLE.open(encoding="utf-8")))
    lines = [
        "# P6 抽检召回工作册（AC-6.3）",
        "",
        f"> 样本 **{len(rows)}** 条；填写 `ledger/P6_抽检召回样本.csv` 的 `recall_status`（pass/fail/补写）。",
        "",
        "## 汇总",
        "",
        "| # | 书 | 单元 | 冻结 K | L3 | 层 | 状态 |",
        "|---:|---|---|---|---:|---|---|",
    ]
    detail: list[str] = ["", "## 逐条回读清单", ""]
    for i, r in enumerate(rows, 1):
        uid = r["unit_id"]
        ks = k_by_unit.get(uid, [])
        k_ids = [x["card_id"] for x in ks]
        pillar = ks[0]["primary_pillar"] if ks else "—"
        l3_id = l3.get(k_ids[0], "—") if k_ids else "—"
        claims = claims_from_json(uid)
        status = r.get("recall_status", "pending")
        lines.append(
            f"| {i} | {r['book_code']} | `{uid}` | {len(k_ids)} | {l3_id} | {r.get('layer','')} | {status} |"
        )
        detail.append(f"### {i}. {r['book_code']} `{uid}` — {r.get('title','')[:60]}")
        detail.append("")
        detail.append(f"- **支柱**：{pillar}｜**手册**：见 D 章与 M 卡（L3 `{l3_id}`）")
        if k_ids:
            detail.append(f"- **冻结 K**：{', '.join(k_ids[:3])}" + ("…" if len(k_ids) > 3 else ""))
        else:
            detail.append("- **冻结 K**：无（C 壳或未纳入 493；重点看手册整合层是否漏核心论点）")
        for j, c in enumerate(claims[:2], 1):
            detail.append(f"- claim{j}：{c}")
        detail.append(f"- **回读**：`src_frozen/` 对应书名 → 单元标题「{r.get('title','')}」")
        detail.append(f"- **判定**：□ pass □ fail □ 需补 K/M — 备注：")
        detail.append("")
    OUT.write_text("\n".join(lines + detail) + "\n", encoding="utf-8")
    print(f"p6 recall assist: {len(rows)} → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
