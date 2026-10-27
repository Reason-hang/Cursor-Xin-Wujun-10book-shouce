#!/usr/bin/env python3
"""为指定单元生成锚点探针候选（辅助 P3a 抽卡，不自动写 claim）"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
import wujun_units as wu

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pick_probe(text: str) -> str | None:
    for pat in [
        r"[^。！？\n]{12,40}(?:比什么都重要|才是成功之母|最根本|格局要大|境界要高)",
        r"我(?:认为|觉得|一直)[^。！？]{8,35}",
        r"[^。！？]{10,35}才是[^。！？]{4,20}",
    ]:
        for m in re.finditer(pat, text):
            s = m.group(0).strip()
            if text.count(s) == 1 and len(s) >= 10:
                return s[:40]
    for line in wu.paras(text):
        if len(line) >= 20 and "梦华" not in line[:5] and "梦馨" not in line[:5]:
            for i in range(0, max(1, len(line) - 12)):
                sub = line[i : i + 12]
                if text.count(sub) == 1:
                    return sub
    return None


def main():
    ids = sys.argv[1:]
    if not ids:
        print("用法: p3a_unit_draft.py TD-U0009 ...")
        sys.exit(1)
    cat = wu.build_catalog(os.path.join(ROOT, "src_frozen"))
    by_id = {u["unit_id"]: u for u in cat["units"]}
    for uid in ids:
        u = by_id[uid]
        text = cat["per_book_units"]["TD"][u["seq"] - 1]["text"]
        book = os.path.join(ROOT, "src_frozen", u["file"])
        pr = pick_probe(text)
        print(uid, u["title"][:35], "probe:", pr)
        if pr:
            w1 = re.findall(r"[\u4e00-\u9fff]{2}", pr)[:2]
            words = ",".join(w1) if len(w1) >= 2 else f"{w1[0]},{w1[0]}" if w1 else "态度,吴军"
            cid = f"P3a-{uid}-K01"
            rc = subprocess.run(
                [
                    sys.executable,
                    os.path.join(ROOT, "scripts/anchor_tool.py"),
                    "make",
                    "--book",
                    book,
                    "--probe",
                    pr,
                    "--words",
                    words,
                    "--id",
                    cid,
                ],
                capture_output=True,
                text=True,
            )
            print(rc.stdout.strip() if rc.returncode == 0 else rc.stderr.strip())


if __name__ == "__main__":
    main()
