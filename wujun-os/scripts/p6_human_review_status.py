#!/usr/bin/env python3
"""P6 人审阻塞一览（只读，不写签收/试用/recall）。"""
import csv
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "ledger/P6_人审提交.txt"
SAMPLE = ROOT / "ledger/P6_抽检召回样本.csv"
GUIDE = ROOT / "ledger/P7_人审一次填完.md"


def main() -> int:
    print("P6 人审阻塞状态（工程闸门已绿，阶段验收等人审）\n")

    if SRC.is_file():
        bad = bool(re.search(r"待填|你的姓名|替换为真名|【", SRC.read_text(encoding="utf-8"), re.I))
        print(f"  P6_人审提交.txt：存在{'（仍含模板占位，须改掉）' if bad else ''}")
    else:
        print("  P6_人审提交.txt：缺失")
        print("    cp ledger/P6_人审提交_模板.txt ledger/P6_人审提交.txt")

    subprocess.call([sys.executable, str(ROOT / "scripts/p7_human_signoff_lint.py")], cwd=ROOT)
    pre = ROOT / "ledger/P7_人审签字预检.md"
    if pre.is_file():
        m = re.search(r"\*\*overall\*\*：(.+)", pre.read_text(encoding="utf-8"))
        print(f"  人审预检：{m.group(1).strip() if m else '未知'}")

    if SAMPLE.is_file():
        rows = list(csv.DictReader(SAMPLE.open(encoding="utf-8")))
        pend = sum(1 for r in rows if r.get("recall_status", "pending") == "pending")
        print(f"  AC-6.3 recall：pending {pend}/{len(rows)}（p7-ready-lint 须 0 pending）")
        print("    工作册：ledger/P6_抽检召回工作册.md")
        print("    分批：make p6-recall-batch-init → 编辑 ledger/P6_召回批次/*.txt → make p6-recall-ingest")

    print("\n填完后：")
    print('  cd "' + str(ROOT) + '"')
    print("  make p6-human-review-full && make pack")
    print(f"  指引：{GUIDE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
