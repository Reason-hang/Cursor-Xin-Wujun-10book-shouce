#!/usr/bin/env python3
"""组装 D3《溯源与处置台账》v0.9 与统一锚点 ledger。"""
import csv
import hashlib
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "ledger"
OUT = ROOT / "out"
DELIVER = ROOT.parent / "最终所有交付物"
ANCHOR_PARTS = [LEDGER / "锚点表_P3a.md", LEDGER / "锚点表_P3b.md", LEDGER / "锚点表_试点.md"]


def merge_anchors() -> tuple[str, int]:
    lines = ["# 溯源与处置台账｜锚点表（P3a+P3b+试点合并）\n", "\n"]
    lines.append("| 卡ID | 书文件名 | 行起 | 行止 | 字符起 | 字符止 | SHA1 | 指纹词 |\n")
    lines.append("|---|---|---|---|---|---|---|---|\n")
    n = 0
    for path in ANCHOR_PARTS:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("| P") or line.startswith("| P1-") or line.startswith("| P3"):
                lines.append(line + "\n")
                n += 1
    merged = LEDGER / "溯源与处置台账.md"
    merged.write_text("".join(lines), encoding="utf-8")
    return "".join(lines), n


def triage_stats() -> dict:
    rows = list(csv.DictReader(LEDGER.joinpath("分诊表.csv").open(encoding="utf-8")))
    layer = Counter(r["layer"] for r in rows)
    return {"units": len(rows), "layer": dict(layer)}


def build_d3(anchor_n: int, verify_ok: bool, verify_detail: str) -> str:
    tri = triage_stats()
    p4_k = sum(1 for _ in csv.DictReader(LEDGER.joinpath("P4_归属表.csv").open(encoding="utf-8")))
    kd = sum(1 for _ in csv.DictReader(LEDGER.joinpath("K降级审计表.csv").open(encoding="utf-8"))) - 0
    return f"""# 溯源与处置台账 v0.9（P6 组装稿）

> 生成日：{date.today().isoformat()}。完整 CSV/分表在恢复包 `wujun-os/ledger/`；本文件为正式交付索引 + 锚点合并表。

## 1. 单元处置（分诊）

| 指标 | 值 |
|---|---|
| 分诊表行数 | **{tri['units']}**（`ledger/分诊表.csv`） |
| 读法层 A/B/C | {tri['layer']} |

处置率 100% 以 P0 单元清单 + 分诊表为准；P6 全量逐行嵌入待下一版脚本（避免单文件过大）。

## 2. 论点卡与归属

| 指标 | 值 |
|---|---|
| P4 归属表 K 行 | **{p4_k}**（冻结 K=493 见 `P4_K卡冻结_2026-10-27.md`） |
| 论点卡 JSON | `cards/**/*.json`（selftest：1697 张 unit_cards） |

## 3. 锚点表（合并）

| 指标 | 值 |
|---|---|
| 合并锚点行 | **{anchor_n}** |
| 统一 ledger | `ledger/溯源与处置台账.md` |
| `src_frozen` 校验 | **{'通过' if verify_ok else '失败'}** — {verify_detail} |

复验命令（在 `wujun-os/` 下）：

```bash
python3 scripts/anchor_tool.py verify --ledger ledger/溯源与处置台账.md --books-dir src_frozen
make p3a-verify-anchors && make p3b-verify-anchors
```

## 4. 其他分表（路径）

| 分表 | 文件 |
|---|---|
| K 降级审计 | `ledger/K降级审计表.csv` |
| 关系与冲突 | `ledger/P4_卡对关系表.csv`、`ledger/P4_冲突台账.csv` |
| 盲重标 κ | `ledger/P4_盲重标κ报告.md`（κ=0.839） |
| P4 抽查 20 张 | `ledger/P4_抽查20张.csv`（**Y/N 待你确认**） |

## 5. 已知缺口（P6 后续）

- A 层 **50** 单元无 JSON（见 `P4_P3产物冻结_2026-10-27.md`）
- 说话人台账、排除清单 X1–X8 独立表待 P6 全量导出
"""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    DELIVER.mkdir(parents=True, exist_ok=True)
    _, anchor_n = merge_anchors()
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/anchor_tool.py"), "verify",
         "--ledger", str(LEDGER / "溯源与处置台账.md"), "--books-dir", str(ROOT / "src_frozen")],
        capture_output=True, text=True,
    )
    detail = (proc.stdout or proc.stderr).strip().replace("\n", " ")
    verify_ok = proc.returncode == 0
    d3 = build_d3(anchor_n, verify_ok, detail)
    out_path = OUT / "溯源与处置台账_v0.9.md"
    del_path = DELIVER / "溯源与处置台账_v0.9.md"
    out_path.write_text(d3, encoding="utf-8")
    del_path.write_text(d3, encoding="utf-8")
    print(f"p6 d3: {anchor_n} anchors, verify={'OK' if verify_ok else 'FAIL'} → {out_path}")
    return 0 if verify_ok else 1


if __name__ == "__main__":
    sys.exit(main())
