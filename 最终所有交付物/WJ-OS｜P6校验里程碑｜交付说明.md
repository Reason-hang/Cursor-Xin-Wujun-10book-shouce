# WJ-OS｜P6 校验里程碑｜交付说明

> 更新：2026-10-28。正式夹 **D1–D6 + 恢复包**；过程件在 `wujun-os/ledger/`。

## 本里程碑已交付（正式夹）

| 类型 | 文件 |
|---|---|
| D1/D2 | 认知与行动操作系统_主手册_v0.9.md、行动工具集_v0.9.md |
| D3/D4/D6 | 溯源与处置台账_v0.9.md、覆盖与质检报告_v0.9.md、方案决策与裁决记录_v0.9.md |
| D5 | 00_内容盘点与单元清单.md |
| 恢复包 | **wujun-os-pack_20261028.zip**（`make pack` 自动同步） |
| 演练摘要 | P6_应用验证场景演练_5条.md |

## 复水与闸门

```bash
cd wujun-os
make restore-check
make p6-build && make p7-preflight && make p7-acceptance-audit && make pack && make test
```

说明：`wujun-os/ledger/P7_阶段验收前一键命令.md`、`P6_阶段验收_用户动作清单.md`。K 冻结 **663**（含 SG1 高信号 48 等；历史 532/493 见 `P4_K冻结差量_待批复.md`）。

## AC-6 快照（机械项）

| 项 | 状态 |
|---|---|
| 6.4 G10① 去向 | 机械 100% |
| 6.5 / 6.6 / 6.7 / 6.8 | PASS |
| 6.2 | 机械双向矩阵 PASS；语义靠 6.3 回读 |
| **G10③ 划重点** | **EXCEPTION**（0.51%；`G10③_AC例外登记.md`） |
| **6.9 / 6.10 / 6.3** | **待你** → `P6_阶段验收_用户动作清单.md` |

看板：`wujun-os/ledger/P6_AC6_状态看板.md`　合一审计：`make p7-acceptance-audit`

## 阶段验收通过后

`make p7-ready-lint` PASS → `make p7-closeout`（写入 `WJ-OS｜P7阶段验收｜交付说明.md` 并 pack）。

## 未达 P7 的硬阻塞

AC-6.9 签收、AC-6.10 试用、AC-6.3 召回（`p7-ready-lint` 须 0 pending）。
