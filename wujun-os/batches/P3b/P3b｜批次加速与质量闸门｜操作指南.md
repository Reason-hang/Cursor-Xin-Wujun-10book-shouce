# P3b｜批次加速与质量闸门｜操作指南

与 P3a 相同原则：**探针 + manifest + commit + lint + 锚点校验 + pack/test**。

| 步骤 | 命令 |
|---|---|
| 装箱（已跑） | `make p3b-plan` → `batches/P3b/INDEX.md`（12 批，170 B 层单元） |
| 探针 | `make p3b-probes BATCH=B-P3b-GG-001` |
| 落盘 | `make p3b-commit MANIFEST=drafts/B-P3b-GG-001.json` |
| 收口 | `make p3b-close BATCH=B-P3b-GG-001` |

- 锚点表：`ledger/锚点表_P3b.md`
- 卡 ID：`P3b-<书码>-Uxxxx-K01`
- 书序：**GG → WJ2 → SG3**
