#!/usr/bin/env python3
"""T-P4-13：字典变更报告（相对 pillars v1.0 执行基线）"""
import hashlib
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ledger/P4_字典变更报告_T-P4-13.md"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    d10 = (ROOT / "ledger/P4_D10三道门裁决.md").read_text(encoding="utf-8")
    thin = (ROOT / "ledger/P4_薄簇处置.csv").read_text(encoding="utf-8").count("\n") - 1
    OUT.write_text(
        "\n".join(
            [
                "# T-P4-13｜字典变更报告（2026-10-27）",
                "",
                f"| pillars.yaml SHA-256 | `{sha(ROOT / 'spec/pillars.yaml')}` |",
                f"| 变更流程 | 无 §15.13 正式改柱；**待决**：D10 三道门 fail |",
                f"| 薄簇处置行 | {thin} |",
                f"| concept_keys | `rules/concept_keys.csv`（+206，P4-02） |",
                f"| precedents | `rules/precedents.md`（骨架） |",
                "",
                "## 待用户确认",
                "",
                "1. **D10**：保留 10 柱 vs 降为 9 柱并入 D08-1。",
                "2. **薄簇 5 L2**：手册章结构按 L2定稿 active/thin 执行。",
                "",
                "## P4 收口",
                "",
                "T-P4-01～12 产物已齐；**P5** 可启（须接受上表待决或书面默认）。",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"T-P4-13: {OUT}")


if __name__ == "__main__":
    main()
