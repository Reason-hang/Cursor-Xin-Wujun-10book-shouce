#!/usr/bin/env python3
"""核对「最终所有交付物」与 out/ 正式 D 件是否齐全、字节一致。"""
import hashlib
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DELIVER = ROOT.parent / "最终所有交付物"
REPORT = ROOT / "ledger/P7_正式夹审计.md"

REQUIRED = [
    ("D1", "认知与行动操作系统_主手册_v0.9.md", None),
    ("D2", "行动工具集_v0.9.md", None),
    ("D3", "溯源与处置台账_v0.9.md", OUT / "溯源与处置台账_v0.9.md"),
    ("D4", "覆盖与质检报告_v0.9.md", OUT / "覆盖与质检报告_v0.9.md"),
    ("D5", "00_内容盘点与单元清单.md", None),
    ("D6", "方案决策与裁决记录_v0.9.md", OUT / "方案决策与裁决记录_v0.9.md"),
]


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def main() -> int:
    rows = []
    fail = 0
    for label, name, mirror in REQUIRED:
        dp = DELIVER / name
        if not dp.is_file():
            rows.append((label, name, "MISSING", "—", "—"))
            fail += 1
            continue
        d_sha = sha(dp)
        note = "OK"
        if mirror and mirror.is_file():
            if sha(mirror) != d_sha:
                note = "与 out/ 不一致"
                fail += 1
        rows.append((label, name, "存在", d_sha, note))
    packs = sorted(DELIVER.glob("wujun-os-pack_*.zip"))
    pack_note = f"{len(packs)} 个" + (f"（最新 {packs[-1].name}）" if packs else "（缺失）")
    if len(packs) > 1:
        pack_note += f"；旧包可迁出：`{', '.join(p.name for p in packs[:-1])}`"
    if not packs:
        fail += 1
    body = [
        f"# P7 正式夹审计（{date.today().isoformat()}）",
        "",
        f"**路径**：`{DELIVER}`",
        "",
        f"**overall**：{'PASS' if fail == 0 else f'FAIL（{fail}）'}",
        "",
        "| D# | 文件 | 状态 | SHA256[:16] | 对账 |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        body.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} |")
    body.extend(["", f"**恢复包**：{pack_note}", "", "复跑：`make deliver-audit`"])
    REPORT.write_text("\n".join(body) + "\n", encoding="utf-8")
    print(f"deliver audit: fail={fail} → {REPORT}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
