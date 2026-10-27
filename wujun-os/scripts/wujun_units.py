"""wujun_units — 10 本书加载、单元切分（与 s01_probe 口径一致）"""
from __future__ import annotations

import collections
import glob
import os
import re

CJK = re.compile(r"[\u4e00-\u9fff]")
BOOKS = [
    ("来信1", "硅谷来信1", "SG1", 2),
    ("来信2", "吴军来信2", "WJ2", 2),
    ("来信3", "硅谷来信3", "SG3", 2),
    ("谷歌方法论", "谷歌方法论", "GG", 2),
    ("见识", "见识", "JS", 2),
    ("数学通识", "数学通识50讲", "SX", 3),
    ("格局", "格局", "GJ", 2),
    ("境界", "境界", "JJ", 3),
    ("富足", "富足", "FZ", 3),
    ("态度", "态度", "TD", 2),
]
BOOK_ORDER = [code for _, _, code, _ in BOOKS]
NONCONTENT = re.compile(r"^目录$|^《.*》目录$|导航|第二季来啦|收藏丨|^谷歌方法论：")
QA = re.compile(r"答读者问|周末问答|回用户|回同学")
INTERACT = re.compile(r"周末互动|周末放送|回信精选|精选")
SERIES = re.compile(r"[（(](上|下|中|一|二|三|四|五)[）)]|[上下]篇|之[一二三四]")


def cjk(s: str) -> int:
    return len(CJK.findall(s))


def paras(text: str) -> list[str]:
    out = []
    for l in text.split("\n"):
        s = l.strip()
        if cjk(s) >= 40 and not re.match(r"^([-*]\s*\[|!\[|>|#)", s):
            out.append(s)
    return out


def load_books(src: str) -> dict:
    out = {}
    for p in sorted(glob.glob(os.path.join(src, "*.md"))):
        name = os.path.basename(p)
        for key, book, code, lvl in BOOKS:
            if key in name:
                raw = open(p, encoding="utf-8").read()
                out[code] = {
                    "path": p,
                    "file": name,
                    "book": book,
                    "lvl": lvl,
                    "text": raw,
                    "lines": raw.split("\n"),
                }
                break
    return out


def split_units(text: str, lvl: int) -> list[dict]:
    lines = text.split("\n")
    units, cur, start, buf = [], None, 0, 0
    for i, l in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*)", l)
        if m and len(m.group(1)) <= lvl:
            if cur is not None:
                units.append(dict(title=cur, start=start, end=i, chars=buf))
            cur, start, buf = m.group(2).strip(), i, 0
        else:
            buf += cjk(l)
    if cur is not None:
        units.append(dict(title=cur, start=start, end=len(lines), chars=buf))
    for u in units:
        u["text"] = "\n".join(lines[u["start"] : u["end"]])
        u["cls"] = "N" if NONCONTENT.search(u["title"]) else ("S" if u["chars"] < 100 else "C")
    return units


def build_catalog(src: str = "src_frozen") -> dict:
    books = load_books(src)
    if len(books) != 10:
        raise SystemExit(f"在 {src} 里只找到 {len(books)} 本，期望 10 本")
    all_units = []
    per_book = {}
    for code in BOOK_ORDER:
        d = books[code]
        us = split_units(d["text"], d["lvl"])
        for i, u in enumerate(us, 1):
            uid = f"{code}-U{i:04d}"
            row = {
                "unit_id": uid,
                "book_code": code,
                "book": d["book"],
                "file": d["file"],
                "seq": i,
                "title": u["title"],
                "line_start": u["start"] + 1,
                "line_end": u["end"],
                "chars": u["chars"],
                "cls": u["cls"],
                "is_qa": bool(QA.search(u["title"])),
                "is_interact": bool(INTERACT.search(u["title"])),
                "is_series": bool(SERIES.search(u["title"])),
            }
            all_units.append(row)
        per_book[code] = us
    totals = collections.Counter(u["cls"] for u in all_units)
    return {
        "books": books,
        "per_book_units": per_book,
        "units": all_units,
        "totals": {
            "total": len(all_units),
            "content": totals["C"],
            "container": totals["S"],
            "noncontent": totals["N"],
            "content_chars": sum(u["chars"] for u in all_units if u["cls"] == "C"),
            "file_chars": sum(cjk(b["text"]) for b in books.values()),
        },
    }
