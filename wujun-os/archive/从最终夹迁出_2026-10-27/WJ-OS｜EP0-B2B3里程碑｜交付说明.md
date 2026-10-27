# WJ-OS｜EP-0 + B2/B3 里程碑交付说明

| 项 | 内容 |
|---|---|
| 日期 | 2026-10-27 |
| 范围 | 恢复校验、批次 2（v2.1 增补）、批次 3（机读字典与角色提示词）、EP-0 局部基建 |
| 不含 | P0–P7 手册六件套（D1–D6）、单元处置与论点卡（尚未开始） |

## 本文件夹内容

| 文件 | 说明 |
|---|---|
| `wujun-os-pack_20261027.zip` | 恢复包 v1.1（47 项清单，不含 `src_frozen` 原文；需自备 10 本书 zip） |
| 本文 | 里程碑验收与复现命令 |

## 复现校验（在新环境）

```bash
cd "/Users/lizhihang/Documents/【Cursor-projects】/Cursor-Xin-Wujun-10book-shouce"
unzip -o "最终所有交付物/wujun-os-pack_20261027.zip" -d .
cd wujun-os
cp "../【打包吴军10本电子书_副本.zip" "./_打包吴军10本电子书.zip"
make restore-check   # 冻结 + 探测 107 项 + selftest
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt -q
.venv/bin/python scripts/validate_pillars.py
make test
```

## 本里程碑新增/更新工件（在包内 `wujun-os/`）

- `spec/v2.1_增补.md`（B2）
- `spec/pillars.yaml`、`spec/exclusions.yaml`、`spec/boundary_rules.md`、`spec/schemas/pillar_schema.json`（B3）
- `prompts/R-*.md`、`prompts/phase_append_P0–P2.md`（T-00-07）
- `scripts/gates.py`、`scripts/validate_pillars.py`、`tests/test_gates_smoke.py`（T-00-04 骨架）
- `scripts/selftest.py`（修复临时目录只读副本导致 PermissionError）
- `scripts/pack.py`（排除 `.venv` 与根目录 zip）
- `state/state.json` 更新至 EP-0 进行中

## 验证结果（2026-10-27）

| 检查项 | 结果 |
|---|---|
| `verify_pack` | 46 项，0 缺失，0 被改 |
| `s00_freeze` + 哈希 | 10/10 |
| `s01_probe` 基线 | 107 项，0 不一致；单元 1742 |
| `make test` / selftest | 7/7 PASS |
| `validate_pillars` | L1=10，L2=25 PASS |

## 下一步（仍在 EP-0）

1. T-00-03：实现 S02–S08 脚本
2. T-00-05：`make_handover` 从 state 渲染交接文档
3. T-00-08：ST-1/4/5/6 压力测试干跑报告
4. 书面确认 §7 ★1–★6 后进入 P0（T-P0-01）

## 恢复包 SHA-256

见打包当日终端输出；当前文件：

`1543241c035dac57e6e4ab82c6e5eb90307525704577b7240d7c001f35294afc`
