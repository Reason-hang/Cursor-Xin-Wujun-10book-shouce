#!/usr/bin/env python3
"""st_p1_pressure.py — T-P1-12：ST-2 冷续跑链 + ST-3 黄金漂移

用法（在 wujun-os/ 下）:
  python3 scripts/st_p1_pressure.py --report logs/ST_P1_20261027.md

ST-2：不依赖对话，仅仓库执行 gates + P1 闸门链 + 状态可读。
ST-3：data/gold/锚点表_gold.md 与当前试点锚点表在黄金单元上 S14 ≥0.7。
"""
import argparse
import os
import subprocess
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(cmd, cwd=ROOT):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def st2() -> tuple[bool, list[str]]:
    lines = []
    ok = True
    required = [
        "state/state.json",
        "state/STATE.md",
        "handover/项目交接文档.md",
        "ledger/锚点表_试点.md",
        "ledger/P1_选样表.json",
        "rules/pilot_rules_v1.md",
    ]
    for rel in required:
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            ok = False
            lines.append(f"FAIL 缺文件: {rel}")
        else:
            lines.append(f"OK 存在: {rel}")

    chain = [
        [sys.executable, "scripts/pack.py"],
        [sys.executable, "scripts/gates.py"],
        [sys.executable, "scripts/anchor_tool.py", "verify", "--ledger", "ledger/锚点表_试点.md", "--books-dir", "src_frozen"],
        [sys.executable, "scripts/p1_highlight_recall.py"],
        [sys.executable, "scripts/s14_overlap.py", "--a", "ledger/锚点表_试点.md", "--b", "ledger/锚点表_试点_blind2.md"],
        [sys.executable, "scripts/status.py"],
    ]
    for cmd in chain:
        rc, out = run(cmd)
        tag = "PASS" if rc == 0 else "FAIL"
        if rc != 0:
            ok = False
        lines.append(f"{tag} {' '.join(cmd[1:4])}…")
        if rc != 0 and out:
            lines.append("  " + out.strip().split("\n")[0][:200])
    return ok, lines


def _filter_ledger(src_path: str, unit_ids: list[str], dest_path: str) -> None:
    import re

    lines = open(src_path, encoding="utf-8").readlines()
    header = lines[:4]
    kept = []
    for ln in lines:
        if not ln.startswith("| P1-"):
            continue
        m = re.search(r"P1-([A-Z0-9]+-U\d+)-", ln)
        if m and m.group(1) in unit_ids:
            kept.append(ln)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.writelines(header if header else lines[:4])
        f.writelines(kept)


def st3() -> tuple[bool, list[str], float]:
    gold = os.path.join(ROOT, "data/gold/锚点表_gold.md")
    cur = os.path.join(ROOT, "ledger/锚点表_试点.md")
    manifest = os.path.join(ROOT, "data/gold/manifest.json")
    lines = []
    if not os.path.isfile(gold):
        return False, ["FAIL 缺 data/gold/锚点表_gold.md"], 0.0
    import json

    unit_ids = json.load(open(manifest, encoding="utf-8"))["unit_ids"]
    filtered = os.path.join(ROOT, "data/gold/_pilot_subset.md")
    _filter_ledger(cur, unit_ids, filtered)
    rc, out = run(
        [
            sys.executable,
            "scripts/s14_overlap.py",
            "--a",
            gold,
            "--b",
            filtered,
        ]
    )
    rate = 0.0
    for ln in out.splitlines():
        if "S14 重合率" in ln:
            try:
                rate = float(ln.split(":")[1].split("（")[0].strip())
            except ValueError:
                pass
        lines.append(ln)
    ok = rc == 0 and rate >= 0.7
    if not ok and rc == 0:
        lines.append("FAIL ST-3 重合率 <0.7")
    return ok, lines, rate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default="logs/ST_P1_20261027.md")
    args = ap.parse_args()

    s2_ok, s2_lines = st2()
    s3_ok, s3_lines, rate = st3()

    os.makedirs(os.path.dirname(os.path.join(ROOT, args.report)) or ".", exist_ok=True)
    with open(os.path.join(ROOT, args.report), "w", encoding="utf-8") as f:
        f.write(f"# P1 压力测试报告（T-P1-12）\n\n")
        f.write(f"- 日期: {date.today().isoformat()}\n")
        f.write(f"- ST-2 压缩模拟（仓库冷续跑链）: **{'通过' if s2_ok else '未通过'}**\n")
        f.write(f"- ST-3 漂移回归（gold vs 试点锚点）: **{'通过' if s3_ok else '未通过'}**（重合率 {rate:.4f}）\n\n")
        f.write("## ST-2 明细\n\n")
        for ln in s2_lines:
            f.write(f"- {ln}\n")
        f.write("\n## ST-3 明细\n\n")
        for ln in s3_lines:
            f.write(f"- {ln}\n")
        f.write("\n## 判定\n\n")
        if s2_ok and s3_ok:
            f.write("**ST-2 + ST-3 通过**，可进入 Gate-P1 用户确认。\n")
        else:
            f.write("**存在未通过项**，修机制后重跑 `make st-p1`。\n")

    print(f"ST-2: {'PASS' if s2_ok else 'FAIL'}; ST-3: {'PASS' if s3_ok else 'FAIL'} (rate={rate:.4f})")
    print(f"报告 -> {args.report}")
    sys.exit(0 if (s2_ok and s3_ok) else 1)


if __name__ == "__main__":
    main()
