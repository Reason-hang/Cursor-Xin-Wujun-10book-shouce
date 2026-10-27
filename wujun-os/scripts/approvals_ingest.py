#!/usr/bin/env python3
"""将 `ledger/用户批复_原文.txt` 解析为各裁决文件（不执行 d10-apply）。"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "ledger/用户批复_原文.txt"


def write(path: Path, body: str) -> None:
    path.write_text(body.strip() + "\n", encoding="utf-8")
    print(f"  → {path.relative_to(ROOT)}")


def main() -> int:
    if not SRC.is_file() or not SRC.read_text(encoding="utf-8").strip():
        print("skip: 编辑 ledger/用户批复_原文.txt 后重跑（见 ledger/批复落盘_复制模板.txt）")
        return 0
    text = SRC.read_text(encoding="utf-8")
    got = 0
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        u = line.upper().replace(" ", "")
        if re.match(r"D10=A", u):
            write(ROOT / "ledger/D10_裁决.txt", "A")
            got += 1
        elif re.match(r"D10=B", u):
            write(ROOT / "ledger/D10_裁决.txt", "B")
            got += 1
        elif "G10" in u and re.search(r"[③3]=C|G10③C|G10=C", u):
            write(ROOT / "ledger/G10③_裁决.txt", "C")
            got += 1
        elif "G10" in u and re.search(r"[③3]=B|G10③B|G10=B", u):
            write(ROOT / "ledger/G10③_裁决.txt", "B")
            got += 1
        elif "G10" in u and re.search(r"[③3]=A|G10③A|G10=A", u):
            write(ROOT / "ledger/G10③_裁决.txt", "A")
            got += 1
        elif re.match(r"SG1=B", u):
            write(ROOT / "ledger/SG1_裁决.txt", "B")
            got += 1
        elif re.match(r"SG1=A", u):
            write(ROOT / "ledger/SG1_裁决.txt", "A")
            got += 1
        elif re.search(r"P4.*确认|抽查确认", line, re.I):
            write(ROOT / "ledger/P4_抽查_用户确认.txt", line)
            got += 1
    if not got:
        print("FAIL: 未识别任何批复行（需 D10=A 等，见批复落盘_复制模板.txt）")
        return 1
    print(f"approvals ingest: {got} 条 → 下一步 make approvals-apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
