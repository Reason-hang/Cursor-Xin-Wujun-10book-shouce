#!/usr/bin/env python3
"""读取 ledger/G10③_裁决.txt（A/B/C），登记 D6 例外或提示补抽路径。"""
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "ledger/G10③_裁决.txt"
OUT = ROOT / "ledger/G10③_AC例外登记.md"
LOG = ROOT / "ledger/G10③_裁决执行记录.md"


def main() -> int:
    if not DECISION.is_file():
        print("skip: 无 G10③_裁决.txt（A/B/C）")
        return 0
    raw = DECISION.read_text(encoding="utf-8").strip().upper()
    choice = raw.replace("G10③=", "").replace("G10=", "")[-1:] if raw else ""
    if choice not in ("A", "B", "C"):
        print(f"FAIL: 无法识别 {raw!r}")
        return 1
    body = [f"# G10③ 裁决执行（{choice}）\n\n日期：{date.today().isoformat()}\n\n"]
    if choice == "A":
        body.append("路径 **A**：须 P3b 补抽 SG3 K 后重跑 `make p6-sg3-highlight-recall`（本脚本不自动抽卡）。\n")
        rc = 0
    elif choice == "B":
        OUT.write_text(
            """# G10③ AC 指标重定义（选项 B）

| 原 AC | 调整 |
|---|---|
| SG3 划重点要点 → 冻结 K 锚点段召回 ≥95% | 改为：要点 → **G10 去向（P5 M 章）** + 每章 **5 条** spot check |

须更新 D4 AC-6.1 表述并由 R-AUD 签字。复跑：待 `p6_sg3_highlight_recall.py` 口径开关实现。
""",
            encoding="utf-8",
        )
        body.append(f"已写 `{OUT.name}`（指标重定义留痕）。\n")
        rc = 0
    else:
        OUT.write_text(
            """# G10③ AC 范围例外（选项 C）

来信 3「划重点」块以 **场景 S-xxx / 工具 T-xx** 与 M 卡整合层覆盖为准；
**不**要求每条划重点对齐冻结 K 锚点段（与成书 A 层口径分叉）。

G10③ 脚本结果 0.51% 记为 **已知例外**；P7 验收须本文件 + D6 已记录决策。
""",
            encoding="utf-8",
        )
        body.append(f"已写 `{OUT.name}`（缩范围例外）。\n")
        rc = 0
    LOG.write_text("".join(body), encoding="utf-8")
    print(f"g10 opt ({choice}) → {LOG}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
