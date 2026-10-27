#!/usr/bin/env python3
"""T-P6-02 机械层：K↔单元双向闭合预检（非语义 100%，供 D4 覆盖矩阵前置）。"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSIGN = ROOT / "ledger/P4_归属表.csv"
TRIAGE = ROOT / "ledger/分诊表.csv"
CARDS = ROOT / "cards"
OUT_CSV = ROOT / "ledger/P6_双向矩阵_分书汇总.csv"
OUT_MD = ROOT / "ledger/P6_双向矩阵_机械预检.md"
BOOKS = ["TD", "FZ", "GJ", "GG", "JS", "SX", "WJ2", "SG1", "SG3", "JJ"]
BOOK_LAYERS: dict[str, tuple[str, ...]] = {
    "TD": ("A",),
    "FZ": ("A",),
    "GJ": ("A",),
    "JS": ("A",),
    "SX": ("A",),
    "JJ": ("A",),
    "GG": ("A", "B", "C"),
    "WJ2": ("A", "B", "C"),
    "SG1": ("A", "C"),
    "SG3": ("A", "B", "C"),
}


def load_triage() -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for r in csv.DictReader(TRIAGE.open(encoding="utf-8")):
        out[r["unit_id"]] = r
    return out


def load_json_card_ids() -> dict[str, set[str]]:
    by_unit: dict[str, set[str]] = defaultdict(set)
    for p in CARDS.rglob("*.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        uid = d.get("unit_id", "")
        for c in d.get("cards", []):
            cid = c.get("card_id")
            if cid:
                by_unit[uid].add(cid)
    return by_unit


def main() -> int:
    triage = load_triage()
    json_ids = load_json_card_ids()
    k_rows = [
        r
        for r in csv.DictReader(ASSIGN.open(encoding="utf-8"))
        if r.get("status") == "draft"
    ]
    forward_fail: list[str] = []
    units_with_k: dict[str, set[str]] = defaultdict(set)
    by_book_k: Counter[str] = Counter()

    for r in k_rows:
        cid = r["card_id"]
        uid = r["unit_id"]
        book = r["book_code"]
        by_book_k[book] += 1
        units_with_k[uid].add(cid)
        t = triage.get(uid)
        if not t:
            forward_fail.append(f"{cid}: 单元 {uid} 不在分诊表")
            continue
        if t.get("book_code") != book:
            forward_fail.append(f"{cid}: 书码 {book} ≠ 分诊 {t.get('book_code')}")
        if cid not in json_ids.get(uid, set()):
            forward_fail.append(f"{cid}: 未出现在 cards/{uid}.json")

    # 反向：分诊单元 → 至少一张冻结 K（仅统计 B/C 层，A 层多为骨架）
    by_book_units: dict[str, list[dict]] = {b: [] for b in BOOKS}
    for uid, t in triage.items():
        b = t.get("book_code", "")
        if b in by_book_units:
            by_book_units[b].append(t)

    summary_rows = []
    frozen_ids = {r["card_id"] for r in k_rows}
    orphan_k_in_json: list[str] = []
    for p in CARDS.rglob("*.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        for c in d.get("cards", []):
            cid = c.get("card_id", "")
            if not cid or c.get("disposition") != "K":
                continue
            if cid in frozen_ids:
                continue
            # P1 试点召回卡（Rxx）未进 P4 冻结表，记为已知例外
            if cid.startswith("P1-") and "-R" in cid:
                continue
            orphan_k_in_json.append(cid)

    for b in BOOKS:
        units = by_book_units[b]
        elig = [u for u in units if u.get("layer") in BOOK_LAYERS.get(b, ("A", "B", "C"))]
        covered = sum(1 for u in elig if u["unit_id"] in units_with_k)
        summary_rows.append(
            {
                "book_code": b,
                "k_frozen_count": by_book_k.get(b, 0),
                "content_units": len(elig),
                "units_with_k": covered,
                "unit_k_coverage_pct": f"{100.0 * covered / len(elig):.1f}" if elig else "n/a",
                "forward_fail_count": sum(1 for x in forward_fail if f"-{b}-" in x or f" {b} " in x),
            }
        )

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        w.writeheader()
        w.writerows(summary_rows)

    mech_pass = len(forward_fail) == 0 and not orphan_k_in_json
    md = [
        "# P6 双向矩阵｜机械预检（T-P6-02）",
        "",
        f"- 冻结 K 行数：**{len(k_rows)}**（期望 ≈493）",
        f"- 正向闭合（K→单元→JSON）：**{'PASS' if not forward_fail else 'FAIL'}**（异常 {len(forward_fail)}）",
        f"- 反向孤儿 K（JSON 有、归属表无）：**{len(orphan_k_in_json)}**"
        + (f"（{', '.join(orphan_k_in_json[:5])}）" if orphan_k_in_json else "（P1-R 卡已豁免）"),
        f"- 机械预检 overall：**{'PASS' if mech_pass else 'FAIL'}**",
        "",
        "> 语义「核心论点 100%」仍需人工双向矩阵 + 回读；本文件仅 G9 图论闭合。",
        "",
        "## 分书汇总",
        "",
        "| 书码 | 冻结 K | 内容单元 | 有 K 单元 | 单元覆盖率 |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in summary_rows:
        md.append(
            f"| {r['book_code']} | {r['k_frozen_count']} | {r['content_units']} | {r['units_with_k']} | {r['unit_k_coverage_pct']}% |"
        )
    if forward_fail:
        md.extend(["", "## 正向异常（前 30）", ""])
        for line in forward_fail[:30]:
            md.append(f"- {line}")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"p6 bidir: K={len(k_rows)} forward_fail={len(forward_fail)} orphan_json={orphan_k_in_json} → {OUT_MD}")
    return 0 if mech_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
