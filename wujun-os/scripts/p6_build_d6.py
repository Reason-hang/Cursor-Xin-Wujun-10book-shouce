#!/usr/bin/env python3
"""D6《方案决策与裁决记录》v0.9 交付副本。"""
import csv
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DELIVER = ROOT.parent / "最终所有交付物"


def _d10_row() -> str:
    p = ROOT / "ledger/D10_裁决.txt"
    if p.is_file():
        c = p.read_text(encoding="utf-8").strip().upper()
        if c in ("A", "D10=A", "B", "D10=B"):
            return f"| R-D10-01 | D10 独立第 10 柱 | 裁决 **{c.replace('D10=', '')}** | **已批复**（`make d10-apply`） |"
    return "| R-D10-01 | D10 独立第 10 柱 | **A** 保留 10 柱，证据门记 D6 例外 / **B** 9 柱并入 D08-1 | **待你**（见 `ledger/R-D10-01_裁决附件_AB对比.md`） |"


def _g10_row() -> str:
    if (ROOT / "ledger/G10③_AC例外登记.md").is_file():
        return "| R-G10-03 | SG3 划重点召回 0.51% | 已登记 AC 例外 | **已批复**（`G10③_AC例外登记.md`） |"
    return "| R-G10-03 | SG3 划重点召回 0.51% | **A** 补抽 K / **B** 重定义指标 / **C** 缩范围 | **待你**（`P6_G10③_差距与补抽建议.md`） |"


def _sg1_row() -> str:
    if (ROOT / "ledger/SG1_范围例外登记.md").is_file():
        return "| R-SG1-01 | 来信1 无冻结 K | 范围例外 B | **已批复**（`SG1_范围例外登记.md`） |"
    p = ROOT / "ledger/SG1_裁决.txt"
    if p.is_file() and p.read_text(encoding="utf-8").strip().upper() in ("A", "SG1=A"):
        return "| R-SG1-01 | 来信1 无冻结 K | **A** 补批 P3b | **已批复**（39 高信号 K 已落库；冻结 532） |"
    return "| R-SG1-01 | 来信1 无冻结 K | **A** 补批 P3b / **B** D6 缩范围声明 | **待你** |"


def _p4_row() -> str:
    if (ROOT / "ledger/P4_抽查_用户确认.txt").is_file():
        return "| R-P4-01 | P4 抽查 20 张 Y/N | 用户已确认 2026-10-28 | **已批复** |"
    return "| R-P4-01 | P4 抽查 20 张 Y/N | `ledger/P4_抽查20张.csv` | **待你** |"


def _anchor_row() -> str:
    q = ROOT / "ledger/P6_锚点修探针队列.csv"
    if not q.is_file():
        return "| R-P6-01 | 锚点↔claim 质控 | `ledger/P6_锚点修探针队列.csv`（3 条 P1） | **待你批后修锚** |"
    rows = list(csv.DictReader(q.open(encoding="utf-8")))
    done = sum(1 for r in rows if r.get("status") == "done")
    if done == len(rows) and rows:
        return f"| R-P6-01 | 锚点↔claim 质控 | 队列 {len(rows)} 条 | **已修锚**（verify 见 p6-build-d3） |"
    return "| R-P6-01 | 锚点↔claim 质控 | `ledger/P6_锚点修探针队列.csv`（3 条 P1） | **待 approved → `make p6-anchor-queue-apply`** |"


def _extra_decisions() -> str:
    lines: list[str] = []
    if (ROOT / "ledger/D10_证据门例外登记.md").is_file():
        lines.append("| 2026-10-28 | D10=A：证据门例外，保留 10 柱 | `ledger/D10_证据门例外登记.md` |")
    q = ROOT / "ledger/P6_锚点修探针队列.csv"
    if q.is_file():
        rows = list(csv.DictReader(q.open(encoding="utf-8")))
        if rows and all(r.get("status") == "done" for r in rows):
            lines.append("| 2026-10-28 | P6 锚点队列 3 条修探针（不改 claim） | J-020；`make p6-anchor-queue-apply` |")
    g = ROOT / "ledger/G10③_AC例外登记.md"
    if g.is_file():
        lines.append("| 2026-10-28 | G10③ 指标例外（缩范围/重定义） | `ledger/G10③_AC例外登记.md` |")
    s = ROOT / "ledger/SG1_范围例外登记.md"
    if s.is_file():
        lines.append("| 2026-10-28 | SG1 无 K：书面缩范围 | `ledger/SG1_范围例外登记.md` |")
    return "\n".join(lines) + ("\n" if lines else "")


def build_body() -> str:
    extra = _extra_decisions()
    return f"""# 方案决策与裁决记录 v0.9

> 更新：{date.today().isoformat()}

## 待裁决（阻塞 D1 v1.0 目录）

| ID | 议题 | 选项 | 状态 |
|---|---|---|---|
{_d10_row()}
{_p4_row()}
{_anchor_row()}
{_g10_row()}
{_sg1_row()}

## 已记录决策

| 日期 | 决策 | 依据 |
|---|---|---|
| 2026-10-27 | P5 场景 ID 按手册 D01→D10 重排为 S-001–046 | `ledger/P5_场景ID重排_手册章序.md` |
| 2026-10-27 | P5 v0.9 集成 D1/D2 至 `最终所有交付物/` | `ledger/P5_T-P5-10_集成记录.md` |
| 2026-10-27 | D10 三道门总裁决 **fail**（证据 2.36%）仍完成 P5 第 10 章过程稿 | `ledger/P4_D10三道门裁决.md` |
| 2026-10-27 | K 冻结 493；P4 κ=0.839（13 manual override） | `ledger/P4_K卡冻结_2026-10-27.md` |
| 2026-10-27 | P6 双向矩阵机械预检 PASS；抽检召回样本 130 条 | `ledger/P6_双向矩阵_机械预检.md`、`P6_抽检召回样本.csv` |
| 2026-10-27 | SG1 无 K 卡纳入冻结（范围缺口登记） | `ledger/P6_SG1_来信1论点缺口.md` |
| 2026-10-27 | B3：P3–P6 阶段追加段入库 | `prompts/phase_append_P3.md`–`P6.md` |
| 2026-10-27 | G10 去向机械 100%（5051 命中） | `make p6-g10-refresh`；口径 `ledger/P6_G10去向登记口径.md` |
| 2026-10-28 | G10③ 全量划重点召回 **0.51%（未通过）** | `make p6-sg3-highlight-recall` |
{extra}
## 变更日志

- **v0.9.1**：G10③ 全量实测；待批复清单 `ledger/P6_待你批复清单.md`。

- **v0.9**：P6 启动；D3/D4/D6 首版入 `最终所有交付物/`；EP-0 B3 自测扩至角色/阶段段/机读字典。
"""


def main() -> int:
    body = build_body()
    OUT.mkdir(parents=True, exist_ok=True)
    DELIVER.mkdir(parents=True, exist_ok=True)
    for d in (OUT, DELIVER):
        (d / "方案决策与裁决记录_v0.9.md").write_text(body, encoding="utf-8")
    print("p6 d6 → out + 最终所有交付物")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
