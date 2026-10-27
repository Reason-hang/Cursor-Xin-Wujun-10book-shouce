#!/usr/bin/env python3
"""T-P5-10：汇总 drafts/p5 → out/D1、D2 与能力速查、冲突表。"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "drafts/p5"
OUT = ROOT / "out"
DELIVER = ROOT.parent / "最终所有交付物"

CHAPTERS = [
    ("D01", "第 1 章 D01 认知格局与境界哲学"),
    ("D02", "第 2 章 D02 个人成长与世界观/人生观/价值观"),
    ("D03", "第 3 章 D03 判断决策与风险止损"),
    ("D04", "第 4 章 D04 数理与计算机思维与工程思维"),
    ("D05", "第 5 章 D05 做事方法与执行力"),
    ("D06", "第 6 章 D06 职业与职场"),
    ("D07", "第 7 章 D07 为人处世与组织协同"),
    ("D08", "第 8 章 D08 商业与创业"),
    ("D09", "第 9 章 D09 财富与投资"),
    ("D10", "第 10 章 D10 创新与产品方法（三道门 fail，见章首）"),
]

TAG_PROMPTS = {
    "思": "我现在要想清楚……",
    "学": "我现在要学或建立体系……",
    "沟": "我现在要沟通或对齐……",
    "做": "我现在要执行或落地……",
}


def parse_m_card(text: str) -> dict | None:
    m = re.search(r"#### (M-[^\s　]+)", text)
    if not m:
        return None
    mid = m.group(1)
    tags_m = re.search(r"- 能力标签：(.+)", text)
    tags = []
    if tags_m:
        raw = tags_m.group(1).replace("｜", "、")
        for part in re.split(r"[、,]", raw):
            part = part.strip()
            if part in TAG_PROMPTS:
                tags.append(part)
    pillar_m = re.search(r"- 所属：([^\n]+)", text)
    pillar = pillar_m.group(1).split("｜")[0].strip() if pillar_m else ""
    claim_m = re.search(r"^2\. 原著核心判断：(.+)$", text, re.M)
    claim = claim_m.group(1).strip() if claim_m else ""
    if len(claim) > 30:
        claim = claim[:27] + "…"
    return {"id": mid, "tags": tags, "pillar": pillar, "claim": claim}


def collect_m_cards() -> list[dict]:
    rows = []
    for p in sorted(DRAFT.glob("**/M-*.md")):
        d = parse_m_card(p.read_text(encoding="utf-8"))
        if d:
            rows.append(d)
    return rows


def chapter_block(code: str, title: str) -> str:
    parts = [f"\n# {title}\n"]
    ch_dir = DRAFT / code
    if not ch_dir.is_dir():
        return ""
    for name in sorted(ch_dir.iterdir()):
        if name.name.startswith("D") and "章首" in name.name:
            parts.append(name.read_text(encoding="utf-8"))
            parts.append("\n")
    for name in sorted(ch_dir.glob("M-*.md")):
        parts.append(name.read_text(encoding="utf-8"))
        parts.append("\n")
    for name in sorted(ch_dir.glob("S_*.md")):
        parts.append(name.read_text(encoding="utf-8"))
        parts.append("\n")
    cov = ch_dir / f"AC-5.8_{code}必检议题覆盖表.md"
    if cov.is_file():
        parts.append(cov.read_text(encoding="utf-8"))
        parts.append("\n")
    end = ch_dir / "章末覆盖声明.md"
    if end.is_file():
        parts.append(end.read_text(encoding="utf-8"))
        parts.append("\n")
    return "\n".join(parts)


def build_quick_ref(cards: list[dict]) -> str:
    lines = ["# 第五篇 能力速查（思·学·沟·做）\n"]
    for tag in ("思", "学", "沟", "做"):
        lines.append(f"\n## {tag}｜{TAG_PROMPTS[tag]}\n")
        lines.append("| 我现在要…… | 模型卡 ID | 支柱 | 一句话 |\n")
        lines.append("|---|---|---|---|\n")
        for c in cards:
            if tag not in c["tags"]:
                continue
            lines.append(
                f"| {TAG_PROMPTS[tag]} | {c['id']} | {c['pillar']} | {c['claim']} |\n"
            )
    return "".join(lines)


def build_conflict_table() -> str:
    path = DRAFT / "P5_冲突消解表.md"
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return ""


def build_scenes_index() -> str:
    lines = ["# 第四篇 场景入口汇总（§16.6）\n\n"]
    for code, _ in CHAPTERS:
        for p in sorted((DRAFT / code).glob("S_*.md")) if (DRAFT / code).is_dir() else []:
            lines.append(p.read_text(encoding="utf-8"))
            lines.append("\n")
    return "".join(lines)


def build_d1(cards: list[dict]) -> str:
    head = """# 认知与行动操作系统｜主手册 v0.9（P5 集成稿）

> **状态**：过程集成稿；D10 独立第 10 柱 **待你裁决**（A 保留 / B 并入 D08）。不构成投资建议等见 D09 章首。

## 使用说明（简）

1. 按情境从「场景入口」找 `S-` 行，跳到对应 `M-` 模型卡。
2. 按能力从「能力速查」找思/学/沟/做。
3. 可执行步骤用《行动工具集》中的 `T-` 卡。
4. 论点溯源见 D3 台账（P6 前为过程件）。

## 全景（10 柱）

| 分类 | 支柱 |
|---|---|
| 对内 | D01 认知格局；D02 个人成长；D03 判断决策；D04 数理与工程思维 |
| 对外 | D05 做事方法；D06 职业职场；D07 为人处世；D08 商业；D09 财富投资；D10 创新产品（待裁决） |

"""
    body = []
    for code, title in CHAPTERS:
        block = chapter_block(code, title)
        if block:
            body.append(block)
    body.append(build_scenes_index())
    body.append(build_quick_ref(cards))
    body.append("\n\n")
    body.append(build_conflict_table())
    return head + "\n".join(body)


def build_d2() -> str:
    tools = sorted((DRAFT / "tools").glob("T-*.md"))
    parts = [
        "# 行动工具集 v0.9（P5 集成稿）\n\n",
        f"共 **{len(tools)}** 个工具（候选 14 已齐）。\n\n",
    ]
    for t in tools:
        parts.append(t.read_text(encoding="utf-8"))
        parts.append("\n\n")
    return "".join(parts)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    DELIVER.mkdir(parents=True, exist_ok=True)
    cards = collect_m_cards()
    d1 = build_d1(cards)
    d2 = build_d2()
    d1_path = OUT / "认知与行动操作系统_主手册_v0.9.md"
    d2_path = OUT / "行动工具集_v0.9.md"
    d1_path.write_text(d1, encoding="utf-8")
    d2_path.write_text(d2, encoding="utf-8")
    deliver_d1 = DELIVER / "认知与行动操作系统_主手册_v0.9.md"
    deliver_d2 = DELIVER / "行动工具集_v0.9.md"
    deliver_d1.write_text(d1, encoding="utf-8")
    deliver_d2.write_text(d2, encoding="utf-8")
    print(f"p5 assemble: {len(cards)} M → {d1_path}")
    print(f"p5 assemble: tools → {d2_path}")
    print(f"copied → {deliver_d1.parent}")


if __name__ == "__main__":
    main()
