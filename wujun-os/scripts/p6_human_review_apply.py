#!/usr/bin/env python3
"""用户填完 AC-6.9/6.10 后落盘：校验 → 登记 → 刷新看板与 D4 过程稿。"""
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from p7_human_signoff_lint import check_signoff_table, check_trial_record

OUT = ROOT / "ledger/P6_AC6_人审落盘记录.md"


def main() -> int:
    s_msg, s_ok = check_signoff_table()
    t_msg, t_ok = check_trial_record()
    if not s_ok or not t_ok:
        print("FAIL: 人审未齐")
        print(f"  6.9: {s_msg}")
        print(f"  6.10: {t_msg}")
        print("填法见 ledger/P7_人审一次填完.md")
        return 1
    OUT.write_text(
        "\n".join(
            [
                f"# P6 AC-6.9 / 6.10 人审落盘（{date.today().isoformat()}）",
                "",
                f"| AC-6.9 | PASS | {s_msg} |",
                f"| AC-6.10 | PASS | {t_msg} |",
                "",
                "证据：`P6_对抗式审查_签收表.md`、`P6_用户试用记录.md`",
                "",
                "下一步：`make p6-report && make p7-ready-lint && make pack`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"人审落盘 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
