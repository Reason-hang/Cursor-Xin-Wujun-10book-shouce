# EP-0｜restore-check 实测（2026-10-28）

```bash
cd wujun-os
make restore-check   # verify-pack → freeze → probe → test → status
```

| 步骤 | 结果 |
|---|---|
| verify_pack | PASS（复跑前清单一致） |
| freeze（G0） | 完成 → `logs/g0_inputs.md` |
| probe（G1–G8 基线） | 107 项不一致 0；1742 单元 |
| selftest | 全 PASS（含 EP-0 B3、P6、P7 S18） |
| status | 渲染 OK |

完整日志：`logs/restore_check_20261028.log`

**复水测验题库**：`spec/quiz.md`（ST-1 冷启动 ≥11/12，见 `logs/ST_dry_run_20261027.md`）。

收工前：`make pack`（freeze 后须刷新 MANIFEST）。
