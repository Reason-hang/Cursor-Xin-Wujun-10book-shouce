#!/usr/bin/env python3
"""s09_make_cards.py — S09 单元卡（P2 分诊输入）

用法: python3 scripts/s09_make_cards.py --src src_frozen --out logs/unit_cards.md
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from wujun_units import build_catalog, paras, cjk, QA, INTERACT, SERIES

DOMAIN_TERMS = (
    "跨境",
    "电商",
    "物流",
    "供应链",
    "出海",
    "定价",
    "库存",
    "仓储",
    "关税",
    "运费",
)
DATE_RE = re.compile(r"(20\d{2})[年\-/]")


def clip(s: str, n: int) -> str:
    s = re.sub(r"\s+", " ", s.strip())
    return s if len(s) <= n else s[: n - 1] + "…"


def keywords(title: str, text: str, k=5) -> str:
    pool = re.findall(r"[\u4e00-\u9fff]{2,6}", title + text[:800])
    seen, out = set(), []
    for w in pool:
        if w in seen or len(w) < 2:
            continue
        seen.add(w)
        out.append(w)
        if len(out) >= k:
            break
    return "、".join(out)


def unit_type(u: dict, text: str) -> str:
    if u["cls"] != "C":
        return u["cls"]
    if u["is_qa"]:
        return "问答"
    if u["is_interact"]:
        return "互动"
    if "游记" in u["title"] or "日记" in u["title"]:
        return "游记"
    if re.search(r"教育|学校|大学|博士", u["title"]):
        return "教育"
    if "### 划重点" in text and u["book_code"] == "SG3":
        return "来信3"
    return "正文"


def series_key(title: str) -> str:
    t = re.sub(r"[（(][上下中一二三四五][）)]", "", title)
    t = re.sub(r"[上下]篇", "", t)
    return t.strip()[:48]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="src_frozen")
    ap.add_argument("--out", default="logs/unit_cards.md")
    args = ap.parse_args()
    cat = build_catalog(args.src)
    content = [u for u in cat["units"] if u["cls"] == "C"]
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("# 单元卡（S09 · P2 分诊输入）\n\n")
        f.write(f"- 内容单元: **{len(content)}**\n")
        f.write(f"- 生成脚本: `scripts/s09_make_cards.py`\n\n")
        f.write(
            "| unit_id | 书码 | 类型 | 日期 | 汉字 | 首段≤100 | 末段≤60 | 关键词 | 领域直连 | 划重点 | 系列组 |\n"
        )
        f.write("|---|---|---|---|---:|---|---|---|---|---|---|\n")
        for u in content:
            seq = u["seq"] - 1
            text = cat["per_book_units"][u["book_code"]][seq]["text"]
            ps = paras(text)
            head = clip(ps[0] if ps else u["title"], 100)
            tail = clip(ps[-1] if ps else "", 60)
            dom = sum(text.count(t) for t in DOMAIN_TERMS)
            hl = "Y" if re.search(r"^###\s+划重点", text, re.M) else ""
            sk = series_key(u["title"]) if u["is_series"] else ""
            dates = DATE_RE.findall(u["title"] + text[:200])
            date = dates[0] if dates else ""
            ut = unit_type(u, text)
            f.write(
                f"| {u['unit_id']} | {u['book_code']} | {ut} | {date} | {u['chars']} | {head} | {tail} | "
                f"{keywords(u['title'], text)} | {'Y' if dom >= 3 else ''} | {hl} | {sk} |\n"
            )
    print(f"s09: {len(content)} 张单元卡 -> {args.out}")
    if len(content) != cat["totals"]["content"]:
        print(f"WARN 期望内容单元 {cat['totals']['content']}，实际 {len(content)}", file=sys.stderr)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
