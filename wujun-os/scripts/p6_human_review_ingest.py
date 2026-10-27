#!/usr/bin/env python3
"""将 ledger/P6_人审提交.txt 写入签收表与试用记录（须用户自填，禁止占位符）。"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "ledger/P6_人审提交.txt"
SIGN = ROOT / "ledger/P6_对抗式审查_签收表.md"
TRIAL = ROOT / "ledger/P6_用户试用记录.md"

ROW_KEYS = [
    ("逻辑", "逻辑：D10 fail 与第 10 章并存已知情"),
    ("事实", "事实：锚点 SHA 与 claim 语义分离已知情"),
    ("边界", "边界：D09/T-13 非投资建议声明足够"),
    ("过度设计", "过度设计：50 M / 532 K 冻结策略接受"),
    ("遗漏", "遗漏：SG1 仅 39/386 高信号 K（非全量）；A 层无 JSON 已登记"),
    ("G10语义", "G10 机械 100% 不等于语义全覆盖已知情"),
]

BAD = re.compile(r"待填|你的姓名|PLACEHOLDER|替换为真名|【", re.I)


def parse_sections(text: str) -> dict[str, dict[str, str]]:
    cur = None
    data: dict[str, dict[str, str]] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"\[([^\]]+)\]", line)
        if m:
            cur = m.group(1).strip()
            data.setdefault(cur, {})
            continue
        if cur and "=" in line:
            k, v = line.split("=", 1)
            data[cur][k.strip()] = v.strip()
    return data


def yn(v: str) -> str:
    v = v.strip().upper()
    if v not in ("Y", "N"):
        raise ValueError(f"须为 Y/N，当前: {v!r}")
    return v


def assert_real(val: str, field: str) -> str:
    val = (val or "").strip()
    if not val or BAD.search(val):
        raise ValueError(f"{field} 未填或仍为模板占位")
    return val


def apply_signoff(sec: dict[str, str]) -> None:
    vals = {k: yn(sec[k]) for k, _ in ROW_KEYS}
    name = assert_real(sec.get("签收", ""), "签收")
    d = assert_real(sec.get("日期", ""), "日期")
    header = """# AC-6.9 对抗式审查签收表

依据：`ledger/P6_对抗式审查_草稿.md`（五角度 + 高风险点）。

| 项 | 你确认（Y/N） | 备注 |
|---|---|---|
"""
    rows = "\n".join(f"| {label} | {vals[key]} | |" for key, label in ROW_KEYS)
    footer = f"""
**签收**：{name}　日期：{d}

签收后由 R-ORCH 更新 D4 AC-6.9 为 PASS，并 `make p6-report`.
"""
    SIGN.write_text(header + rows + footer, encoding="utf-8")


def result_mark(choice: str) -> str:
    c = choice.strip()
    if "已解决" in c:
        return "☑ 已解决 □ 部分 □ 未覆盖"
    if "部分" in c:
        return "□ 已解决 ☑ 部分 □ 未覆盖"
    if "未覆盖" in c:
        return "□ 已解决 □ 部分 ☑ 未覆盖"
    raise ValueError(f"Q结果须含 已解决/部分/未覆盖: {c!r}")


def apply_trial(sec: dict[str, str]) -> None:
    name = assert_real(sec.get("签字", ""), "签字")
    d = assert_real(sec.get("日期", ""), "日期")
    parts = ["# P6 用户试用记录（AC-6.10）\n\n> 由 `P6_人审提交.txt` ingest 生成。\n\n"]
    for i in range(1, 4):
        bg = assert_real(sec.get(f"Q{i}背景", ""), f"Q{i}背景")
        ent = assert_real(sec.get(f"Q{i}入口", ""), f"Q{i}入口")
        res = result_mark(sec.get(f"Q{i}结果", ""))
        parts.append(
            f"## 问题 {i}\n\n| 项 | 内容 |\n|---|---|\n"
            f"| 背景 | {bg} |\n| 查阅入口（S-/T-/D章） | {ent} |\n"
            f"| 结果 | {res} |\n| 备注 | |\n\n"
        )
    parts.append(f"**签字**：{name}　日期：{d}\n")
    TRIAL.write_text("".join(parts), encoding="utf-8")


def main() -> int:
    if not SRC.is_file():
        print("FAIL: 复制 ledger/P6_人审提交_模板.txt → P6_人审提交.txt 并填写")
        return 1
    text = SRC.read_text(encoding="utf-8")
    if BAD.search(text):
        print("FAIL: 提交文件仍含模板占位（你的姓名/待填等）")
        return 1
    data = parse_sections(text)
    if "6.9" not in data or "6.10" not in data:
        print("FAIL: 缺少 [6.9] 或 [6.10] 段")
        return 1
    try:
        apply_signoff(data["6.9"])
        apply_trial(data["6.10"])
    except (ValueError, KeyError) as e:
        print(f"FAIL: {e}")
        return 1
    print(f"ingest OK → {SIGN.name} + {TRIAL.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
