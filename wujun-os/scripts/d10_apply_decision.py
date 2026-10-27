#!/usr/bin/env python3
"""读取 ledger/D10_裁决.txt（单行 A 或 B），执行对应工程清单并登记。"""
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "ledger/D10_裁决.txt"
LOG = ROOT / "ledger/D10_裁决执行记录.md"
CHECK_A = ROOT / "ledger/D10_A_裁决后工程清单.md"
CHECK_B = ROOT / "ledger/D10_B_裁决后工程清单.md"


def read_choice() -> str | None:
    if not DECISION.is_file():
        return None
    raw = DECISION.read_text(encoding="utf-8").strip().upper()
    if raw in ("A", "D10=A"):
        return "A"
    if raw in ("B", "D10=B"):
        return "B"
    print(f"FAIL: D10_裁决.txt 内容无法识别: {raw!r}")
    return None


def main() -> int:
    choice = read_choice()
    if not choice:
        print("skip: 无 ledger/D10_裁决.txt，等待你写入 A 或 B")
        return 0
    checklist = CHECK_A if choice == "A" else CHECK_B
    body = [
        f"# D10 裁决执行记录（{choice}）\n",
        f"\n日期：{date.today().isoformat()}\n",
        f"\n依据：`D10_裁决.txt` = **{choice}**\n",
        f"\n清单：`{checklist.name}`\n",
        "\n## 自动步骤\n",
    ]
    steps: list[tuple[str, list[str]]] = [
        ("p5-assemble", ["make", "p5-assemble"]),
        ("p6-build", ["make", "p6-build"]),
        ("p6-report", ["make", "p6-report"]),
        ("p6-s15-g-audit", ["make", "p6-s15-g-audit"]),
        ("pack", ["make", "pack"]),
    ]
    if choice == "A":
        exc = ROOT / "ledger/D10_证据门例外登记.md"
        exc.write_text(
            """# D10 证据门例外登记（R-D10-01 选项 A）

| 项 | 内容 |
|---|---|
| 裁决 | **保留第 10 柱**（L1=10 不变） |
| 三道门 | 证据门实测 **2.36% < 3%**（见 `ledger/P4_D10三道门裁决.md`） |
| 处理 | 主手册保留 D10 章与 P5 过程稿；**对外宣称十柱时须附本例外** |
| 复核 | P7 前由 R-AUD 抽检 D10 主归属 K ≥23 张 |

依据：`D10_裁决.txt` = A；`make d10-apply` 自动生成。
""",
            encoding="utf-8",
        )
        body.append(f"\n- 已写 `{exc.name}`\n")
    if choice == "B":
        body.append("\n> **B 路径**：目录迁移、L1=9、场景改挂等须按清单人工/脚本逐条完成；本脚本仅串联 assemble/build/pack。\n")
    fail = 0
    for name, cmd in steps:
        rc = subprocess.call(cmd, cwd=ROOT)
        body.append(f"- `{name}`: {'OK' if rc == 0 else f'FAIL rc={rc}'}\n")
        if rc:
            fail += 1
    LOG.write_text("".join(body), encoding="utf-8")
    print(f"d10 apply ({choice}): fail={fail} → {LOG}")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
