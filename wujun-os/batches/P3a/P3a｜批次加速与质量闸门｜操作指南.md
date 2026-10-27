# P3a｜批次加速与质量闸门｜操作指南

> P3b/P4–P6 复用同一原则：**机器做可脚本复验的事，人/Agent 只做主张与批末回顾**；验收口径不变（AC-3.x、HC-11/14、`make test`）。

## 1. 结论（推荐方案）

**采用「探针自动化 + manifest 落盘 + 卡面 lint + 既有闸门」流水线**（`scripts/p3a_batch.py` + `make p3a-*`），替代每批手写 `_xx_batch.py`。

| 维度 | 一次性脚本（旧） | 加大批次 | 多 Agent 并行写卡 | **manifest 流水线（推荐）** |
|---|---|---|---|---|
| 提速 | 低（重复造轮子） | 中（少次交接） | 高 | **高（探针/落盘自动化）** |
| 质量风险 | 中（探针/指纹手误） | **高**（疲劳、回顾变薄） | **高**（claim 漂移） | **低**（锚点+lint+test 不变） |
| 验收对齐 | 是 | 否（违 HC-14） | 仅当合并后全量闸门 | **是** |
| 额度中断恢复 | 差 | 差 | 中 | **好**（manifest 可续作） |
| P3b 复用 | 否 | 否 | 部分 | **是**（改 ledger 路径即可扩展） |

不推荐：跳过锚点、跳过批末回顾、省略 `S-P3a-*` 书级回顾、或降低 `make test` 范围——这些都不满足交接 §10.5 / AC-3。

## 2. 质量门槛（不可降）

| 闸门 | 命令 | 证明什么 |
|---|---|---|
| 锚点位置真实 | `make p3a-verify-anchors` | SHA1/行号/指纹（HC-11） |
| 卡与分诊一致 | `make test`（s09/p2/status/pack） | 1697 单元壳、分诊规则 |
| 卡面字段 | `make p3a-lint BATCH=…` | speaker/claim/type/pillar/card_id |
| 主张质量 | **不脚本化** | Agent 读单元正文写 claim；批末回顾概念键 |
| 里程碑 | 每书 `S-P3a-{书码}` + 台账 + pack | v2.1 §4.3 MVD |

## 3. 单批标准作业（P3a）

```bash
cd "/Users/lizhihang/Documents/【Cursor-projects】/Cursor-Xin-Wujun-10book-shouce/wujun-os"

# ① 机器：探针+指纹草稿（不写 claim）
make p3a-probes BATCH=B-P3a-GJ-003

# ② 人/Agent：复制 probes.json → 同名 .json，补全 claim/type/pillar_hints；errors 须为空
# ③ 机器：写 cards + 锚点表
make p3a-commit MANIFEST=drafts/B-P3a-GJ-003.json

# ④ 批末回顾 + state/台账（仍须 Agent 写 md）
# ⑤ 收口闸门
make p3a-close BATCH=B-P3a-GJ-003
# 若 commit 已做过可: make p3a-lint BATCH=... && make p3a-verify-anchors && make test && make pack
```

`manifest` 单元字段：`unit_id`, `probe`, `words`, `claim`, `type`, `pillar_hints`（可选 `capability_tags`）。

## 4. P3b / 后续阶段怎么加速

| 阶段 | 可自动化 | 仍须人审 |
|---|---|---|
| **P3b** | 探针（来信/问答单元）、锚点校验、卡面 lint；复用 `p3a_shared` 探针逻辑 | B 层 claim、划重点召回（`make p1-recall` 类）、双出处 M 卡 |
| **P4** | 指纹/TF-IDF 候选（`s14_overlap`）、pillar 格式校验 | 概念键归一、κ 盲重标、冲突裁决 |
| **P5–P6** | 溯源矩阵反查、孤立节点脚本（G9） | 手册文体、三章重点倾斜（HC-17） |

**并行策略**：同一批次内可拆「探针子集 / claim 子集」给多 Agent，但**合并前**必须整批 `p3a-close`；禁止多批同时改 `锚点表_P3a.md`。

## 5. 辅助工具

| 工具 | 作用 |
|---|---|
| `scripts/p3a_batch.py` | probes / commit / lint |
| `scripts/p3a_unit_draft.py` | 单单元探针试跑 |
| `make p3a-plan` | 重新装箱（一般不需重跑） |
| `make pack` | 每批快照（R-3） |

---

**本质**：提速靠「把重复劳动沉到脚本 + manifest 续作」，质量靠「锚点与 test 不缩水 + claim 仍由读懂原文的 Agent 写」；P3b 起复制同一模式即可。
