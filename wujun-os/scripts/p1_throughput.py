#!/usr/bin/env python3
"""p1_throughput.py — T-P1-09 试点吞吐估算"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    sel = json.load(open(os.path.join(ROOT, "ledger/P1_选样表.json"), encoding="utf-8"))
    idx = json.load(open(os.path.join(ROOT, "data/units_index.json"), encoding="utf-8"))
    by_id = {u["unit_id"]: u for u in idx["units"]}
    units = sel["units"]
    chars = sum(by_id[u]["chars"] for u in units if u in by_id)
    cards = 24  # 与当前台账一致；可由扫描 cards/ 动态计
    out = os.path.join(ROOT, "ledger/P1_吞吐记录.md")
    batch_target = 35000
    batches_for_pilot = max(1, round(chars / batch_target))
    with open(out, "w", encoding="utf-8") as f:
        f.write("# P1 吞吐记录（T-P1-09）\n\n")
        f.write(f"| 项 | 值 |\n|---|---|\n")
        f.write(f"| 试点单元数 | {len(units)} |\n")
        f.write(f"| 试点单元汉字（索引 chars） | {chars:,} |\n")
        f.write(f"| 论点卡数 | {cards} |\n")
        f.write(f"| 卡/单元（均值） | {cards/len(units):.2f} |\n")
        f.write(f"| 按 3.5 万字/批折算 | 约 **{batches_for_pilot}** 批完成试点体量 |\n")
        f.write(f"| 2026-10-27 Agent 实测 | 18 单元分多轮完成；含锚点/划重点补齐 |\n")
        f.write(f"| 上下文占用（估） | 单单元正文 2.7k–7.1k 字；建议每轮 **≤2 单元深读+抽卡** |\n")
        f.write(f"| **建议每轮批数** | **2 批**（≈7 万字上限），3 批仅在大促前赶进度时用 |\n")
        f.write(f"| 全量 1697 内容单元 @2批/轮 | 约 **{max(1, round(1697 * (chars/len(units)) / (2*batch_target)))}–{max(1, round(1697 * (chars/len(units)) / (2*batch_target) * 1.2))}** 轮量级（待 P3 校准） |\n")
        f.write("\n降级触发：单轮连 1 个 3–5 万字批次（含锚点校验）无法稳定完成 → 走 §7.8 Z1。\n")
    print(f"已写入 {out}；试点 {chars} 字")


if __name__ == "__main__":
    main()
