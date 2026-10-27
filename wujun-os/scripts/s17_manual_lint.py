#!/usr/bin/env python3
"""S17：主手册草稿 lint（drafts/p5 下核心卡）"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "drafts/p5"
REQ = re.compile(r"^[1-9]\.\s")


def lint_file(p: Path) -> list[str]:
    t = p.read_text(encoding="utf-8")
    errs = []
    if "#### M-" not in t:
        errs.append("缺少核心卡标题")
    nums = {int(m.group(1)) for m in re.finditer(r"^(\d)\.\s", t, re.M)}
    for i in range(1, 10):
        if i not in nums:
            errs.append(f"缺字段 {i}")
    if re.search(r"[\u4e00-\u9fff]{16,}", t) and "出处" in t:
        longq = re.findall(r"「[^」]{20,}」", t)
        if longq:
            errs.append("疑似长引文")
    return errs


def main():
    files = list(DRAFT.glob("**/*.md"))
    files = [f for f in files if f.name.startswith("M-")]
    if not files:
        print("s17: 无 M- 草稿，跳过")
        return 0
    bad = 0
    for f in files:
        errs = lint_file(f)
        if errs:
            bad += 1
            print(f"FAIL {f.name}: {', '.join(errs)}")
    if bad:
        return 1
    print(f"s17 lint OK: {len(files)} 张核心卡")
    return 0


if __name__ == "__main__":
    sys.exit(main())
