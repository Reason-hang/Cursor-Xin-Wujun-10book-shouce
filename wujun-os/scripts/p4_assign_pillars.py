#!/usr/bin/env python3
"""T-P4-05：K 卡支柱归属初稿（pillar_hints[0] 为主归属，[1] 为辅助）"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILLARS = ROOT / "spec/pillars.yaml"
CODE_RE = re.compile(r"^\s+code:\s+(D\d{2}(?:-\d+)?)\s*$")
ASSIGN_OUT = ROOT / "ledger/P4_归属表.csv"
AMBIG_OUT = ROOT / "ledger/P4_归属歧义清单.csv"
REPORT = ROOT / "ledger/P4_归属_T-P4-05.md"


def load_valid_l2() -> set[str]:
    codes = set()
    for line in PILLARS.read_text(encoding="utf-8").splitlines():
        m = CODE_RE.match(line)
        if m:
            codes.add(m.group(1))
    return codes


def parent_d(code: str) -> str:
    m = re.match(r"(D\d{2})", code)
    return m.group(1) if m else code


def load_k_cards():
    rows = []
    for p in sorted(ROOT.glob("cards/*/*.json")):
        doc = json.loads(p.read_text(encoding="utf-8"))
        for c in doc.get("cards", []):
            if c.get("disposition") != "K":
                continue
            hints = [h.strip() for h in (c.get("pillar_hints") or []) if h.strip()]
            caps = [t.strip() for t in (c.get("capability_tags") or []) if t.strip()]
            rows.append(
                {
                    "card_id": c["card_id"],
                    "unit_id": doc.get("unit_id", p.stem),
                    "book_code": doc.get("book_code", p.parent.name),
                    "claim": (c.get("claim") or "")[:80],
                    "pillar_hints": hints,
                    "capability_tags": caps,
                }
            )
    return rows


def main():
    valid = load_valid_l2()
    cards = load_k_cards()
    assign = []
    ambig = []
    for c in cards:
        hints = c["pillar_hints"]
        d_hints = [h for h in hints if h.startswith("D") and h in valid]
        if not d_hints:
            primary, aux = "", ""
            status = "x_hint_only" if hints else "missing_hints"
        else:
            primary = d_hints[0]
            aux_list = d_hints[1:3]
            aux = ";".join(aux_list)
            status = "draft"
        cross = (
            len(d_hints) >= 2
            and parent_d(d_hints[0]) != parent_d(d_hints[1])
        )
        needs = "Y" if cross else "N"
        row = {
            "card_id": c["card_id"],
            "unit_id": c["unit_id"],
            "book_code": c["book_code"],
            "primary_pillar": primary,
            "auxiliary_pillars": aux,
            "capability_tags": ";".join(c["capability_tags"][:2]),
            "pillar_hints_raw": ";".join(hints),
            "status": status,
            "needs_precedent": needs,
        }
        assign.append(row)
        if needs == "Y" or status != "draft":
            ambig.append({**row, "note": "跨 D 柱双提示，主归属取 hints[0]" if cross else status})

    fields = list(assign[0].keys()) if assign else []
    with ASSIGN_OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(assign)

    afields = list(ambig[0].keys()) if ambig else fields + ["note"]
    with AMBIG_OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=afields)
        w.writeheader()
        w.writerows(ambig)

    cross_n = sum(1 for r in assign if r["needs_precedent"] == "Y")
    REPORT.write_text(
        "\n".join(
            [
                "# T-P4-05｜支柱归属初稿（2026-10-27）",
                "",
                f"| K 卡 | **{len(assign)}** |",
                f"| 主归属规则 | `pillar_hints[0]`；辅助 ≤2（hints[1:3]） |",
                f"| 跨柱歧义（需判例复核） | **{cross_n}** → `{AMBIG_OUT.name}` |",
                f"| 输出 | `{ASSIGN_OUT.name}` |",
                "",
                "**下一工单**：T-P4-06 L3 核心模型节点聚合（增长门）",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"T-P4-05: {len(assign)} cards, cross-pillar {cross_n} -> {ASSIGN_OUT}")


if __name__ == "__main__":
    main()
