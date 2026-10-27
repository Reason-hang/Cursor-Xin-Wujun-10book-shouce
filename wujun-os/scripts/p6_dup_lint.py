#!/usr/bin/env python3
"""AC-6.7：主手册 v0.9 中 24 字滑窗重复检测（忽略空白与 Markdown 标记行）。

M 卡模板字段（数理工程表达、行动方法骨架等）在多卡间重复属预期，不计入重复。
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "out/认知与行动操作系统_主手册_v0.9.md"
WIN = 24
MIN_HITS = 2  # 同一滑窗出现 >=2 次视为重复

# 整行可丢弃的 M 卡套话（归一化后匹配）
_BOILERPLATE_LINE = re.compile(
    r"^(?:"
    r"5\.数理工程表达：不映射。"
    r"|9\.落地映射（可缺省）：—"
    r"|变体卡：（待续）"
    r")$"
)

# 去掉行首「N.字段名：」只保留正文，避免跨行拼接误报
_MCARD_FIELD_PREFIX = re.compile(
    r"^[1-9]\.(?:"
    r"解决什么问题|原著核心判断|前提与边界|跨书关系|数理工程表达|"
    r"行动方法|例子与反例|出处|落地映射"
    r")[：:]?"
)

# 滑窗内若模板片段覆盖过高则视为套话，非卡间正文重复
_TEMPLATE_MARKERS = (
    "数理工程表达",
    "行动方法",
    "落地映射",
    "变体卡",
    "前提与边界",
    "跨书关系",
    "解决什么问题",
    "原著核心判断",
    "例子与反例",
    "可缺省",
    "映射·非原著",
    "整合者推断",
    "可检验映射",
    "不映射",
    "→判断（",
    "→步骤（",
    "→输出（",
    "→复查（",
    "→退出（",
    "主分类：对内",
    "主分类：对外",
    "稳定度：",
    "能力标签：",
    "所属：",
    "辅助标签：",
)


def _collapse_ws(line: str) -> str:
    return re.sub(r"\s+", "", line)


def norm_lines(text: str) -> list[str]:
    out: list[str] = []
    for line in text.splitlines():
        if line.startswith("#") or line.startswith("|") or line.startswith("```"):
            continue
        if line.strip().startswith("- 所属") or line.strip().startswith("####"):
            continue
        s = _collapse_ws(line)
        if not s or _BOILERPLATE_LINE.fullmatch(s):
            continue
        # 章首写作序 / 导出命令（多章重复，非模型卡正文）
        if "p5-export-chapter" in s or "写作序" in s:
            continue
        s = _MCARD_FIELD_PREFIX.sub("", s, count=1)
        if s:
            out.append(s)
    return out


def _template_char_coverage(w: str) -> float:
    """滑窗中被已知模板片段覆盖的字符比例（贪心从左匹配，近似即可）。"""
    if not w:
        return 1.0
    covered = [False] * len(w)
    for marker in sorted(_TEMPLATE_MARKERS, key=len, reverse=True):
        start = 0
        while True:
            idx = w.find(marker, start)
            if idx < 0:
                break
            for j in range(idx, idx + len(marker)):
                covered[j] = True
            start = idx + 1
    return sum(covered) / len(w)


def is_boilerplate_window(w: str) -> bool:
    if re.fullmatch(r"[\W_]+", w):
        return True
    if _template_char_coverage(w) >= 0.55:
        return True
    # 行动方法流水线骨架（括号内可变，骨架重复）
    if "输入（" in w and "→判断（" in w:
        return True
    # 出处行：P3 批次编号片段
    stripped = re.sub(r"P3[a-z]?-[A-Z0-9]+(?:-[A-Z0-9]+)*", "", w)
    stripped = re.sub(r"[；;、。\s]", "", stripped)
    if len(stripped) <= 8 and ("P3" in w or "K0" in w):
        return True
    return False


def main() -> int:
    if not MANUAL.is_file():
        print(f"FAIL: 缺少 {MANUAL}")
        return 1
    lines = norm_lines(MANUAL.read_text(encoding="utf-8"))
    total_chars = sum(len(ln) for ln in lines)
    if total_chars < WIN:
        print("p6 dup lint OK: 文本过短跳过")
        return 0
    buckets: dict[str, list[int]] = defaultdict(list)
    for line in lines:
        if len(line) < WIN:
            continue
        for i in range(len(line) - WIN + 1):
            w = line[i : i + WIN]
            if is_boilerplate_window(w):
                continue
            buckets[w].append(i)
    dups = {w: pos for w, pos in buckets.items() if len(pos) >= MIN_HITS}
    if dups:
        print(f"FAIL: {len(dups)} 个重复滑窗（展示前 5）")
        for w, pos in list(dups.items())[:5]:
            print(f"  「{w}」×{len(pos)}")
        return 1
    print(f"p6 dup lint OK: {total_chars} 字，无 {WIN} 字滑窗重复")
    return 0


if __name__ == "__main__":
    sys.exit(main())
