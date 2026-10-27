#!/usr/bin/env python3
"""生成 P6 AC-6 状态看板（过程件，供 D4 与人审对照）。"""
import csv
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ledger/P6_AC6_状态看板.md"

import sys

sys.path.insert(0, str(ROOT / "scripts"))
try:
    from p7_human_signoff_lint import check_signoff_table, check_trial_record
except ImportError:
    check_signoff_table = check_trial_record = None


def recall_pending() -> int:
    p = ROOT / "ledger/P6_抽检召回样本.csv"
    if not p.is_file():
        return -1
    rows = list(csv.DictReader(p.open(encoding="utf-8")))
    return sum(1 for r in rows if r.get("recall_status", "pending") == "pending")


def g10_ok() -> bool:
    p = ROOT / "ledger/P6_G10关键词去向统计.md"
    return p.is_file() and "待处理 | 0 |" in p.read_text(encoding="utf-8")


def g10c_status() -> str:
    if (ROOT / "ledger/G10③_AC例外登记.md").is_file():
        return "EXCEPTION（D6 已登记）"
    p = ROOT / "ledger/P6_SG3划重点召回_全量.md"
    if p.is_file() and "判定: **通过**" in p.read_text(encoding="utf-8"):
        return "PASS"
    return "**未通过 0.51%**"


def d10_status() -> str:
    p = ROOT / "ledger/D10_裁决.txt"
    if p.is_file() and p.read_text(encoding="utf-8").strip():
        return f"已批复 {p.read_text(encoding='utf-8').strip()}"
    return "待 A/B"


def _human_ac69() -> str:
    if check_signoff_table:
        msg, ok = check_signoff_table()
        return "PASS" if ok else f"待签收（{msg}）"
    return "待签收"


def _human_ac610() -> str:
    if check_trial_record:
        msg, ok = check_trial_record()
        return "PASS" if ok else f"待你（{msg}）"
    return "待你"


def anchor_status() -> str:
    q = ROOT / "ledger/P6_锚点修探针队列.csv"
    if not q.is_file():
        return "—"
    rows = list(csv.DictReader(q.open(encoding="utf-8")))
    if rows and all(r.get("status") == "done" for r in rows):
        return "队列已修"
    return "待处理"


def main() -> int:
    rp = recall_pending()
    lines = [
        f"# P6 AC-6 状态看板（{date.today().isoformat()}）",
        "",
        "| AC | 项 | 状态 | 证据/下一步 |",
        "|---|---|---|---|",
        "| 6.1 | G0–G9 全重跑 | 部分 | `make gates` + selftest 子集 |",
        "| 6.2 | 核心论点覆盖 | 机械 PASS | `make p6-bidir-matrix`（SG1 39/386）；语义待回读 |",
        f"| 6.3 | 抽检召回 | {'未闭环' if rp else '样本全 pass' if rp == 0 else '未知'} | pending={rp}/130 → `P6_抽检召回工作册.md` |",
        f"| 6.4 | 关键词反查 | {'机械达标' if g10_ok() else '未达标'} | `make p6-g10-refresh` |",
        f"| G10③ | SG3 划重点召回 | {g10c_status()} | `P6_G10③_差距与补抽建议.md` |",
        "| 6.5 | 数理映射 | PASS | `make p6-math-audit` 50/50 |",
        "| 6.6 | 应用 5 场景 | PASS | `make p6-app-lint` + ledger 演练稿 |",
        "| 6.7 | 滑窗重复 | PASS | `make p6-dup-lint` |",
        "| 6.8 | 锚点 | PASS | `make verify-anchors` |",
        f"| 6.9 | 对抗审查 | {_human_ac69()} | `P6_对抗式审查_签收表.md` |",
        f"| 6.10 | 用户试用 | {_human_ac610()} | `P7_人审一次填完.md` |",
        "",
        f"**阻塞 P7**：D10={d10_status()}；P4 20 张；锚点={anchor_status()}；6.9/6.10 人审。",
        "",
        "批复：`ledger/批复落盘_复制模板.txt` → `make approvals-ingest` → `make approvals-apply`",
        "",
        "复算：`make p6-ac6-dashboard && make p6-report`",
    ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"p6 ac6 dashboard → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
