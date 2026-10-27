#!/usr/bin/env python3
"""P3b 批次共用：复用 p3a 探针/锚点逻辑，批次目录与锚点表分离"""
from __future__ import annotations

import re
from pathlib import Path

from p3a_shared import *  # noqa: F401,F403

ROOT = Path(__file__).resolve().parents[1]
LEDGER_P3B = ROOT / "ledger/锚点表_P3b.md"
BATCH_DIR_P3B = ROOT / "batches/P3b"


def parse_batch_md(batch_id: str) -> list[str]:
    path = BATCH_DIR_P3B / f"{batch_id}.md"
    if not path.is_file():
        raise FileNotFoundError(path)
    ids = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*([A-Z][A-Z0-9]{1,3}-U\d{4})\s*\|", line)
        if m:
            ids.append(m.group(1))
    if not ids:
        raise ValueError(f"{batch_id} 未解析到 unit_id")
    return ids
