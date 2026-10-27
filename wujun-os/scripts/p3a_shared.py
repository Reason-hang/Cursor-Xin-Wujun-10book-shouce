#!/usr/bin/env python3
"""P3a 批次共用：单元文本、探针、锚点句界、指纹词（与 anchor_tool 口径一致）"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER_P3A = ROOT / "ledger/锚点表_P3a.md"
BATCH_DIR = ROOT / "batches/P3a"
FROZEN = ROOT / "src_frozen"

_UNIT_INDEX: dict | None = None


def load_units_index() -> dict:
    global _UNIT_INDEX
    if _UNIT_INDEX is None:
        data = json.loads((ROOT / "data/units_index.json").read_text(encoding="utf-8"))
        _UNIT_INDEX = {u["unit_id"]: u for u in data["units"]}
    return _UNIT_INDEX


def unit_record(unit_id: str) -> dict:
    u = load_units_index().get(unit_id)
    if not u:
        raise KeyError(f"未知 unit_id: {unit_id}")
    return u


def book_path(unit: dict) -> Path:
    return FROZEN / unit["file"]


def unit_text(unit: dict) -> str:
    lines = book_path(unit).read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[unit["line_start"] - 1 : unit["line_end"]])


def load_book_text(unit: dict) -> str:
    return book_path(unit).read_text(encoding="utf-8")


def sent_span(text: str, pos: int) -> tuple[int, int]:
    s = pos
    while s > 0 and text[s - 1] not in "。！？" and text[max(0, s - 2) : s] != "\n\n":
        s -= 1
    e, n = pos, len(text)
    closers = '""\u201d\u2019\u300d\u300f\uff09'
    while e < n:
        if text[e] in "。！？":
            e += 1
            while e < n and text[e] in closers:
                e += 1
            break
        if text[e : e + 2] == "\n\n":
            break
        e += 1
    while s < e and text[s] in " \n\t":
        s += 1
    return s, e


def find_probe_in_segment(seg: str, book_text: str) -> str | None:
    flat = re.sub(r"\s+", "", re.sub(r"^#+\s*", "", seg))
    for L in range(12, 28):
        for i in range(0, len(flat) - L + 1):
            p = flat[i : i + L]
            if book_text.count(p) == 1:
                return p
    return None


def suggest_probe(unit_id: str) -> str | None:
    u = unit_record(unit_id)
    book = load_book_text(u)
    return find_probe_in_segment(unit_text(u), book)


def pick_fingerprint_words(seg: str) -> str:
    for L in (3, 4, 2):
        for i in range(len(seg) - L):
            w = seg[i : i + L]
            if w.strip() and all("\u4e00" <= c <= "\u9fff" or c.isalnum() for c in w):
                w2 = seg[i + L : i + L + L] if i + 2 * L <= len(seg) else None
                if w2 and w2 in seg and w != w2:
                    return f"{w},{w2}"
    m = re.findall(r"[\u4e00-\u9fff]{2}", seg)
    if len(m) >= 2:
        return f"{m[0]},{m[1]}"
    if m:
        return f"{m[0]},{m[0]}"
    return "态度,吴军"


def validate_words(probe: str, words: str, unit: dict) -> list[str]:
    book = load_book_text(unit)
    pos = book.find(probe)
    if pos < 0 or book.count(probe) != 1:
        return [f"探针需在全书恰好 1 次，当前 {book.count(probe)}"]
    s, e = sent_span(book, pos)
    seg = book[s:e]
    miss = [w for w in words.split(",") if w and w not in seg]
    return [f"指纹词不在锚点段: {miss}"] if miss else []


def anchor_make(unit_id: str, probe: str, words: str, card_id: str) -> tuple[int, str]:
    u = unit_record(unit_id)
    tool = ROOT / "scripts/anchor_tool.py"
    r = subprocess.run(
        [
            sys.executable,
            str(tool),
            "make",
            "--book",
            str(book_path(u)),
            "--probe",
            probe,
            "--words",
            words,
            "--id",
            card_id,
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    return r.returncode, (r.stdout + r.stderr).strip()


def parse_batch_md(batch_id: str) -> list[str]:
    path = BATCH_DIR / f"{batch_id}.md"
    if not path.is_file():
        raise FileNotFoundError(path)
    ids = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*([A-Z][A-Z0-9]{1,3}-U\d{4})\s*\|", line)
        if m:
            ids.append(m.group(1))
    if not ids:
        raise ValueError(f"{batch_id} 未解析到 unit_id")
    return ids


def book_code_from_unit(unit_id: str) -> str:
    return unit_id.split("-")[0]
