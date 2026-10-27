#!/usr/bin/env python3
"""人审与 6.3 全绿后：阶段验收收尾说明入正式夹 + 刷新 pack（须 p7-ready-lint PASS）。"""
import hashlib
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DELIVER = ROOT.parent / "最终所有交付物"
OUT_DOC = DELIVER / "WJ-OS｜P7阶段验收｜交付说明.md"
PACK_GLOB = "wujun-os-pack_*.zip"


def latest_pack_sha() -> tuple[str, str]:
    packs = sorted(DELIVER.glob(PACK_GLOB))
    if not packs:
        return "—", "—"
    p = packs[-1]
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return p.name, h.hexdigest()


def main() -> int:
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts/p7_ready_lint.py")],
        cwd=ROOT,
    )
    if r.returncode != 0:
        print("FAIL: p7-ready-lint 未 PASS；先完成人审与 6.3（见 P6_阶段验收_用户动作清单.md）")
        return 1
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/p7_stage_acceptance_audit.py")],
        cwd=ROOT,
        check=False,
    )
    subprocess.run([sys.executable, str(ROOT / "scripts/p6_report.py")], cwd=ROOT, check=True)
    pack_name, sha = latest_pack_sha()
    body = f"""# WJ-OS｜P7 阶段验收｜交付说明

| 日期 | {date.today().isoformat()} |
|---|---|
| 里程碑 | M4（P7）阶段验收机械项 PASS |
| 恢复包 | `{pack_name}` |
| SHA-256 | `{sha}` |

## 验收证据（可复算）

```bash
cd wujun-os
make p7-acceptance-audit
make p7-ready-lint
make deliver-audit
make restore-check
```

- 审计：`ledger/P7_阶段验收审计.md`、`ledger/P7_正式夹审计.md`
- 人审落盘：`ledger/P6_AC6_人审落盘记录.md`（若已 `make p6-human-review-apply`）

## 正式夹 D1–D6

与 `out/` 对账见 `make deliver-audit`。G10③ 仍为登记例外（非刷绿）。

## 版本说明

当前文件名仍为 **v0.9**；若你确认升 **v1.0**，在批复中写明后由下一轮 `pack` 统一改名。
"""
    DELIVER.mkdir(parents=True, exist_ok=True)
    OUT_DOC.write_text(body, encoding="utf-8")
    print(f"p7 closeout → {OUT_DOC}")
    subprocess.run(["make", "pack"], cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
