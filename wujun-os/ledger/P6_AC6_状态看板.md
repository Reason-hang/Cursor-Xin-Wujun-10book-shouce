# P6 AC-6 状态看板（2026-10-28）

| AC | 项 | 状态 | 证据/下一步 |
|---|---|---|---|
| 6.1 | G0–G9 全重跑 | 部分 | `make gates` + selftest 子集 |
| 6.2 | 核心论点覆盖 | 机械 PASS | `make p6-bidir-matrix`（SG1 39/386）；语义待回读 |
| 6.3 | 抽检召回 | 未闭环 | pending=130/130 → `P6_抽检召回工作册.md` |
| 6.4 | 关键词反查 | 机械达标 | `make p6-g10-refresh` |
| G10③ | SG3 划重点召回 | EXCEPTION（D6 已登记） | `P6_G10③_差距与补抽建议.md` |
| 6.5 | 数理映射 | PASS | `make p6-math-audit` 50/50 |
| 6.6 | 应用 5 场景 | PASS | `make p6-app-lint` + ledger 演练稿 |
| 6.7 | 滑窗重复 | PASS | `make p6-dup-lint` |
| 6.8 | 锚点 | PASS | `make verify-anchors` |
| 6.9 | 对抗审查 | 待签收（仍有 6 行未填 Y/N） | `P6_对抗式审查_签收表.md` |
| 6.10 | 用户试用 | 待你（3 问模板，背景已填 0/3） | `P7_人审一次填完.md` |

**阻塞 P7**：D10=已批复 A；P4 20 张；锚点=队列已修；6.9/6.10 人审。

批复：`ledger/批复落盘_复制模板.txt` → `make approvals-ingest` → `make approvals-apply`

复算：`make p6-ac6-dashboard && make p6-report`
