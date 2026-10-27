#!/usr/bin/env python3
"""T-P4-12：K 卡冻结快照 + K 降级审计表"""
import csv
import hashlib
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSIGN = ROOT / "ledger/P4_归属表.csv"
SPOT = ROOT / "ledger/P4_抽查20张.csv"
KAPPA = ROOT / "ledger/P4_盲重标κ报告.md"
AUDIT_OUT = ROOT / "ledger/K降级审计表.csv"
FREEZE_JSON = ROOT / "data/k_card_freeze.json"
REPORT = ROOT / "ledger/P4_K卡冻结_2026-10-27.md"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def kappa_l1() -> float:
    m = re.search(r"κ（L1 柱）\s*\|\s*\*\*([0-9.]+)\*\*", KAPPA.read_text(encoding="utf-8"))
    return float(m.group(1)) if m else 0.0


def spot_errors() -> int:
    rows = list(csv.DictReader(SPOT.open(encoding="utf-8")))
    return sum(1 for r in rows if (r.get("归属明显错误") or "").strip() == "Y")


def main():
    gates = []
    k1 = kappa_l1()
    gates.append(("AC-4.4 κ_L1≥0.6", k1 >= 0.6, f"{k1:.3f}"))
    if not SPOT.is_file():
        gates.append(("AC-4.8 抽查表存在", False, "missing"))
    else:
        err = spot_errors()
        filled = all((r.get("归属明显错误") or "").strip() for r in csv.DictReader(SPOT.open(encoding="utf-8")))
        gates.append(("AC-4.8 抽查已填", filled, "ok" if filled else "empty"))
        gates.append(("AC-4.8 归属错≤3", err <= 3, f"{err}"))

    if not all(ok for _, ok, _ in gates):
        for name, ok, detail in gates:
            if not ok:
                print(f"GATE FAIL: {name} ({detail})")
        raise SystemExit(1)

    assign_rows = list(csv.DictReader(ASSIGN.open(encoding="utf-8")))
    k_cards = [r for r in assign_rows if r["status"] == "draft"]
    audit = []
    for r in assign_rows:
        if r["status"] == "x_hint_only":
            audit.append(
                {
                    "card_id": r["card_id"],
                    "from": "K",
                    "to": "X/M待P4",
                    "reason": "仅 X 子类 pillar_hints，无 D 归属",
                    "status": "open",
                }
            )

    fields = ["card_id", "from", "to", "reason", "status"]
    with AUDIT_OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(audit)

    snap = {
        "date": date.today().isoformat(),
        "ticket": "T-P4-12",
        "k_cards_frozen": len(k_cards),
        "sha256_P4_归属表": sha256_file(ASSIGN),
        "sha256_P4_L3模型清单": sha256_file(ROOT / "ledger/P4_L3模型清单.csv"),
        "kappa_L1": k1,
        "spot_check_errors": spot_errors(),
        "downgrade_open": len(audit),
    }
    FREEZE_JSON.write_text(json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    REPORT.write_text(
        "\n".join(
            [
                "# T-P4-12｜K 卡冻结（2026-10-27）",
                "",
                f"| 冻结 K 卡（draft） | **{len(k_cards)}** |",
                f"| κ_L1 | {k1:.3f} |",
                f"| 抽查归属错 | {spot_errors()} |",
                f"| 降级审计 open | {len(audit)} |",
                f"| 快照 | `data/k_card_freeze.json` |",
                "",
                "**开放**：D10 三道门未过；L2/L3 低于目标区间——不阻止 K 分母锁定，成稿阶段再调簇。",
                "",
                "**下一工单**：T-P4-13 字典变更报告",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"T-P4-12: frozen K={len(k_cards)} audit_open={len(audit)}")


if __name__ == "__main__":
    main()
