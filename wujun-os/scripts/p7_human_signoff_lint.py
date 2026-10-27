#!/usr/bin/env python3
"""P7 人审签字项预检（不替代签字，仅汇总阻塞）。"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ledger/P7_人审签字预检.md"


def check_p4_sample() -> tuple[str, bool]:
    p = ROOT / "ledger/P4_抽查20张.csv"
    if not p.is_file():
        return "缺少文件", False
    rows = list(csv.DictReader(p.open(encoding="utf-8")))
    pending = sum(
        1
        for r in rows
        if "待用户" in (r.get("reviewer") or "") or "待用户" in (r.get("note") or "")
    )
    if pending:
        return f"{len(rows)} 行，仍标 Agent 预填待确认", False
    return f"{len(rows)} 行用户已确认", True


def check_signoff_table() -> tuple[str, bool]:
    p = ROOT / "ledger/P6_对抗式审查_签收表.md"
    if not p.is_file():
        return "缺少签收表", False
    text = p.read_text(encoding="utf-8")
    rows = [ln for ln in text.splitlines() if ln.startswith("|") and "你确认" not in ln and "---" not in ln]
    missing = sum(1 for ln in rows if re.search(r"\|\s*\|\s*\|", ln))
    if missing:
        return f"仍有 {missing} 行未填 Y/N", False
    sig = re.search(r"\*\*签收\*\*：\s*([^　\n]+)", text)
    if not sig or len(sig.group(1).strip()) < 2 or "_" in sig.group(1):
        return "签收/日期未填", False
    return "签收表已填", True


def check_trial_record() -> tuple[str, bool]:
    p = ROOT / "ledger/P6_用户试用记录.md"
    if not p.is_file():
        return "缺少试用记录", False
    text = p.read_text(encoding="utf-8")
    sig = re.search(r"\*\*签字\*\*：\s*([^　\n|_]+)", text)
    if sig and len(sig.group(1).strip()) >= 2:
        return "已签字", True
    filled = 0
    for block in re.split(r"^## 问题\s*\d+", text, flags=re.MULTILINE)[1:]:
        if re.search(r"\|\s*背景\s*\|\s*[^|\s].+\|", block):
            filled += 1
    if filled < 3:
        return f"3 问模板，背景已填 {filled}/3", False
    return "3 问已填（未签字）", False


def check_d10() -> tuple[str, bool]:
    for name in ("ledger/D10_裁决.txt", "ledger/P6_D10_批复.txt"):
        p = ROOT / name
        if p.is_file() and p.read_text(encoding="utf-8").strip() in ("A", "B", "D10=A", "D10=B"):
            return p.read_text(encoding="utf-8").strip(), True
    return "未写入 D10_裁决.txt（A 或 B）", False


def check_anchor_queue() -> tuple[str, bool]:
    p = ROOT / "ledger/P6_锚点修探针队列.csv"
    rows = list(csv.DictReader(p.open(encoding="utf-8")))
    pend = [r for r in rows if r.get("status") in ("pending", "approved")]
    if pend:
        return f"{len(pend)} 条未 done（可预演 make p6-anchor-queue-preview）", False
    return "队列已闭环", True


def main() -> int:
    checks = [
        ("D10 裁决", check_d10()),
        ("P4 抽查 20 张", check_p4_sample()),
        ("AC-6.9 签收", check_signoff_table()),
        ("AC-6.10 试用", check_trial_record()),
        ("锚点修探针队列", check_anchor_queue()),
    ]
    fail = sum(1 for _, (_, ok) in checks if not ok)
    lines = ["# P7 人审签字预检\n", f"\n**overall**：{'PASS' if fail == 0 else f'{fail} 项未过'}\n\n", "| 项 | 状态 | 结论 |\n", "|---|---|---|\n"]
    for name, (detail, ok) in checks:
        lines.append(f"| {name} | {'✅' if ok else '⚠️'} | {detail} |\n")
    lines.append("\n批复入口：`ledger/P6_待你批复清单.md`\n")
    OUT.write_text("".join(lines), encoding="utf-8")
    print(f"p7 human signoff: fail={fail} → {OUT}")
    return 0 if fail == 0 else 0  # 预检不阻断 gates；P7 验收前人工看报告


if __name__ == "__main__":
    sys.exit(main())
