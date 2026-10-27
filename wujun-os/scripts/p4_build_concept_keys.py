#!/usr/bin/env python3
"""T-P4-02：从 P3a/P3b 批末回顾 harvest 概念短语，归一并写出 rules/concept_keys.csv"""
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_RULES = ROOT / "rules/concept_keys.csv"
OUT_DATA = ROOT / "data/concept_keys.csv"
REPORT = ROOT / "ledger/P4_概念键归一_T-P4-02.md"

PILLAR_REF = re.compile(r"^D\d{2}(-\d)?([\s·]|$)")
SKIP_WORDS = ("呼应", "子链", "双出处", "与已", "登记", "聚类")


def split_phrases(s: str) -> list[str]:
    s = re.sub(r"（[^）]*）", "", s)
    s = re.sub(r"\([^)]*\)", "", s)
    parts = re.split(r"[、,，；;]|(?:\s+与\s+)", s)
    out = []
    for p in parts:
        p = p.strip().strip("「」\"\"")
        p = re.sub(r"\s+", "", p)
        if not p or len(p) < 2:
            continue
        if any(w in p for w in SKIP_WORDS):
            continue
        if PILLAR_REF.match(p):
            continue
        if re.match(r"^D\d{2}", p):
            continue
        out.append(p[:24])
    return out


def harvest() -> Counter:
    counts: Counter = Counter()
    sources: dict[str, set[str]] = defaultdict(set)
    for p in sorted((ROOT / "batches").rglob("*.md")):
        if "/P3a/" not in str(p) and "/P3b/" not in str(p):
            continue
        rel = str(p.relative_to(ROOT))
        t = p.read_text(encoding="utf-8")
        for block in re.findall(r"### 概念键\s*\n+(.*?)(?=\n### |\n## |\Z)", t, re.S):
            for line in block.splitlines():
                if "本批新增" not in line:
                    continue
                if "|" in line:
                    cells = [c.strip() for c in line.strip().strip("|").split("|")]
                    text = cells[-1] if len(cells) >= 2 else line
                else:
                    text = line.split("：", 1)[-1] if "：" in line else line
                for ph in split_phrases(text):
                    counts[ph] += 1
                    sources[ph].add(rel)
        m = re.search(r"## 2\. [^\n]*概念键[^\n]*\n\n([^\n#]+)", t)
        if m:
            for ph in split_phrases(m.group(1)):
                counts[ph] += 1
                sources[ph].add(rel)
    return counts, sources


# 人工归并：别名 → 规范名（P4-02 首轮，后续写入 precedents）
CANONICAL_MERGE = {
    "主人道德": "主人/奴隶道德",
    "奴隶道德": "主人/奴隶道德",
    "理性主义": "理性主义方法论",
    "苏格兰启蒙": "苏格兰启蒙与英美经验路径",
    "尼采": "尼采与积极虚无主义",
    "维特根斯坦": "维特根斯坦语言界限与语言游戏",
    "黑格尔": "黑格尔三层历史",
    "超越免费": "超越免费五法则",
    "未来八": "未来八特征",
    "面对面传播": "面对面口头传播",
}


def normalize_name(name: str) -> str:
    n = name.strip()
    for k, v in CANONICAL_MERGE.items():
        if n == k or (k in n and len(n) <= len(v) + 2):
            return v
    return n


def build_rows(counts: Counter, sources: dict) -> list[dict]:
    bucket: dict[str, Counter] = defaultdict(Counter)
    src_bucket: dict[str, set[str]] = defaultdict(set)
    for name, n in counts.items():
        canon = normalize_name(name)
        bucket[canon][name] += n
        src_bucket[canon].update(sources[name])
    rows = []
    for i, canon in enumerate(sorted(bucket.keys(), key=lambda x: (-sum(bucket[x].values()), x)), start=1):
        aliases = [a for a in bucket[canon] if a != canon]
        rows.append(
            {
                "concept_id": f"CK-{i:04d}",
                "canonical_name": canon,
                "aliases": ";".join(sorted(aliases)),
                "mention_count": sum(bucket[canon].values()),
                "source_files": ";".join(sorted(src_bucket[canon])[:8]),
                "status": "active",
            }
        )
    return rows


def main():
    counts, sources = harvest()
    rows = build_rows(counts, sources)
    OUT_RULES.parent.mkdir(parents=True, exist_ok=True)
    fields = ["concept_id", "canonical_name", "aliases", "mention_count", "source_files", "status"]
    for path in (OUT_RULES, OUT_DATA):
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
    dup_exact = sum(1 for n, c in counts.items() if c > 1)
    lines = [
        "# T-P4-02｜概念键归一（2026-10-27）",
        "",
        f"| 项 | 值 |",
        f"|---|---|",
        f"| harvest 原始短语 | {sum(counts.values())} 次 / **{len(counts)}** 个 |",
        f"| 归一后概念键 | **{len(rows)}** |",
        f"| 输出 | `rules/concept_keys.csv`（权威）+ `data/concept_keys.csv`（镜像） |",
        f"| 完全重复短语（合并为别名） | {dup_exact} |",
        "",
        "## 验收",
        "",
        "- `make p4-lint-concept-keys`：canonical 唯一、CK 连续、别名不跨键",
        "- **下一工单**：T-P4-03 近似卡对（`scripts/s14_overlap` 扩展 / TF-IDF 候选表）",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    meta = {"raw_unique": len(counts), "keys": len(rows), "path": str(OUT_RULES)}
    (ROOT / "data/p4_concept_keys_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"T-P4-02: {len(rows)} keys -> {OUT_RULES}")


if __name__ == "__main__":
    main()
