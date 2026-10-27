#!/usr/bin/env python3
"""T-P4-07：L2 定稿 + 薄簇条款（K<8 或 书<2 → 降级为 L1 下 L3+标签）"""
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L2_IN = ROOT / "ledger/P4_L2清单.csv"
L3_IN = ROOT / "ledger/P4_L3模型清单.csv"
ASSIGN = ROOT / "ledger/P4_归属表.csv"
L2_OUT = ROOT / "ledger/P4_L2定稿.csv"
THIN_OUT = ROOT / "ledger/P4_薄簇处置.csv"
REPORT = ROOT / "ledger/P4_L2定稿_T-P4-07.md"

MIN_K_L2 = 8
MIN_BOOKS_L2 = 2


def load_l3_by_l2():
    by = {}
    for r in csv.DictReader(L3_IN.open(encoding="utf-8")):
        by.setdefault(r["l2_code"], []).append(r["l3_id"])
    return by


def tags_for_l2(l2_code: str) -> str:
    tags = Counter()
    for r in csv.DictReader(ASSIGN.open(encoding="utf-8")):
        if r["primary_pillar"] != l2_code:
            continue
        for t in (r.get("capability_tags") or "").split(";"):
            t = t.strip()
            if t:
                tags[t] += 1
    return ";".join(t for t, _ in tags.most_common(3))


def main():
    l3_map = load_l3_by_l2()
    l2_rows = list(csv.DictReader(L2_IN.open(encoding="utf-8")))
    final = []
    thin = []
    for r in l2_rows:
        k = int(r["k_count"])
        b = int(r["book_count"])
        reasons = []
        if k < MIN_K_L2:
            reasons.append(f"K<{MIN_K_L2}")
        if b < MIN_BOOKS_L2:
            reasons.append(f"书<{MIN_BOOKS_L2}")
        if reasons:
            status = "thin_downgrade"
            thin.append(
                {
                    "l2_code": r["l2_code"],
                    "l1_code": r["l1_code"],
                    "k_count": k,
                    "book_count": b,
                    "reason": "+".join(reasons),
                    "action": f"保留 L3 {','.join(l3_map.get(r['l2_code'], []))}，挂 {r['l1_code']} 章；L2 不留空壳",
                    "capability_tags": tags_for_l2(r["l2_code"]),
                }
            )
        else:
            status = "active"
        final.append(
            {
                "l2_code": r["l2_code"],
                "l1_code": r["l1_code"],
                "status": status,
                "k_count": k,
                "book_count": b,
                "l3_count": r["l3_count"],
                "l3_ids": ";".join(l3_map.get(r["l2_code"], [])),
                "capability_tags": tags_for_l2(r["l2_code"]) if status == "thin_downgrade" else "",
            }
        )

    with L2_OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(final[0].keys()))
        w.writeheader()
        w.writerows(final)

    fields = list(thin[0].keys()) if thin else ["l2_code", "reason", "action"]
    with THIN_OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(thin)

    active = sum(1 for x in final if x["status"] == "active")
    REPORT.write_text(
        "\n".join(
            [
                "# T-P4-07｜L2 定稿与薄簇（2026-10-27）",
                "",
                f"| L2 有卡 | {len(final)} |",
                f"| **active** L2 | **{active}** |",
                f"| **thin_downgrade** | **{len(thin)}** |",
                f"| 输出 | `{L2_OUT.name}`、`{THIN_OUT.name}` |",
                "",
                "**下一工单**：T-P4-08 创新/产品三道门裁决",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"T-P4-07: active L2={active} thin={len(thin)}")


if __name__ == "__main__":
    main()
