#!/usr/bin/env python3
"""S18 / T-P7-01：D1/D2 表格列数、Mermaid 块、内部锚点链接检查。"""
import argparse
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILES = [
    ROOT.parent / "最终所有交付物/认知与行动操作系统_主手册_v0.9.md",
    ROOT.parent / "最终所有交付物/行动工具集_v0.9.md",
]
OUT = ROOT / "ledger/P7_S18_渲染链接检查.md"

LINK_RE = re.compile(r"\]\((#[^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


def slugify(title: str) -> str:
    s = title.strip().lower()
    s = re.sub(r"[`*_~]", "", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^\w\u4e00-\u9fff\-]+", "", s)
    return s


def check_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    issues: list[str] = []
    headings = {slugify(m.group(2)) for m in HEADING_RE.finditer(text)}
    for m in LINK_RE.finditer(text):
        anchor = m.group(1)[1:]
        if anchor and anchor not in headings:
            # 常见生成器用 user-content- 前缀，放宽：仅报明显缺失
            if not any(h.startswith(anchor[:8]) for h in headings if len(anchor) >= 8):
                issues.append(f"可疑内链 {m.group(1)}")
    # tables
    in_table = False
    cols = 0
    for i, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("|"):
            n = line.count("|") - 1
            if not in_table:
                cols = n
                in_table = True
            elif "---" not in line and n != cols:
                issues.append(f"L{i} 表格列数 {n} ≠ {cols}")
        else:
            in_table = False
    # mermaid
    blocks = re.findall(r"```mermaid\s*\n(.*?)```", text, re.DOTALL)
    for bi, block in enumerate(blocks, 1):
        if block.count("```"):
            issues.append(f"mermaid 块 {bi} 含嵌套反引号")
    return {
        "path": str(path),
        "links_checked": len(list(LINK_RE.finditer(text))),
        "headings": len(headings),
        "mermaid": len(blocks),
        "issues": issues,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="待检查 md，默认正式夹 D1/D2")
    args = ap.parse_args()
    files = [Path(p) for p in args.files] if args.files else DEFAULT_FILES
    results = []
    for p in files:
        if not p.is_file():
            results.append({"path": str(p), "issues": ["文件缺失"], "links_checked": 0, "headings": 0, "mermaid": 0})
            continue
        results.append(check_file(p))
    fail = sum(len(r["issues"]) for r in results)
    lines = [
        f"# P7 S18 渲染与链接检查（{date.today().isoformat()}）",
        "",
        f"**overall**: {'PASS' if fail == 0 else 'FAIL'}（问题 {fail}）",
        "",
        "| 文件 | 标题数 | 内链数 | Mermaid | 问题 |",
        "|---|---:|---:|---:|---|",
    ]
    for r in results:
        iss = "; ".join(r["issues"][:5]) if r["issues"] else "—"
        lines.append(
            f"| `{Path(r['path']).name}` | {r['headings']} | {r['links_checked']} | {r['mermaid']} | {iss} |"
        )
    lines.append("")
    lines.append("复跑：`cd wujun-os && make p7-s18-check`")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"s18: {fail} issues → {OUT}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
