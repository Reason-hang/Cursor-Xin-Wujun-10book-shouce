#!/usr/bin/env python3
"""读取 ledger/SG1_裁决.txt（A/B），登记 D6 范围或提示补批。"""
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "ledger/SG1_裁决.txt"
OUT = ROOT / "ledger/SG1_范围例外登记.md"
LOG = ROOT / "ledger/SG1_裁决执行记录.md"


def main() -> int:
    if not DECISION.is_file():
        print("skip: 无 SG1_裁决.txt（A/B）")
        return 0
    raw = DECISION.read_text(encoding="utf-8").strip().upper()
    choice = raw.replace("SG1=", "")[-1:] if raw else ""
    if choice not in ("A", "B"):
        print(f"FAIL: 无法识别 {raw!r}")
        return 1
    body = [f"# SG1 裁决执行（{choice}）\n\n日期：{date.today().isoformat()}\n\n"]
    if choice == "A":
        body.append(
            "路径 **A**：须新开 P3b 补批 SG1 高信号单元抽 K，并走 P4 变更控制；本脚本不自动抽卡。\n"
            "参考：`ledger/P6_SG1_来信1论点缺口.md`\n"
        )
    else:
        OUT.write_text(
            """# SG1 范围例外登记（选项 B）

| 项 | 声明 |
|---|---|
| 来信 1（SG1） | 仅完成分诊 + C 层壳；**无冻结 K** |
| 手册承接 | 来信类论点以 **SG3/WJ2/GG** 冻结 K 与 M 卡整合层为准 |
| AC-6.2 | **不**声称 SG1 单元级 100% 论点覆盖 |

依据：`SG1_裁决.txt` = B；`make sg1-opt-apply`。
""",
            encoding="utf-8",
        )
        body.append(f"已写 `{OUT.name}`。\n")
    LOG.write_text("".join(body), encoding="utf-8")
    print(f"sg1 opt ({choice}) → {LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
