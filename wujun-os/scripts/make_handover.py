#!/usr/bin/env python3
"""make_handover.py — 由 state/state.json 与 state/STATE.md 生成交接摘要

用法（在仓库根目录 wujun-os/ 执行）:
  python3 scripts/make_handover.py

输出: handover/项目交接文档_生成.md
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone


def repo_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def bar(done: int, total: int, width: int = 20) -> str:
    if not total:
        return "[" + "-" * width + "] 0.0%"
    n = int(width * done / total)
    return "[" + "#" * n + "-" * (width - n) + f"] {100 * done / total:.1f}%"


def esc_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def split_next_steps(next_ticket: str) -> list[str]:
    parts = re.split(r"\s*→\s*", next_ticket.strip())
    return [p.strip() for p in parts if p.strip()]


def render(root: str) -> str:
    state_json = os.path.join(root, "state", "state.json")
    state_md = os.path.join(root, "state", "STATE.md")
    for p in (state_json, state_md):
        if not os.path.isfile(p):
            raise SystemExit(f"缺少输入文件: {p}")

    checksum = sha256_file(state_json)
    with open(state_json, encoding="utf-8") as f:
        s = json.load(f)
    with open(state_md, encoding="utf-8") as f:
        state_md_text = f.read()

    pr = s.get("progress", {})
    inf = s.get("in_flight", {})
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines: list[str] = []
    lines.append("# 项目交接文档（自动生成）\n")
    lines.append("| 项 | 内容 |")
    lines.append("|---|---|")
    lines.append(f"| 生成时间 | {generated_at} |")
    lines.append(f"| state.json 校验和 (SHA256) | `{checksum}` |")
    lines.append(f"| state.json.updated | {esc_cell(str(s.get('updated', '—')))} |")
    lines.append(
        f"| STATE.md | 已读取（{len(state_md_text.splitlines())} 行，"
        f"与 state.json.updated={esc_cell(str(s.get('updated', '—')))} 对齐渲染） |"
    )
    lines.append(
        "\n> 若 `state/state.json` 已变更而本文校验和不符，请重新运行 "
        "`python3 scripts/make_handover.py`。\n"
    )

    lines.append("## 状态摘要\n")
    lines.append("| 项 | 内容 |")
    lines.append("|---|---|")
    summary_rows = [
        ("项目", s.get("project", "—")),
        ("包版本", s.get("pack_version", "—")),
        ("最后更新", s.get("updated", "—")),
        ("阶段", s.get("phase", "—")),
        ("步骤说明", s.get("step", "—")),
        ("冻结状态", json.dumps(s.get("frozen", {}), ensure_ascii=False)),
        ("规格版本", json.dumps(s.get("spec", {}), ensure_ascii=False)),
        ("进行中备注", inf.get("note", "—")),
    ]
    for k, v in summary_rows:
        lines.append(f"| {esc_cell(str(k))} | {esc_cell(str(v))} |")

    lines.append("\n## 工单\n")
    lines.append("| 项 | 内容 |")
    lines.append("|---|---|")
    ticket_rows = [
        ("上一张工单", s.get("last_ticket", "—")),
        ("下一张工单", s.get("next_ticket", "—")),
        ("in_flight.ticket", inf.get("ticket")),
        ("处理中的单元", json.dumps(inf.get("unit_ids", []), ensure_ascii=False)),
        ("尚未落盘", json.dumps(inf.get("unsaved", []), ensure_ascii=False)),
    ]
    for k, v in ticket_rows:
        lines.append(f"| {esc_cell(str(k))} | {esc_cell(str(v))} |")

    lines.append("\n## 阻塞\n")
    blocked = s.get("blocked_by") or []
    if blocked:
        lines.append("| # | 阻塞项 |")
        lines.append("|---|---|")
        for i, item in enumerate(blocked, 1):
            lines.append(f"| {i} | {esc_cell(item)} |")
    else:
        lines.append("| # | 阻塞项 |")
        lines.append("|---|---|")
        lines.append("| — | 无 |")

    lines.append("\n## 进度\n")
    lines.append("| 指标 | 当前/总量 | 进度 |")
    lines.append("|---|---|---|")
    u_done, u_total = pr.get("units_done", 0), pr.get("units_total", 0)
    c_done, c_total = pr.get("chars_done", 0), pr.get("chars_total", 0)
    lines.append(
        f"| 单元 | {u_done}/{u_total}（内容单元 {pr.get('units_content', '—')}） | "
        f"{bar(u_done, u_total)} |"
    )
    lines.append(
        f"| 汉字 | {c_done:,}/{c_total:,} | {bar(c_done, c_total)} |"
    )
    lines.append(
        f"| 批次 | {pr.get('batches_done', 0)}/{pr.get('batches_est', '—')} | — |"
    )
    est = s.get("estimates", {})
    if est:
        lines.append(
            f"| 轮次估算（乐观/保守） | {esc_cell(est.get('rounds_optimistic', '—'))} / "
            f"{esc_cell(est.get('rounds_conservative', '—'))} | EP-0: {esc_cell(est.get('EP-0', '—'))} |"
        )

    lines.append("\n## 下一步\n")
    lines.append("| 序号 | 事项 | 类型 |")
    lines.append("|---|---|---|")
    steps = split_next_steps(str(s.get("next_ticket", "")))
    for i, step in enumerate(steps, 1):
        lines.append(f"| {i} | {esc_cell(step)} | 工单链 |")
    base = len(steps)
    for j, item in enumerate(s.get("open_items") or [], 1):
        lines.append(f"| {base + j} | {esc_cell(item)} | 待确认 |")

    return "\n".join(lines) + "\n"


def main() -> None:
    root = repo_root()
    os.chdir(root)
    out_path = os.path.join(root, "handover", "项目交接文档_生成.md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    content = render(root)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"已写入: {out_path}")


if __name__ == "__main__":
    main()
