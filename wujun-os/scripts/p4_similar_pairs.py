#!/usr/bin/env python3
"""T-P4-03：K 卡 claim TF-IDF 余弦相似度，输出近似卡对候选表（人工判定输入）"""
import argparse
import csv
import json
import math
import re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "ledger/P4_近似卡对候选.csv"
TOKEN = re.compile(r"[\u4e00-\u9fff]{2,4}")


def tokens(text: str) -> Counter:
    text = re.sub(r"\s+", "", text)
    c = Counter()
    for m in TOKEN.findall(text):
        c[m] += 1
    for i in range(len(text) - 1):
        bg = text[i : i + 2]
        if all("\u4e00" <= ch <= "\u9fff" for ch in bg):
            c[bg] += 1
    return c


def load_fingerprints() -> dict[str, set[str]]:
    fps: dict[str, set[str]] = {}
    for name in ("ledger/锚点表_P3a.md", "ledger/锚点表_P3b.md"):
        p = ROOT / name
        if not p.is_file():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.startswith("| P"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 8:
                continue
            cid, words = cells[0], cells[7]
            fps[cid] = {w.strip() for w in words.split(",") if w.strip()}
    return fps


def fingerprint_jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    u = a | b
    return len(a & b) / len(u) if u else 0.0


def load_k_cards():
    rows = []
    for p in sorted(ROOT.glob("cards/*/*.json")):
        doc = json.loads(p.read_text(encoding="utf-8"))
        uid = doc.get("unit_id", p.stem)
        book = doc.get("book_code", p.parent.name)
        for c in doc.get("cards", []):
            if c.get("disposition") != "K":
                continue
            claim = (c.get("claim") or "").strip()
            if len(claim) < 8:
                continue
            rows.append(
                {
                    "card_id": c["card_id"],
                    "unit_id": uid,
                    "book_code": book,
                    "claim": claim,
                    "type": c.get("type", ""),
                }
            )
    return rows


def tfidf_vectors(docs: list[Counter]) -> list[dict[str, float]]:
    n = len(docs)
    df = Counter()
    for d in docs:
        for t in d:
            df[t] += 1
    vecs = []
    for d in docs:
        v = {}
        ln = sum(d.values()) or 1
        for t, cnt in d.items():
            idf = math.log((n + 1) / (df[t] + 1)) + 1.0
            v[t] = (cnt / ln) * idf
        vecs.append(v)
    return vecs


def cosine(a: dict, b: dict) -> float:
    if not a or not b:
        return 0.0
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in a if k in b)
    na = math.sqrt(sum(x * x for x in a.values()))
    nb = math.sqrt(sum(x * x for x in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def unit_from_card(cid: str) -> str:
    m = re.search(r"(U\d+)", cid)
    return m.group(1) if m else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-sim", type=float, default=0.36, help="综合相似度下限（TF-IDF 与 claim 序列比取 max）")
    ap.add_argument("--min-fp", type=float, default=0.34, help="锚点指纹 Jaccard 下限（可与 min-sim 二选一达标）")
    ap.add_argument("--top-per-card", type=int, default=5, help="每张卡最多保留候选对数")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    cards = load_k_cards()
    fps = load_fingerprints()
    counters = [tokens(c["claim"]) for c in cards]
    vecs = tfidf_vectors(counters)
    pairs = []
    for i in range(len(cards)):
        for j in range(i + 1, len(cards)):
            if cards[i]["unit_id"] == cards[j]["unit_id"]:
                continue
            tf = cosine(vecs[i], vecs[j])
            seq = SequenceMatcher(None, cards[i]["claim"], cards[j]["claim"]).ratio()
            sim = max(tf, seq)
            fp = fingerprint_jaccard(
                fps.get(cards[i]["card_id"], set()),
                fps.get(cards[j]["card_id"], set()),
            )
            if sim < args.min_sim and fp < args.min_fp:
                continue
            score = max(sim, fp)
            pairs.append((score, sim, fp, i, j))
    pairs.sort(key=lambda x: -x[0])

    kept = []
    per_card = Counter()
    for score, sim, fp, i, j in pairs:
        if per_card[cards[i]["card_id"]] >= args.top_per_card:
            continue
        if per_card[cards[j]["card_id"]] >= args.top_per_card:
            continue
        per_card[cards[i]["card_id"]] += 1
        per_card[cards[j]["card_id"]] += 1
        kept.append((score, sim, fp, i, j))

    out = Path(args.out)
    fields = [
        "pair_id",
        "card_a",
        "card_b",
        "book_a",
        "book_b",
        "unit_a",
        "unit_b",
        "score",
        "sim_claim",
        "sim_fingerprint",
        "claim_a",
        "claim_b",
        "review_status",
        "relation_type",
    ]
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for n, (score, sim, fp, i, j) in enumerate(kept, start=1):
            a, b = cards[i], cards[j]
            w.writerow(
                {
                    "pair_id": f"P4P-{n:04d}",
                    "card_a": a["card_id"],
                    "card_b": b["card_id"],
                    "book_a": a["book_code"],
                    "book_b": b["book_code"],
                    "unit_a": a["unit_id"],
                    "unit_b": b["unit_id"],
                    "score": f"{score:.4f}",
                    "sim_claim": f"{sim:.4f}",
                    "sim_fingerprint": f"{fp:.4f}",
                    "claim_a": a["claim"][:120],
                    "claim_b": b["claim"][:120],
                    "review_status": "pending",
                    "relation_type": "",
                }
            )

    summary = ROOT / "ledger/P4_近似卡对_T-P4-03.md"
    summary.write_text(
        "\n".join(
            [
                "# T-P4-03｜近似卡对候选（2026-10-27）",
                "",
                f"| K 卡数 | {len(cards)} |",
                f"| 阈值 claim≥{args.min_sim} 或指纹≥{args.min_fp} | 原始 {len(pairs)} 对 |",
                f"| 裁剪后（每卡≤{args.top_per_card}） | **{len(kept)}** 对 |",
                f"| 输出 | `{out.relative_to(ROOT)}` |",
                "",
                "## 人工列",
                "",
                "- `review_status`: pending → same|variant|conflict|distinct",
                "- `relation_type`: §15.8 七类关系（归一后填）",
                "",
                "**下一工单**：T-P4-04 关系标注 + 冲突台账",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"T-P4-03: {len(cards)} K cards -> {len(kept)} pairs -> {out}")


if __name__ == "__main__":
    main()
