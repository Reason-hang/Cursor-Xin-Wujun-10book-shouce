# T-SG1-P3b｜来信1 高信号补批工单

| 字段 | 值 |
|---|---|
| 工单 ID | T-SG1-P3b |
| 触发 | `SG1_裁决.txt` = **A**（2026-10-28） |
| 范围 | 分诊表 SG1 且 `x_candidate=Y`（**39** 单元；layer 当前多为 C） |
| 不含 | 其余 347 封 C 层来信（仍 C 壳）；10 个 A 层骨架（另轨 P3a） |
| 批次 | `batches/P3b/B-P3b-SG1-*.md`；索引 `batches/P3b/INDEX_SG1_补批.md` |
| 生成 | `python3 scripts/p3b_plan_sg1_batches.py` |

## 执行步骤（变更控制）

1. **按批抽 K**：`make p3b-probes BATCH=B-P3b-SG1-001` → 成稿 `drafts/B-P3b-SG1-001.json` → `make p3b-commit` → `make p3b-close`
2. **锚点**：更新 `ledger/锚点表_P3b.md`（增量）
3. **P4 增量**：新 K 写入 `ledger/P4_归属表.csv`；重算 κ / 冻结表版本（登记 `ledger/P4_K卡冻结_*.md` 增量节）
4. **闸门**：`make gates` + `make test`；`make p6-build`；`make pack`
5. **P6**：更新双向矩阵 SG1 行；G10 去向若含新 K 则 `make p6-g10-refresh`

## 验收口径（本工单）

| AC | 说明 |
|---|---|
| 批完 39 单元 | 每单元 ≥1 张 disposition=K 且字段满足 P3b 规范 |
| P4 | SG1 冻结 K > 0；变更记录可追溯 |
| 不夸大 | D1 仍不得宣称 SG1 全量 386 单元论点覆盖 |

## 状态

| 项 | 状态 |
|---|---|
| 批次计划 | 已生成（见 INDEX_SG1_补批） |
| B-P3b-SG1-001/002/003 | **全部 close**（39 K；manifest 见 `drafts/B-P3b-SG1-*.json`） |
| P4 | 归属/L3/冻结已更新（K 冻结 **532**） |
| 待办 | P6 矩阵/G10 刷新；κ 是否补标 SG1（变更控制） |
