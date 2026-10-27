#!/usr/bin/env python3
"""AC-6.5：50 张 M 卡「数理工程表达」字段（第 5 项）可检验率审计。"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "drafts/p5"
OUT = ROOT / "ledger/P6_数理映射审计.md"
FIELD_RE = re.compile(r"^5\.\s*数理[^\n：]*[：:]\s*(.+)$", re.MULTILINE)


def main() -> int:
    cards = sorted(DRAFT.glob("D*/M-*.md"))
    missing: list[str] = []
    rows: list[tuple[str, str]] = []
    for p in cards:
        text = p.read_text(encoding="utf-8")
        m = FIELD_RE.search(text)
        if not m or len(m.group(1).strip()) < 4:
            missing.append(p.name)
            continue
        rows.append((p.parent.name, p.stem, m.group(1).strip()[:80]))
    body = [
        "# P6 数理映射可检验率（AC-6.5）",
        "",
        f"| 指标 | 值 |",
        f"|---|---|",
        f"| M 卡总数 | {len(cards)} |",
        f"| 字段 5 已填 | {len(rows)} |",
        f"| 缺失/过短 | {len(missing)} |",
        f"| 可检验率 | **{100.0 * len(rows) / len(cards) if cards else 0:.1f}%** |",
        "",
        f"**结论**：{'PASS（50/50）' if not missing else 'FAIL'}",
        "",
        "复跑：`make p6-math-audit`",
    ]
    if missing:
        body.extend(["", "## 缺失", ""] + [f"- {x}" for x in missing])
    OUT.write_text("\n".join(body) + "\n", encoding="utf-8")
    print(f"p6 math audit: {len(rows)}/{len(cards)} → {OUT}")
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
