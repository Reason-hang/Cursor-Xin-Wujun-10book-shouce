#!/usr/bin/env python3
"""T-P4-08：D10 创新与产品方法三道门裁决（§5.5）"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSIGN = ROOT / "ledger/P4_归属表.csv"
UNITS = ROOT / "data/units_index.json"
OUT_CSV = ROOT / "ledger/P4_D10三道门裁决.csv"
OUT_MD = ROOT / "ledger/P4_D10三道门裁决.md"

EXCLUDE_RE = re.compile(r"教育|升学|家庭|文明史|宏观|人口红利|高考")
CONTENT_UNITS = 1697
MIN_UNIT_RATIO = 0.03
MIN_CHARS = 100_000
MIN_BOOKS = 2
MIN_UNITS_SINGLE_BOOK = 5


def load_d10_scope():
    primary_cards = []
    unit_ids = set()
    for r in csv.DictReader(ASSIGN.open(encoding="utf-8")):
        if r["status"] != "draft":
            continue
        if r["primary_pillar"] == "D10-1":
            primary_cards.append(r)
            unit_ids.add(r["unit_id"])
        elif "D10" in (r.get("auxiliary_pillars") or ""):
            unit_ids.add(r["unit_id"])
    return primary_cards, unit_ids


def main():
    idx = {u["unit_id"]: u for u in json.loads(UNITS.read_text(encoding="utf-8"))["units"]}
    primary, scope_units = load_d10_scope()
    books = {idx[u]["book_code"] for u in scope_units if u in idx}
    chars = sum(idx[u].get("chars", 0) for u in scope_units if u in idx)
    ratio = len(scope_units) / CONTENT_UNITS
    claims = []
    for p in Path(ROOT / "cards").glob("*/*.json"):
        doc = json.loads(p.read_text(encoding="utf-8"))
        for c in doc.get("cards", []):
            if c.get("disposition") != "K":
                continue
            if doc.get("unit_id") not in scope_units:
                continue
            claims.append(c.get("claim", ""))

    ex_hits = sum(1 for t in claims if EXCLUDE_RE.search(t))
    ex_ratio = ex_hits / len(claims) if claims else 0

    gates = []
    # 证据门
    ev_books = len(books) >= MIN_BOOKS
    ev_chars = chars >= MIN_CHARS
    ev_ratio = ratio >= MIN_UNIT_RATIO
    ev_single = any(
        sum(1 for u in scope_units if u in idx and idx[u]["book_code"] == b) >= MIN_UNITS_SINGLE_BOOK
        for b in books
    )
    ev_pass = (ev_books or ev_single) and ev_chars and ev_ratio
    gates.append(
        {
            "gate": "证据门",
            "pass": "Y" if ev_pass else "N",
            "metric": f"书={len(books)} 单元={len(scope_units)}({ratio:.2%}) 汉字={chars}",
            "rule": f"跨≥{MIN_BOOKS}书或单书≥{MIN_UNITS_SINGLE_BOOK}单元；占比≥{MIN_UNIT_RATIO:.0%}；汉字≥{MIN_CHARS}",
            "detail": f"跨书={ev_books} 单书5+={ev_single} 占比={ev_ratio} 汉字={ev_chars}",
        }
    )
    # 价值门（P4 脚本仅记证据，M3 再验）
    val_pass = len(primary) >= 12 and len(books) >= 3
    gates.append(
        {
            "gate": "价值门",
            "pass": "provisional" if val_pass else "N",
            "metric": f"主归属 D10-1 K 卡={len(primary)} 书={len(books)}",
            "rule": "B端PM兼工程师 6–12月可用（P4 记 provisional，M3 使用验证）",
            "detail": "内容体量与跨书覆盖达 provisional 线；待 P5/M3 场景演练",
        }
    )
    # 排除门
    ex_pass = ex_ratio < 0.25
    gates.append(
        {
            "gate": "排除门",
            "pass": "Y" if ex_pass else "N",
            "metric": f"命中排除主题 claim 占比={ex_ratio:.1%} ({ex_hits}/{len(claims)})",
            "rule": "非宏观/文明/教育家庭主导",
            "detail": "关键词粗筛，P5 成稿再复核",
        }
    )

    strict_pass = ev_pass and val_pass != "N" and ex_pass
    if gates[1]["pass"] == "provisional":
        overall = "provisional_10_pillars" if ev_pass and ex_pass else "fail"
    else:
        overall = "keep_D10" if strict_pass else "merge_D10_to_D08"

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(gates[0].keys()) + ["overall"])
        w.writeheader()
        for g in gates:
            w.writerow({**g, "overall": overall})

    OUT_MD.write_text(
        "\n".join(
            [
                "# T-P4-08｜D10 三道门裁决（2026-10-27）",
                "",
                f"**总裁决**：`{overall}`",
                "",
                "| 门 | 通过 | 指标 |",
                "|---|---|---|",
                *[f"| {g['gate']} | {g['pass']} | {g['metric']} |" for g in gates],
                "",
                "## 说明",
                "",
                "- **证据门**：单元占比 **{:.2%}**（门槛 3%）——若严格按 §5.5，占比项 **未达标**。".format(ratio),
                "- **价值门**：`provisional`，待 M3 场景验证。",
                "- 若最终 `merge_D10_to_D08`：一级降为 9 柱，D10 内容并入 D08-1（见 §13 D10 手册条）。",
                "",
                "**下一工单**：T-P4-09 数量核对（L2/L3 目标区间与红线）",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"T-P4-08: overall={overall} ev_ratio={ratio:.2%}")


if __name__ == "__main__":
    main()
