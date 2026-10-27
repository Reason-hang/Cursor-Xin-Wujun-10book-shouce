#!/usr/bin/env python3
"""复算单元处置率（AC-0.1）：以 cards/*.json 为 SSOT，更新 state.json 进度与审计 md。"""
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "cards"
STATE = ROOT / "state/state.json"
OUT = ROOT / "ledger/P3_单元处置率审计.md"


def main() -> int:
    units = json.loads((ROOT / "data/units_index.json").read_text(encoding="utf-8"))["units"]
    disp_u: Counter[str] = Counter()
    k_units = 0
    chars_total = 0
    chars_k = 0
    chars_disposed = 0
    missing = []

    for u in units:
        uid = u["unit_id"]
        ch = int(u.get("chars") or 0)
        chars_total += ch
        p = CARDS / u["book_code"] / f"{uid}.json"
        if not p.is_file():
            missing.append(uid)
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        du = d.get("disposition_unit") or "?"
        disp_u[du] += 1
        chars_disposed += ch
        has_k = du == "K" or any(c.get("disposition") == "K" for c in d.get("cards", []))
        if has_k:
            k_units += 1
            chars_k += ch

    disposed = len(units) - len(missing)
    today = date.today().isoformat()
    lines = [
        f"# P3 单元处置率审计（{today}）",
        "",
        "| 指标 | 值 |",
        "|---|---|",
        f"| 单元总数 | {len(units)} |",
        f"| 已落盘 cards（处置完成） | **{disposed}** |",
        f"| 无卡 | {len(missing)} |",
        f"| 含 K 主张单元 | {k_units} |",
        f"| disposition_unit 分布 | {dict(disp_u)} |",
        f"| 汉字（已处置） | {chars_disposed:,} / {chars_total:,} |",
        f"| 汉字（含 K） | {chars_k:,} |",
        "",
        "说明：`units_done` 进度条按 **已处置单元** 计；K 数量见 `k_units`（P4 冻结仍为 532 时需另工单增量冻结）。",
    ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    state = json.loads(STATE.read_text(encoding="utf-8"))
    pr = state.setdefault("progress", {})
    pr["units_done"] = disposed
    pr["chars_done"] = chars_disposed
    pr["k_units"] = k_units
    pr["cards_present"] = disposed
    pr["disposition_breakdown"] = dict(disp_u)
    state["updated"] = today
    if not missing:
        state["phase"] = "P3 单元处置率 100%（cards）；P7 人审用户延后"
        state["step"] = f"K 单元 {k_units}；P4 冻结 K=532 与现网 {k_units} 差量待你决定是否重冻"
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"P3 disposition: {disposed}/{len(units)} disposed, K={k_units} -> {OUT}")
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
