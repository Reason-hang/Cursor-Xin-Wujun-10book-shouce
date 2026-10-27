#!/usr/bin/env python3
"""T-P6-05 预检：SG3 单元「划重点」块数量（全量召回未跑）。"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ledger/P6_SG3划重点召回_预检.md"


def main() -> int:
    src = ROOT / "src_frozen"
    book = next(src.glob("*来信3*"), None)
    if not book:
        print("FAIL: 无来信3 冻结文件")
        return 1
    text = book.read_text(encoding="utf-8")
    hl = len(re.findall(r"^###\s+划重点\s*$", text, re.MULTILINE))
    body = f"""# SG3 划重点召回（T-P6-05 预检）

| 项 | 值 |
|---|---|
| 源文件 | `{book.name}` |
| 「### 划重点」块数 | **{hl}** |
| AC 门槛 | ≥95% 要点有去向（**未在本脚本验证**） |
| 试点证据 | `ledger/P1_划重点召回.md`（P1 样本） |

**下一步**：全量召回需扩展 `p1_highlight_recall.py` 至 SG3 全单元 + 对照 493 K；当前标 **MISSING**（见 `P6_S15_G闸门对账.md` G10③）。

复跑：`python3 scripts/p6_sg3_highlight_status.py`
"""
    OUT.write_text(body, encoding="utf-8")
    print(f"p6 sg3 highlight: blocks={hl} → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
