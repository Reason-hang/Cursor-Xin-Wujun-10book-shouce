#!/usr/bin/env python3
"""从首轮锚点表生成双盲第二轮锚点（同单元内另选探针，目标区间重叠≥50%）。

不读取 cards/*.json，仅读 ledger 与 src_frozen。
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_ledger(path):
    rows = []
    for line in open(path, encoding="utf-8"):
        if not line.startswith("|"):
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 8 or not re.fullmatch(r"\d+", c[2]):
            continue
        rows.append(
            {
                "id": c[0],
                "book": c[1],
                "cs": int(c[4]),
                "ce": int(c[5]),
                "words": c[7],
            }
        )
    return rows


def pick_probe(text, cs, ce, old_probe_hint=""):
    seg = text[cs:ce]
    # 优先句内 8–15 字唯一子串
    for length in (12, 10, 8, 15, 14):
        for i in range(0, max(1, len(seg) - length)):
            sub = seg[i : i + length].strip()
            if len(sub) < 6 or "\n" in sub:
                continue
            if text.count(sub) == 1 and sub in seg:
                return sub
    return None


def main():
    ledger = os.path.join(ROOT, "ledger/锚点表_试点.md")
    out_ledger = os.path.join(ROOT, "ledger/锚点表_试点_blind2.md")
    books_dir = os.path.join(ROOT, "src_frozen")
    rows = parse_ledger(ledger)
    cache = {}
    out_lines = [
        "# 锚点表（P1 试点 · 双盲第二轮）\n",
        "\n",
        "| 卡ID | 书文件名 | 行起 | 行止 | 字符起 | 字符止 | SHA1 | 指纹词 |\n",
        "|---|---|---|---|---|---|---|---|\n",
    ]
    for r in rows:
        book = r["book"]
        path = os.path.join(books_dir, book)
        if book not in cache:
            cache[book] = open(path, encoding="utf-8").read()
        text = cache[book]
        probe = pick_probe(text, r["cs"], r["ce"])
        if not probe:
            sys.exit(f"无法为 {r['id']} 选探针")
        blind_id = re.sub(r"-(K|M|R|X)\d+$", "-B01", r["id"])
        if blind_id == r["id"]:
            blind_id = r["id"] + "-B2"
        words = r["words"] or "要点,吴军"
        cmd = [
            sys.executable,
            os.path.join(ROOT, "scripts/anchor_tool.py"),
            "make",
            "--book",
            path,
            "--probe",
            probe,
            "--words",
            words.split(",")[0] + "," + (words.split(",")[1] if "," in words else words.split(",")[0]),
            "--id",
            blind_id,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        if proc.returncode != 0:
            # 指纹词失败时仅用段内前两字
            w1 = words.split(",")[0]
            cmd[-1] = w1 + "," + w1
            proc = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        if proc.returncode != 0:
            print(proc.stderr or proc.stdout, file=sys.stderr)
            sys.exit(f"anchor make 失败: {r['id']}")
        line = proc.stdout.strip()
        if line.startswith("|"):
            out_lines.append(line + "\n")
    with open(out_ledger, "w", encoding="utf-8") as f:
        f.writelines(out_lines)
    print(f"已写入 {out_ledger}（{len(rows)} 行）")


if __name__ == "__main__":
    main()
