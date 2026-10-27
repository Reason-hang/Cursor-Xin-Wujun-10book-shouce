# AC-6.1–6.10 差距分析（SA-1 只读审计）

| AC | 状态 | 证据 | 下一步 |
|---|---|---|---|
| 6.1 G0–G9 | PARTIAL | selftest/gates 子集 | 接入 S15 全闸门 |
| 6.2 论点覆盖 100% | MISSING | p6_unit_coverage 仅数量 | 双向矩阵 T-P6-02 |
| 6.3 抽检召回 | MISSING | 仅 P1 试点 | P6 盲抽循环 |
| 6.4 关键词反查 | PARTIAL | logs/g10_kw.md 待登记 | 全量 kwscan + lint |
| 6.5 数理映射率 | PARTIAL | M 卡字段 5 | 全量审计脚本 |
| 6.6 应用 5 场景 | PARTIAL | `P6_应用验证场景演练_5条.md` | 链入 D4 |
| 6.7 滑窗重复 0 | **PASS** | `make p6-dup-lint` | 保持 D4 同步 |
| 6.8 锚点 100% | **PASS** | 509 合并 verify | 定期复验 |
| 6.9 对抗审查 | MISSING | — | R-AUD 五角度 |
| 6.10 用户验证 | **BLOCKED** | P4 抽查 20 张待确认 | 你签字 + 3 真实问题 |

开放：**D10 柱 A/B**；**D10 证据门 fail**；**SA-5** 快核 3 张 claim↔锚点 0/3（技术 SHA 均 PASS）。
