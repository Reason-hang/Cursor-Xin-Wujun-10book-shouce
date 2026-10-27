#!/usr/bin/env python3
"""阶段验收合一审计：可机械验证的 AC-6 / AC-7 与 p7-ready 阻塞项。"""
import csv
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ledger/P7_阶段验收审计.md"
sys.path.insert(0, str(ROOT / "scripts"))

from p7_human_signoff_lint import (
    check_anchor_queue,
    check_d10,
    check_p4_sample,
    check_signoff_table,
    check_trial_record,
)


def run_script(name: str) -> tuple[bool, str]:
    p = ROOT / "scripts" / name
    if not p.is_file():
        return False, f"缺少 {name}"
    r = subprocess.run([sys.executable, str(p)], cwd=ROOT, capture_output=True, text=True)
    tail = (r.stdout + r.stderr).strip().splitlines()
    return r.returncode == 0, tail[-1] if tail else f"exit {r.returncode}"


def recall_pending() -> tuple[int, int]:
    p = ROOT / "ledger/P6_抽检召回样本.csv"
    if not p.is_file():
        return 0, -1
    rows = list(csv.DictReader(p.open(encoding="utf-8")))
    pend = sum(1 for r in rows if r.get("recall_status", "pending") == "pending")
    return len(rows), pend


def main() -> int:
    rows: list[tuple[str, bool, str]] = []
    fail = 0

    for ac, script in [
        ("AC-7.1 正式夹 D1–D6", "deliverables_audit.py"),
        ("AC-7.2 S18 渲染链接", "s18_render_check.py"),
        ("AC-6.5 数理映射", "p6_math_mapping_audit.py"),
        ("AC-6.6 应用 5 场景", "p6_app_scenarios_lint.py"),
        ("AC-6.7 滑窗重复", "p6_dup_lint.py"),
    ]:
        ok, msg = run_script(script)
        rows.append((ac, ok, msg))
        if not ok:
            fail += 1

    for ac, fn in [
        ("AC-6.9 对抗审查签收", check_signoff_table),
        ("AC-6.10 用户试用", check_trial_record),
        ("D10 批复", check_d10),
        ("P4 抽查 20 张", check_p4_sample),
        ("AC-6.8 锚点队列", check_anchor_queue),
    ]:
        msg, ok = fn()
        rows.append((ac, ok, msg))
        if not ok:
            fail += 1

    total, pend = recall_pending()
    ok63 = total > 0 and pend == 0
    rows.append(
        (
            "AC-6.3 抽检召回",
            ok63,
            f"pending {pend}/{total}" if total else "缺少样本 CSV",
        )
    )
    if not ok63:
        fail += 1

    human = ROOT / "ledger/P6_人审提交.txt"
    rows.append(
        (
            "人审提交文件",
            human.is_file(),
            human.name if human.is_file() else "未创建（可用模板/示例稿）",
        )
    )

    overall = fail == 0
    lines = [
        f"# P7 阶段验收审计（{date.today().isoformat()}）",
        "",
        f"**overall**：{'可进入 P7 签字验收' if overall else f'NOT READY（{fail} 项未过）'}",
        "",
        "| 项 | 状态 | 结论 |",
        "|---|---|---|",
    ]
    for name, ok, msg in rows:
        lines.append(f"| {name} | {'✅' if ok else '⚠️'} | {msg} |")
    lines.extend(
        [
            "",
            "人审：`make p6-human-review-full`　召回：`make p6-recall-ingest`",
            "全链：`make p7-acceptance-audit && make p7-ready-lint && make pack`",
            "",
            "复跑：`make p7-acceptance-audit`",
        ]
    )
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"p7 acceptance audit: fail={fail} → {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
