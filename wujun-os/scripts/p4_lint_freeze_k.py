#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
J = ROOT / "data/k_card_freeze.json"


def main():
    if not J.is_file():
        print("先 make p4-freeze-k")
        return 1
    d = json.loads(J.read_text(encoding="utf-8"))
    if d.get("kappa_L1", 0) < 0.6:
        print("FAIL: freeze 时 κ 不足")
        return 1
    if d.get("spot_check_errors", 99) > 3:
        print("FAIL: 抽查归属错>3")
        return 1
    print(f"P4 freeze lint OK: K={d.get('k_cards_frozen')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
