#!/usr/bin/env python3
"""AC-6.4 预检：g10_kw.md 去向登记完成率。"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "logs/g10_kw.md"
OUT = ROOT / "ledger/P6_G10关键词去向统计.md"


def main() -> int:
    if not LOG.is_file():
        print("FAIL: 缺少 logs/g10_kw.md，先 make p1-kwscan")
        return 1
    pending = 0
    resolved = 0
    total = 0
    for line in LOG.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        if "书名" in line and "命中" in line:
            continue
        if "---" in line:
            continue
        total += 1
        dest = line.split("|")[-2].strip() if line.count("|") >= 6 else ""
        if not dest or dest.startswith("待 P1") or dest.startswith("待 P6") or dest == "待登记":
            pending += 1
        else:
            resolved += 1
    rate = (resolved / total * 100) if total else 0
    body = f"""# G10 关键词反查去向（AC-6.4 预检）

| 指标 | 值 |
|---|---|
| 命中行数 | {total} |
| 已登记去向 | {resolved} |
| 待处理 | {pending} |
| 完成率 | {rate:.1f}% |

**门槛**：AC-6.4 要求命中段落 100% 有去向；机械登记 **{'未达标' if pending else '达标'}**。

> 机械达标 ≠ 语义已抽 K；口径见 `ledger/P6_G10去向登记口径.md`。

复跑：`cd wujun-os && make p6-g10-refresh`
"""
    OUT.write_text(body, encoding="utf-8")
    print(f"p6 g10: {resolved}/{total} resolved ({rate:.1f}%) pending={pending} → {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
