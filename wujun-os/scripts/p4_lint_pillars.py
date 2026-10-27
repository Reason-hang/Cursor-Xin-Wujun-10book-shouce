#!/usr/bin/env python3
"""P4 归属 lint：每张 K 有唯一主归属且码表合法"""
import csv
import json
import sys
from pathlib import Path

import re

ROOT = Path(__file__).resolve().parents[1]
ASSIGN = ROOT / "ledger/P4_归属表.csv"
PILLARS = ROOT / "spec/pillars.yaml"
CODE_RE = re.compile(r"^\s+code:\s+(D\d{2}(?:-\d+)?)\s*$")


def valid_codes():
    codes = set()
    for line in PILLARS.read_text(encoding="utf-8").splitlines():
        m = CODE_RE.match(line)
        if m:
            codes.add(m.group(1))
    return codes


def k_card_ids():
    ids = set()
    for p in ROOT.glob("cards/*/*.json"):
        doc = json.loads(p.read_text(encoding="utf-8"))
        for c in doc.get("cards", []):
            if c.get("disposition") == "K":
                ids.add(c["card_id"])
    return ids


def main():
    valid = valid_codes()
    k_ids = k_card_ids()
    rows = list(csv.DictReader(ASSIGN.open(encoding="utf-8")))
    errs = []
    seen = set()
    for r in rows:
        cid = r["card_id"]
        if cid in seen:
            errs.append(f"重复卡: {cid}")
        seen.add(cid)
        p = (r.get("primary_pillar") or "").strip()
        st = r.get("status", "")
        if p and p not in valid:
            errs.append(f"非法主归属 {cid}: {p}")
        if st == "x_hint_only" and p:
            errs.append(f"x_hint_only 不应有主归属: {cid}")
        if st == "x_hint_only" and not p:
            continue
        for a in (r.get("auxiliary_pillars") or "").split(";"):
            a = a.strip()
            if a and a not in valid:
                errs.append(f"非法辅助 {cid}: {a}")
        if r.get("status") == "draft" and not p:
            errs.append(f"draft 但无主归属: {cid}")
    missing = k_ids - seen
    extra = seen - k_ids
    if missing:
        errs.append(f"归属表缺 K 卡 {len(missing)} 张")
    if extra:
        errs.append(f"归属表多余 {len(extra)} 张")
    if errs:
        for e in errs[:20]:
            print("FAIL:", e)
        return 1
    print(f"P4 pillars lint OK: {len(rows)} 张 K")
    return 0


if __name__ == "__main__":
    sys.exit(main())
