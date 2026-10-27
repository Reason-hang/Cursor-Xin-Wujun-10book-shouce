# WJ-OS｜P1 试点卡 MVD

| 项 | 内容 |
|---|---|
| 日期 | 2026-10-27 |
| 范围 | T-P1-02～08、04：18 单元、**24 锚点**；S14、划重点召回、回归 6 组、规则 pilot-v1 |
| 选样 | 视同「开始/持续推进」确认，见 `P1_选样表.md` |

## 交付物（本文件夹）

| 文件 | 说明 |
|---|---|
| `论点卡台账_试点.md` | 20 卡台账（含 X3 游记、双出处 M、划重点 R） |
| `锚点表_试点.md` | 首轮 20 行锚点 |
| `锚点表_试点_blind2.md` | 双盲第二轮 20 行（`make p1-blind2`） |
| `试点报告_草稿.md` | AC-1.1～1.7 大部分已填 |
| `P1_划重点召回.md` | T-P1-07 100% |
| `P1_回归组判定.md` | T-P1-04 |
| `P1_试点统计.md` | T-P1-08 |
| `抽卡规则_pilot_v1.md` | T-P1-10 草案 |
| `wujun-os-pack_20261027.zip` | 恢复包（含 `cards/` 18 单元 JSON） |

## 验证

```bash
cd "/Users/lizhihang/Documents/【Cursor-projects】/Cursor-Xin-Wujun-10book-shouce/wujun-os"
make p1-verify-anchors   # 24/24
make p1-recall           # 划重点 ≥90%
make p1-blind2 && make p1-overlap
make p1-kwscan && make p1-stats
make test && make pack
```

## 进度

| 指标 | 值 |
|---|---|
| 试点单元 | 18 / 18 |
| 论点卡 | 24（含 SG3 划重点补齐） |
| AC-1.1 锚点 | 24/24 PASS |
| AC-1.3 S14 | 1.00 |
| AC-1.4 划重点 | 6/6 = 100% |

恢复包 SHA-256：`688f450808cfec00e011de8501290f10f569a38a4a02596e89f7c53b6d8822bd`

下一工单：**T-P1-09** 吞吐、**T-P1-11** 报告定稿、**T-P1-12** ST-2/3、**Gate-P1**。
