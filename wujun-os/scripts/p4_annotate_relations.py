#!/usr/bin/env python3
"""T-P4-04：对近似卡对做七类关系初标 + 冲突台账（指纹误配单独剔除）"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAIRS_IN = ROOT / "ledger/P4_近似卡对候选.csv"
REL_OUT = ROOT / "ledger/P4_卡对关系表.csv"
CONFLICT_OUT = ROOT / "ledger/P4_冲突台账.csv"
REPORT = ROOT / "ledger/P4_关系标注_T-P4-04.md"

CONFLICT_MARKERS = (
    ("不应", "应该"),
    ("不要", "要"),
    ("反对", "支持"),
    ("悲观", "乐观"),
)

REL_TYPES = (
    "同义重复",
    "同一机制、不同应用",
    "层次递进",
    "条件不同",
    "时间变化",
    "实质冲突",
    "独有论点",
    "指纹误配",
)


def suggest_relation(row: dict) -> tuple[str, str, str]:
    """返回 relation_type, review_status, note"""
    sim = float(row["sim_claim"])
    fp = float(row["sim_fingerprint"])
    ca, cb = row["claim_a"], row["claim_b"]
    same_book = row["book_a"] == row["book_b"]

    if fp >= 0.5 and sim < 0.22:
        return "指纹误配", "auto_distinct", "锚点指纹重合但 claim 不近，P4 聚类忽略"

    for a, b in CONFLICT_MARKERS:
        if (a in ca and b in cb) or (b in ca and a in cb):
            return "实质冲突", "needs_review", f"措辞对立标记：{a}/{b}"

    if sim >= 0.40:
        return "同义重复", "auto_same", ""
    if sim >= 0.33:
        if same_book:
            return "层次递进", "auto_variant", ""
        return "同一机制、不同应用", "auto_variant", ""
    if sim >= 0.28:
        return "条件不同", "auto_cond", ""
    if re.search(r"20\d{2}|当时|如今|今天|过去", ca + cb) and sim >= 0.22:
        return "时间变化", "auto_time", ""
    return "独有论点", "auto_distinct", "相似度低，保留独立卡"


def main():
    rows = list(csv.DictReader(PAIRS_IN.open(encoding="utf-8")))
    rel_rows = []
    conflicts = []
    fseq = 0
    for r in rows:
        rel, status, note = suggest_relation(r)
        rel_rows.append(
            {
                "pair_id": r["pair_id"],
                "card_a": r["card_a"],
                "card_b": r["card_b"],
                "score": r["score"],
                "sim_claim": r["sim_claim"],
                "sim_fingerprint": r["sim_fingerprint"],
                "relation_type": rel,
                "review_status": status,
                "note": note,
            }
        )
        if rel == "实质冲突":
            fseq += 1
            conflicts.append(
                {
                    "conflict_id": f"F-P4-{fseq:03d}",
                    "pair_id": r["pair_id"],
                    "card_a": r["card_a"],
                    "card_b": r["card_b"],
                    "status": "open",
                    "resolution": "",
                    "note": note,
                }
            )

    fields_rel = list(rel_rows[0].keys()) if rel_rows else []
    with REL_OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields_rel)
        w.writeheader()
        w.writerows(rel_rows)

    cfields = ["conflict_id", "pair_id", "card_a", "card_b", "status", "resolution", "note"]
    with CONFLICT_OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cfields)
        w.writeheader()
        w.writerows(conflicts)

    from collections import Counter

    c = Counter(x["relation_type"] for x in rel_rows)
    high = [x for x in rel_rows if float(x["sim_claim"]) >= 0.36 and x["relation_type"] != "指纹误配"]
    REPORT.write_text(
        "\n".join(
            [
                "# T-P4-04｜七类关系初标（2026-10-27）",
                "",
                f"| 输入对数 | {len(rows)} |",
                f"| 输出 | `{REL_OUT.name}` |",
                f"| 冲突登记 | `{CONFLICT_OUT.name}`（**{len(conflicts)}** 条 open） |",
                f"| 高相似真候选（sim_claim≥0.36，非指纹误配） | **{len(high)}** |",
                "",
                "## 关系分布",
                "",
                *[f"- {k}：{v}" for k, v in c.most_common()],
                "",
                "## 说明",
                "",
                "- `指纹误配`：仅指纹重合，claim 不近；聚类时不合并。",
                "- `实质冲突` 须人工填 `resolution` 后 status→resolved。",
                "- **下一工单**：T-P4-05 支柱归属（决策树 + 判例库骨架）。",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"T-P4-04: relations={len(rel_rows)} conflicts={len(conflicts)} -> {REL_OUT}")


if __name__ == "__main__":
    main()
