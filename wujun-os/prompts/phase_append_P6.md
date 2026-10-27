# 阶段追加段｜P6 校验

> **用法**：粘贴于开场提示词之后；审计加载 `prompts/R-AUD.md`（**全新窗口**）。规格：`spec/v2_方案.md` §9.7、§15.5.7。

## 本阶段目标

重跑闸门 subset；AC-6.1–6.10 逐项留证；产出 D3/D4/D6 v0.9 入 `最终所有交付物/`（过程件在 `ledger/`）。

## 可复算命令

```bash
cd wujun-os
make p6-build && make pack && make gates && make test
make verify-anchors   # 对照 ledger/溯源与处置台账.md
```

## 执行要点

1. **6.2**：机械预检 `make p6-bidir-matrix`；语义 100% 靠双向矩阵 + 回读，不单靠计数。
2. **6.3**：`ledger/P6_抽检召回样本.csv` 130 条 pending → 漏则回 P4/P5。
3. **6.4**：`make p1-kwscan` + 去向登记；不得以改脚本冒充达标。
4. **6.9–6.10**：对抗审查签收 + 用户 20 张抽查与 3 个真实问题。
5. 未批锚点队列前 **勿** 改冻结 K/锚点正文。

## 停线

D10 A/B 未裁决、P4 抽查未确认、AC-6.4 未达标时 **不可标 P7**。
