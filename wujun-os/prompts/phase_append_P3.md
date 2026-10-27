# 阶段追加段｜P3 抽卡（P3a 成书 / P3b 来信）

> **用法**：粘贴于 `handover/开场提示词.md` 之后；抽卡加载 `prompts/R-EXT.md`；批次关闭由 R-ORCH 跑 lint/锚点/pack。规格：`spec/v2_方案.md` §15.5.4–§15.5.5。

## 本阶段目标

按批次对内容单元抽 **论点卡（K）**、生成 **锚点**、落 `cards/<书码>/`；P3a 六本成书 → M2（v0.3）；P3b 来信/问答 → M3（v0.7）。单元处置率 100%，锚点校验 100%。

## 主角色

| 角色 | 职责 |
|---|---|
| R-EXT | 探针、claim、锚点草稿、卡面字段 |
| R-ORCH | 批次 manifest、`p3a-close` / `p3b-close`、Gate-P3a/P3b |
| R-AUD | 抽检、盲重标（**全新窗口**） |

## 执行要点

1. 只读 `src_frozen/` 与工单 manifest；不改冻结原文。
2. 每批：`probes` → 人工填 claim → `commit` → `lint` → `verify-anchors` → `pack` → `test`。
3. C 层壳允许空 `cards[]`；K 须锚点 + 字段齐。
4. 系列单元成组处置；跨单元论点各记锚点。
5. 里程碑：P3a 后重点三柱初稿；P3b 后 10 柱初版与能力速查 v0.7。

## 停线条件

锚点 verify 失败、lint 失败、manifest 与分诊表不一致 → 写异常报告，不静默跳过。
