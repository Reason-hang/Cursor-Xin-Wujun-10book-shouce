#!/usr/bin/env python3
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "ledger/P4_盲重标κ报告.md"
SAMPLE = ROOT / "ledger/P4_盲重标样本.csv"


def main():
    if not REPORT.is_file() or not SAMPLE.is_file():
        print("缺少盲重标产物，先 make p4-blind-kappa")
        return 1
    text = REPORT.read_text(encoding="utf-8")
    m = re.search(r"κ（L1 柱）\s*\|\s*\*\*([0-9.]+)\*\*", text)
    if not m:
        print("无法解析 κ")
        return 1
    k = float(m.group(1))
    n = sum(1 for _ in open(SAMPLE, encoding="utf-8")) - 1
    if n < 60:
        print(f"样本不足 60: {n}")
        return 1
    manual_col = "primary_blind_manual" in open(SAMPLE, encoding="utf-8").readline()
    if k < 0.6:
        msg = f"κ_L1={k:.3f}<0.6"
        if not manual_col:
            print(f"WARN: {msg}（先 make p4-apply-blind-manual）")
            return 0
        print(f"FAIL: {msg}（AC-4.4 未过，勿冻结 K）")
        return 1
    print(f"P4 blind kappa lint OK: n={n} κ={k:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
