# P4 K 冻结差量（2026-10-28 工程收口）

| 口径 | 数量 | 说明 |
|---|---:|---|
| disposition 含 K | **579** | `make p3-disposition-audit` |
| P4 归属表行 | **585** | `ledger/P4_归属表.csv` |
| 冻结 draft K | **582** | `make p4-freeze-k`（2026-10-28） |
| x_hint_only（降级审计 open） | **3** | `ledger/K降级审计表.csv` |
| 双向矩阵 | **582**，forward_fail=0 | `make p6-bidir-matrix` |

**已执行**：补批后增量冻结 **532→582**（非人审项；κ/抽查闸门仍 PASS）。

**若你坚持验收口径=旧 532**：请明示，Agent 可回滚冻结快照并单独登记「增量 K 池」。

**仍待你**：P7 人审与召回（见 `P7_用户延后登记.md`）；D10 三道门与 L2/L3 区间（成稿阶段）。
