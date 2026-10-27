#!/usr/bin/env python3
"""概念键表 lint：AC-4.2 多处定义 0（canonical 唯一、别名不冲突）"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "rules/concept_keys.csv"
CK = re.compile(r"^CK-\d{4}$")


def main():
    if not PATH.is_file():
        print("缺少 rules/concept_keys.csv，先 make p4-concept-keys")
        return 1
    rows = list(csv.DictReader(PATH.open(encoding="utf-8")))
    errs = []
    ids = set()
    canon = {}
    alias_owner = {}
    for r in rows:
        cid = r["concept_id"]
        name = r["canonical_name"].strip()
        if not CK.match(cid):
            errs.append(f"非法 ID {cid}")
        if cid in ids:
            errs.append(f"重复 ID {cid}")
        ids.add(cid)
        if name in canon:
            errs.append(f"canonical 重复: {name} ({canon[name]} vs {cid})")
        canon[name] = cid
        for a in (r.get("aliases") or "").split(";"):
            a = a.strip()
            if not a:
                continue
            if a in alias_owner and alias_owner[a] != cid:
                errs.append(f"别名跨键: {a} -> {alias_owner[a]} 与 {cid}")
            alias_owner[a] = cid
            if a == name:
                errs.append(f"别名与 canonical 相同: {cid}")
    long_names = [r for r in rows if len(r["canonical_name"]) > 12]
    if long_names:
        print(f"WARN: {len(long_names)} 个 canonical 超 12 字，P4 后续可缩写（§15.8）")
    if errs:
        for e in errs[:20]:
            print("FAIL:", e)
        print(f"concept_keys lint: {len(errs)} 项失败")
        return 1
    print(f"concept_keys lint OK: {len(rows)} 键")
    return 0


if __name__ == "__main__":
    sys.exit(main())
