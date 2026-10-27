#!/usr/bin/env python3
"""P5/P6：场景入口全局 ID 唯一且合计 46。"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "drafts/p5"
EXPECTED = 46
CHAPTER_TARGETS = {
    "D01": 6, "D02": 8, "D03": 4, "D04": 3, "D05": 4,
    "D06": 10, "D07": 4, "D08": 3, "D09": 2, "D10": 2,
}


def main() -> int:
    ids: list[str] = []
    for ch, want in CHAPTER_TARGETS.items():
        paths = list((DRAFT / ch).glob("S_*.md"))
        if not paths:
            print(f"FAIL {ch}: 无场景文件")
            return 1
        n = 0
        for p in paths:
            for line in p.read_text(encoding="utf-8").splitlines():
                if m := re.match(r"\| (S-\d{3}) \|", line):
                    ids.append(m.group(1))
                    n += 1
        if n != want:
            print(f"FAIL {ch}: 场景 {n} 条，期望 {want}")
            return 1
    if len(ids) != EXPECTED:
        print(f"FAIL: 合计 {len(ids)}，期望 {EXPECTED}")
        return 1
    if len(set(ids)) != len(ids):
        dup = [i for i in ids if ids.count(i) > 1]
        print(f"FAIL: 重复 ID {sorted(set(dup))}")
        return 1
    nums = sorted(int(i.split("-")[1]) for i in ids)
    if nums != list(range(1, EXPECTED + 1)):
        print(f"FAIL: ID 非连续 001–{EXPECTED:03d}，缺/多 {set(range(1, EXPECTED + 1)) - set(nums)}")
        return 1
    print(f"p5 scenes lint OK: {EXPECTED} 条，S-001–S-{EXPECTED:03d} 唯一连续")
    return 0


if __name__ == "__main__":
    sys.exit(main())
