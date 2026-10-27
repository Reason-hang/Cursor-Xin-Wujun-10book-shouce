#!/usr/bin/env python3
"""P6 预检：必检议题行数、场景 lint、D10 门状态。"""
import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "drafts/p5"
MUST_CHECK_EXPECT = 112


def count_must_check_rows() -> int:
    total = 0
    for p in DRAFT.glob("D*/AC-5.8_*必检议题覆盖表.md"):
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.startswith("| D") and "必检议题" not in line and "---" not in line:
                total += 1
    return total


def main() -> int:
    mc = count_must_check_rows()
    if mc != MUST_CHECK_EXPECT:
        print(f"FAIL: 必检议题表行 {mc}，期望 {MUST_CHECK_EXPECT}")
        return 1
    r = subprocess.run([sys.executable, str(ROOT / "scripts/p5_lint_scenes.py")], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout or r.stderr)
        return 1
    gate = ROOT / "ledger/P4_D10三道门裁决.csv"
    if gate.is_file():
        rows = list(csv.DictReader(gate.open(encoding="utf-8")))
        overall = rows[0].get("overall", "unknown") if rows else "missing"
        print(f"p6 preflight: 必检 {mc}/{MUST_CHECK_EXPECT}；D10 overall={overall}")
    else:
        print(f"p6 preflight: 必检 {mc}/{MUST_CHECK_EXPECT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
