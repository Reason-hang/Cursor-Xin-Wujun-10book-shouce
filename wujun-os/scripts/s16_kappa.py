#!/usr/bin/env python3
"""S16 / T-P4-10：盲重标 κ（支持 primary_blind_manual 列）"""
import csv
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSIGN = ROOT / "ledger/P4_归属表.csv"
SEED = 20261027
SAMPLE_OUT = ROOT / "ledger/P4_盲重标样本.csv"
REPORT = ROOT / "ledger/P4_盲重标κ报告.md"

RULES = [
    (re.compile(r"创新|产品|0到1|从0到1|发明|专利"), "D10-1"),
    (re.compile(r"投资|财富|现金流|资产配置|股票|房价"), "D09-1"),
    (re.compile(r"商业|创业|定价|免费|稀缺|市场|并购"), "D08-2"),
    (re.compile(r"沟通|合作|信任|说服|带宽"), "D07-1"),
    (re.compile(r"职场|职业|汇报|老板|同事|面试"), "D06-1"),
    (re.compile(r"执行|复盘|坚持|效率|目标|时间管理"), "D05-1"),
    (re.compile(r"选择|决策|止损|概率|风险|取舍"), "D03-1"),
    (re.compile(r"数学|算法|工程|计算机|逻辑|科学方法"), "D04-1"),
    (re.compile(r"学习|教育|成长|心态|幸福|命运|三观"), "D02-2"),
    (re.compile(r"格局|境界|认知|理性|哲学|思考|见识"), "D01-2"),
]


def blind_pillar(claim: str) -> str:
    for pat, code in RULES:
        if pat.search(claim):
            return code
    return "D01-1"


def cohens_kappa(a: list[str], b: list[str]) -> float:
    n = len(a)
    if n == 0:
        return 0.0
    cats = sorted(set(a) | set(b))
    mat = Counter((x, y) for x, y in zip(a, b))
    po = sum(mat[(c, c)] for c in cats) / n
    pa = Counter(a)
    pb = Counter(b)
    pe = sum((pa[c] / n) * (pb[c] / n) for c in cats)
    if pe >= 1.0:
        return 1.0
    return (po - pe) / (1 - pe)


def load_claim(card_id: str) -> str:
    for p in ROOT.glob("cards/*/*.json"):
        doc = json.loads(p.read_text(encoding="utf-8"))
        for c in doc.get("cards", []):
            if c["card_id"] == card_id:
                return c.get("claim", "")
    return ""


def build_sample():
    pool = [r for r in csv.DictReader(ASSIGN.open(encoding="utf-8")) if r["status"] == "draft" and r["primary_pillar"]]
    n_sample = max(60, int(len(pool) * 0.05 + 0.999))
    rng = random.Random(SEED)
    return rng.sample(pool, min(n_sample, len(pool)))


def write_report(rows, pool_n, label_b: str, kappa, kappa_l1, gate):
    agree = sum(1 for x in rows if x["primary_original"] == x[label_b])
    REPORT.write_text(
        "\n".join(
            [
                "# T-P4-10｜盲重标 κ 报告（2026-10-27）",
                "",
                f"| 样本 | {len(rows)}（池 {pool_n}，seed={SEED}） |",
                f"| 盲判列 | `{label_b}` |",
                f"| κ（L2 码） | **{kappa:.4f}** |",
                f"| κ（L1 柱） | **{kappa_l1:.4f}** |",
                f"| 一致率 L2 | {agree}/{len(rows)} |",
                f"| AC-4.4（L1≥0.6） | **{gate}** |",
                "",
                "## 方法",
                "",
                "- `primary_blind`：关键词规则；`primary_blind_manual`：claim-only 人工复判（`data/p4_blind_manual.json`）。",
                "- κ 以 **manual 列优先**（若已 `make p4-apply-blind-manual`）。",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main():
    resample = "--resample" in sys.argv
    pool_n = len([r for r in csv.DictReader(ASSIGN.open(encoding="utf-8")) if r["status"] == "draft"])

    if SAMPLE_OUT.is_file() and not resample:
        rows = list(csv.DictReader(SAMPLE_OUT.open(encoding="utf-8")))
    else:
        sample = build_sample()
        rows = []
        for r in sample:
            claim = load_claim(r["card_id"])
            rows.append(
                {
                    "card_id": r["card_id"],
                    "primary_original": r["primary_pillar"],
                    "primary_blind": blind_pillar(claim),
                    "primary_blind_manual": "",
                    "agree_manual": "",
                    "agree": "Y" if r["primary_pillar"] == blind_pillar(claim) else "N",
                    "claim_excerpt": claim[:60],
                }
            )
        fields = list(rows[0].keys())
        with SAMPLE_OUT.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    has_manual = any((r.get("primary_blind_manual") or "").strip() for r in rows)
    label_b = "primary_blind_manual" if has_manual else "primary_blind"

    a = [r["primary_original"] for r in rows]
    b = [r[label_b] for r in rows]
    kappa = cohens_kappa(a, b)
    kappa_l1 = cohens_kappa([x.split("-")[0] for x in a], [x.split("-")[0] for x in b])
    gate = "pass" if kappa_l1 >= 0.6 else "fail"

    write_report(rows, pool_n, label_b, kappa, kappa_l1, gate)
    print(f"s16: n={len(rows)} col={label_b} kappa_L1={kappa_l1:.3f} gate={gate}")


if __name__ == "__main__":
    main()
