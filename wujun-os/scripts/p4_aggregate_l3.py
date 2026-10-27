#!/usr/bin/env python3
"""T-P4-06：按 L2 聚合 L3 模型簇（增长门 + 每 L2≤4 个 L3）"""
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSIGN = ROOT / "ledger/P4_归属表.csv"
REL = ROOT / "ledger/P4_卡对关系表.csv"
L3_OUT = ROOT / "ledger/P4_L3模型清单.csv"
L2_OUT = ROOT / "ledger/P4_L2清单.csv"
CARD_MAP_OUT = ROOT / "ledger/P4_卡到L3映射.csv"
REPORT = ROOT / "ledger/P4_L3聚合_T-P4-06.md"

MERGE_REL = {"同义重复", "同一机制、不同应用", "层次递进"}
MAX_L3_PER_L2 = 4
MIN_K = 3
MIN_UNITS = 2


class UF:
    def __init__(self):
        self.p = {}

    def add(self, x):
        self.p.setdefault(x, x)

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra


def load_assign():
    rows = []
    for r in csv.DictReader(ASSIGN.open(encoding="utf-8")):
        if r["status"] != "draft" or not r["primary_pillar"]:
            continue
        rows.append(r)
    return rows


def load_merge_edges(cards_primary: dict):
    edges = []
    if not REL.is_file():
        return edges
    for r in csv.DictReader(REL.open(encoding="utf-8")):
        if r["relation_type"] not in MERGE_REL:
            continue
        a, b = r["card_a"], r["card_b"]
        if a not in cards_primary or b not in cards_primary:
            continue
        if cards_primary[a] != cards_primary[b]:
            continue
        edges.append((a, b))
    return edges


def cluster_size(uf, members):
    roots = {uf.find(m) for m in members}
    groups = defaultdict(list)
    for m in members:
        groups[uf.find(m)].append(m)
    return list(groups.values())


def merge_smallest(groups):
    groups = [g for g in groups if g]
    if len(groups) <= 1:
        return groups
    groups.sort(key=len)
    small = groups.pop(0)
    groups[-1].extend(small)
    return groups


def main():
    assign = load_assign()
    cards_primary = {r["card_id"]: r["primary_pillar"] for r in assign}
    by_l2 = defaultdict(list)
    card_meta = {r["card_id"]: r for r in assign}
    for r in assign:
        by_l2[r["primary_pillar"]].append(r["card_id"])

    edges = load_merge_edges(cards_primary)
    l3_rows = []
    l2_rows = []
    card_map = []
    l3_seq = 0

    for l2, card_ids in sorted(by_l2.items()):
        uf = UF()
        for c in card_ids:
            uf.add(c)
        units = defaultdict(list)
        for c in card_ids:
            units[card_meta[c]["unit_id"]].append(c)
        for u_cards in units.values():
            for i in range(1, len(u_cards)):
                uf.union(u_cards[0], u_cards[i])
        for a, b in edges:
            if a in card_ids and b in card_ids:
                uf.union(a, b)

        groups = cluster_size(uf, card_ids)
        while len(groups) > MAX_L3_PER_L2:
            groups = merge_smallest(groups)
        changed = True
        while changed:
            changed = False
            groups.sort(key=len, reverse=True)
            new_groups = []
            orphans = []
            for g in groups:
                u_set = {card_meta[c]["unit_id"] for c in g}
                if len(g) >= MIN_K and len(u_set) >= MIN_UNITS:
                    new_groups.append(g)
                else:
                    orphans.extend(g)
            if orphans and new_groups:
                new_groups[-1].extend(orphans)
                changed = True
                groups = new_groups
            elif orphans and not new_groups:
                groups = [orphans]
                break
            else:
                groups = new_groups
                break

        books = {card_meta[c]["book_code"] for c in card_ids}
        l2_k = len(card_ids)
        l2_gate = "pass" if len(books) >= 2 and l2_k >= 12 else "thin_or_single_book"
        l2_rows.append(
            {
                "l2_code": l2,
                "l1_code": l2.split("-")[0],
                "k_count": l2_k,
                "book_count": len(books),
                "l3_count": len(groups),
                "l2_growth_gate": l2_gate,
            }
        )

        for i, g in enumerate(groups, start=1):
            l3_seq += 1
            l3_id = f"L3-{l3_seq:03d}"
            u_set = {card_meta[c]["unit_id"] for c in g}
            b_set = {card_meta[c]["book_code"] for c in g}
            gate = "pass" if len(g) >= MIN_K and len(u_set) >= MIN_UNITS else "merge_pending"
            sample = card_meta[g[0]]["card_id"]
            l3_rows.append(
                {
                    "l3_id": l3_id,
                    "l2_code": l2,
                    "l1_code": l2.split("-")[0],
                    "working_name": f"{l2}·簇{i}",
                    "k_count": len(g),
                    "unit_count": len(u_set),
                    "book_count": len(b_set),
                    "growth_gate": gate,
                    "card_ids": ";".join(sorted(g)),
                    "sample_card_id": sample,
                }
            )
            for c in g:
                card_map.append({"card_id": c, "l3_id": l3_id, "l2_code": l2})

    for path, rows, fields in (
        (L3_OUT, l3_rows, None),
        (L2_OUT, l2_rows, None),
        (CARD_MAP_OUT, card_map, None),
    ):
        fields = fields or (list(rows[0].keys()) if rows else [])
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    pending = sum(1 for r in l3_rows if r["growth_gate"] != "pass")
    REPORT.write_text(
        "\n".join(
            [
                "# T-P4-06｜L3 聚合（2026-10-27）",
                "",
                f"| 纳入 K 卡（draft） | {len(assign)} |",
                f"| L3 节点 | **{len(l3_rows)}** |",
                f"| L2 行 | **{len(l2_rows)}** |",
                f"| 增长门未过（merge_pending） | **{pending}** |",
                f"| 约束 | 每 L2≤{MAX_L3_PER_L2} L3；L3 目标 32–44（当前为机械聚类初稿） |",
                "",
                "**下一工单**：T-P4-07 L2 定稿与薄簇条款",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"T-P4-06: L3={len(l3_rows)} L2={len(l2_rows)} pending_gate={pending}")


if __name__ == "__main__":
    main()
