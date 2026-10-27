#!/usr/bin/env python3
"""validate_pillars.py — 校验 spec/pillars.yaml 一级 / 二级数量

期望：L1 = 10，L2 = 25（与 v2 §13.1、工程化总纲 T-00-02 一致）。

支持的机读结构（任选其一）:
  - 顶层 `l1` 或 `pillars`：长度为 10 的列表；每项下嵌套 `l2` 或 `children`（合计 25）
  - 或顶层同时有 `l1`（10 项）与扁平 `l2`（25 项，每项可有 parent / l1_code 指向一级）

文件缺失：退出码 2。
解析或数量不符：退出码 1。

用法（在仓库根目录 wujun-os/ 执行）:
  python3 scripts/validate_pillars.py
  python3 scripts/validate_pillars.py --path spec/pillars.yaml
"""
from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PATH = os.path.join(ROOT, "spec", "pillars.yaml")
EXPECTED_L1 = 10
EXPECTED_L2 = 25


def load_yaml(path: str):
    try:
        import yaml  # type: ignore
    except ImportError:
        print("validate_pillars: 需要 PyYAML（pip install pyyaml）", file=sys.stderr)
        raise SystemExit(1)
    with open(path, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    if doc is None:
        raise ValueError("pillars.yaml 为空")
    if not isinstance(doc, dict):
        raise ValueError("pillars.yaml 根节点必须是映射（mapping）")
    return doc


def _l1_list(doc: dict) -> list | None:
    for key in ("l1", "pillars", "L1"):
        val = doc.get(key)
        if val is not None:
            if not isinstance(val, list):
                raise ValueError(f"{key} 必须是列表")
            return val
    return None


def _nested_l2(item: dict) -> list:
    for key in ("l2", "l2_children", "children", "L2"):
        val = item.get(key)
        if val is None:
            continue
        if not isinstance(val, list):
            raise ValueError(f"一级项下的 {key} 必须是列表")
        return val
    return []


def count_levels(doc: dict) -> tuple[int, int]:
    l1_items = _l1_list(doc)
    flat_l2 = doc.get("l2") or doc.get("L2")

    if l1_items is not None:
        l1_count = len(l1_items)
        nested = sum(len(_nested_l2(it)) for it in l1_items if isinstance(it, dict))
        if nested:
            return l1_count, nested
        if flat_l2 is not None:
            if not isinstance(flat_l2, list):
                raise ValueError("l2 必须是列表")
            return l1_count, len(flat_l2)
        raise ValueError("未找到二级：一级项下无 l2/children，且顶层无 l2")

    if flat_l2 is not None:
        if not isinstance(flat_l2, list):
            raise ValueError("l2 必须是列表")
        parents = set()
        for row in flat_l2:
            if not isinstance(row, dict):
                continue
            p = row.get("parent") or row.get("l1_code") or row.get("l1")
            if p:
                parents.add(p)
        l1_count = len(parents) if parents else 0
        return l1_count, len(flat_l2)

    raise ValueError("缺少 l1/pillars 或 l2 结构")


def validate(path: str) -> int:
    if not os.path.isfile(path):
        print(f"validate_pillars: 缺少 {path}（由 SA1 落库 pillars.yaml）", file=sys.stderr)
        return 2

    try:
        doc = load_yaml(path)
        l1, l2 = count_levels(doc)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"validate_pillars: 解析失败 — {exc}", file=sys.stderr)
        return 1

    ok = l1 == EXPECTED_L1 and l2 == EXPECTED_L2
    print(f"validate_pillars: L1={l1} L2={l2}（期望 L1={EXPECTED_L1} L2={EXPECTED_L2}）")
    if not ok:
        print("validate_pillars: 数量与 v2 §13.1 不一致", file=sys.stderr)
        return 1
    print("validate_pillars: 通过")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="校验 pillars.yaml 一级 10、二级 25")
    ap.add_argument("--path", default=DEFAULT_PATH, help="pillars.yaml 路径")
    args = ap.parse_args()
    return validate(os.path.abspath(args.path))


if __name__ == "__main__":
    sys.exit(main())
