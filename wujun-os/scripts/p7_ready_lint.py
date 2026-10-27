#!/usr/bin/env python3
"""P7 阶段验收就绪 lint：人审预检须 0 项未过（不含 AC-6.3 recall，另查）。"""
import csv
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    subprocess.call([sys.executable, str(ROOT / "scripts/p7_human_signoff_lint.py")], cwd=ROOT)
    text = (ROOT / "ledger/P7_人审签字预检.md").read_text(encoding="utf-8")
    m = re.search(r"\*\*overall\*\*：(\d+) 项未过", text)
    fail = int(m.group(1)) if m else 99
    sample = ROOT / "ledger/P6_抽检召回样本.csv"
    if sample.is_file():
        rows = list(csv.DictReader(sample.open(encoding="utf-8")))
        pend = sum(1 for r in rows if r.get("recall_status", "pending") == "pending")
        if pend:
            print(f"p7 ready: AC-6.3 仍有 pending={pend}/130")
            fail += 1
    if fail:
        print(f"p7 ready: NOT READY（阻塞 {fail} 类）→ ledger/P7_人审签字预检.md")
        return 1
    print("p7 ready: 人审签字 + 6.3 样本已闭环（仍须你确认内容真实性）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
