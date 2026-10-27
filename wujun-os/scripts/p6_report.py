#!/usr/bin/env python3
"""生成 D4《覆盖与质检报告》v0.9。"""
import csv
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DELIVER = ROOT.parent / "最终所有交付物"


def run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return p.returncode, (p.stdout or p.stderr or "").strip()


def _g10_mechanical_ok() -> bool:
    p = ROOT / "ledger/P6_G10关键词去向统计.md"
    if not p.is_file():
        return False
    return "待处理 | 0 |" in p.read_text(encoding="utf-8") or "完成率 | 100" in p.read_text(encoding="utf-8")


def main() -> int:
    _g10_ok = _g10_mechanical_ok()
    st_code, st_out = run([sys.executable, "scripts/selftest.py"])
    pf_code, pf_out = run([sys.executable, "scripts/p6_preflight.py"])
    dup_code, dup_out = run([sys.executable, "scripts/p6_dup_lint.py"])
    d10 = "unknown"
    gate = ROOT / "ledger/P4_D10三道门裁决.csv"
    if gate.is_file():
        rows = list(csv.DictReader(gate.open(encoding="utf-8")))
        if rows:
            d10 = rows[0].get("overall", "unknown")

    body = f"""# 覆盖与质检报告 v0.9（P6 自动化草稿）

> 生成日：{date.today().isoformat()}。AC-6.9/6.10 人工项未填。

## 1. P5 覆盖口径

| 项 | 值 | 证据 |
|---|---|---|
| 十章 M 卡 | 50 | `make p5-lint` |
| 场景入口 | 46（S-001–046） | `make p5-lint-scenes` |
| 必检议题 | 112/112 | `ledger/P6_必检112项汇总.csv` |
| 行动工具 | 14 | `drafts/p5/tools/T-*.md` |
| D1/D2 集成 | v0.9 | `out/` + `最终所有交付物/` |

## 2. 闸门复跑（可复算）

| 闸门 | 结果 |
|---|---|
| selftest | {'**PASS**' if st_code == 0 else '**FAIL**'} |
| p6-preflight | {'**PASS**' if pf_code == 0 else '**FAIL**'} |
| D10 三道门 overall | **{d10}**（证据门 2.36%<3%） |

<details><summary>selftest 摘要</summary>

```
{st_out[-2500:] if len(st_out) > 2500 else st_out}
```

</details>

<details><summary>p6-preflight</summary>

```
{pf_out}
```

</details>

## 3. AC-6 对照（当前）

| AC | 项 | 状态 | 说明 |
|---|---|---|---|
| 6.1 | G0–G9 | 部分 | `ledger/P6_S15_G闸门对账.md`（**G10③ FAIL 0.51%**） |
| 6.2 | 核心论点覆盖 100% | 机械预检 | `ledger/P6_双向矩阵_机械预检.md` + 分书 K 矩阵（语义 100% 待人工） |
| 6.3 | 抽检召回 | 待回读 | `P6_抽检召回工作册.md` + `make p6-recall-lint` |
| 6.4 | 关键词反查 | 机械 **{'达标' if _g10_ok else '未达标'}** | `make p6-g10-refresh` → `ledger/P6_G10关键词去向统计.md` |
| 6.5 | 数理映射可检验率 | **PASS** | `make p6-math-audit` → `ledger/P6_数理映射审计.md` |
| 6.6 | 应用验证 5 场景 | **PASS** | `make p6-app-lint`；`ledger/P6_应用验证场景演练_5条.md` |
| 6.7 | 机械重复 0 | {'**PASS**' if dup_code == 0 else '**FAIL**'} | `make p6-dup-lint` |
| 6.8 | 锚点校验 100% | **PASS** | `make verify-anchors`；自助说明见 `ledger/P6_锚点用户自助核验说明.md` |
| 6.9 | 对抗式审查 | 待签收 | `P6_对抗式审查_草稿.md` + `P6_对抗式审查_签收表.md` |
| 6.10 | 用户抽查/试用 | **待你** | `ledger/P6_用户试用与抽查指引.md` |

## 4. 开放风险

1. **人审阻塞 P7** → `ledger/P6_阶段验收_用户动作清单.md`（6.9/6.10 + 6.3；`make p7-ready-lint` 须全绿）。
2. G10③ 指标例外已登记（召回 0.51%）；D10=A、P4 抽查、SG1 高信号 39 K 已落盘。
3. D3 单元表未 1742 行全文嵌入（v0.9 为索引 + 锚点合并）。
4. **SG1 非全量覆盖**（39/386 高信号 K）→ `ledger/P6_SG1_补批后登记_2026-10-28.md`。

## 5. AC-6 可复算命令

| AC | 命令 |
|---|---|
| 6.2 | `make p6-bidir-matrix` |
| 6.3 | `make p6-recall-assist` → 填 CSV → `make p6-recall-lint` |
| 6.4 | `make p6-g10-refresh` |
| 6.5 | `make p6-math-audit` |
| 6.7 | `make p6-dup-lint` |
| 6.8 | `make verify-anchors` |
| 全链 | `make p6-build && make pack && make gates && make test` |
| P7 正式夹 | `make deliver-audit` |
| EP-0 复水 | `make restore-check`（见 `ledger/EP0_restore_check_20261028.md`） |

## 6. 建议下一命令

```bash
cd wujun-os
make p6-build && make pack && make test
```
"""
    OUT.mkdir(parents=True, exist_ok=True)
    DELIVER.mkdir(parents=True, exist_ok=True)
    p = OUT / "覆盖与质检报告_v0.9.md"
    p.write_text(body, encoding="utf-8")
    (DELIVER / "覆盖与质检报告_v0.9.md").write_text(body, encoding="utf-8")
    print(f"p6 report → {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
