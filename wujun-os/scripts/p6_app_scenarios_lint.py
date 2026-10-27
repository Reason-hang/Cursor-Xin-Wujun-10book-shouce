#!/usr/bin/env python3
"""AC-6.6：应用验证 5 场景演练记录 lint。"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "ledger/P6_应用验证场景演练_5条.md"


def main() -> int:
    if not PATH.is_file():
        print("FAIL: 缺少 P6_应用验证场景演练_5条.md")
        return 1
    text = PATH.read_text(encoding="utf-8")
    drills = re.findall(r"^## 演练 \d+", text, re.MULTILINE)
    abnormal = len(re.findall(r"异常", text))
    passed = len(re.findall(r"走通结论[^\n]*\*\*通过", text))
    if len(drills) != 5:
        print(f"FAIL: 演练节 {len(drills)}，期望 5")
        return 1
    if abnormal < 1:
        print("FAIL: 需至少 1 条异常路径描述")
        return 1
    if passed < 5:
        print(f"FAIL: 走通结论通过数 {passed}，期望 5")
        return 1
    print(f"p6 app scenarios lint OK: 5 条，异常提及 {abnormal} 处，通过 {passed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
