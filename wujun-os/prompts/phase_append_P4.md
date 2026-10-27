# 阶段追加段｜P4 聚类与冻结

> **用法**：粘贴于开场提示词之后；聚类/归属以 R-ORCH + R-AUD 为主；规格：`spec/v2_方案.md` §15.5.5、`spec/工程化总纲.md` T-P4-*。

## 本阶段目标

概念键归一 → 关系标注 → 支柱归属 → L2/L3 定稿 → **D10 三道门** → K 卡冻结（分母锁定）→ 双盲 κ → 抽查 20 张表。

## 执行要点

1. 机读字典以 `spec/pillars.yaml` / `exclusions.yaml` 为准；变更走 §15.13。
2. D10 未过不得宣称「第 10 柱定稿」；须在 D6 留裁决记录。
3. `make p4-freeze-k` 后改 K 须走变更控制。
4. AC-4.8：抽查 20 张由 **用户** 填 Y/N（≤3 错）。

## 输出

`ledger/P4_*`、`data/k_card_freeze.json`、`rules/concept_keys.csv`（同步正式夹 D5 旁 concept_keys 副本）。
