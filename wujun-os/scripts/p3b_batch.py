#!/usr/bin/env python3
"""P3b 批次流水线：probes | commit | lint（口径同 P3a，卡 ID 与锚点表为 P3b）"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import p3b_shared as ps

CARDS = ROOT / "cards"
VALID_TYPES = {"判断", "原理", "方法", "案例"}
VALID_CAPS = {"思", "学", "沟", "做"}
CARD_ID_RE = re.compile(r"P3b-[A-Z][A-Z0-9]{1,3}-U\d{4}-K\d{2}")


def _load_pillar_codes() -> set[str]:
    text = (ROOT / "spec/pillars.yaml").read_text(encoding="utf-8")
    return set(re.findall(r"code:\s*(D\d{2}(?:-\d)?)", text))


def cmd_probes(args):
    ids = ps.parse_batch_md(args.batch)
    out = {"batch_id": args.batch, "units": []}
    for uid in ids:
        u = ps.unit_record(uid)
        probe = ps.suggest_probe(uid)
        words = ""
        errs = []
        if probe:
            book = ps.load_book_text(u)
            pos = book.find(probe)
            if pos >= 0:
                s, e = ps.sent_span(book, pos)
                words = ps.pick_fingerprint_words(book[s:e])
            else:
                errs.append("探针未命中")
        else:
            errs.append("未找到唯一探针")
        out["units"].append({
            "unit_id": uid,
            "title": u["title"],
            "probe": probe,
            "words": words,
            "claim": "",
            "type": "原理",
            "pillar_hints": [],
            "errors": errs,
        })
    text = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
    Path(args.output).write_text(text, encoding="utf-8")
    print(f"已写入 {args.output}（{len(out['units'])} 单元）")


def cmd_commit(args):
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    batch_id = manifest.get("batch_id", "")
    units = manifest["units"]
    ledger_rows = []
    pillars_ok = _load_pillar_codes()
    for item in units:
        uid = item["unit_id"]
        u = ps.unit_record(uid)
        code = ps.book_code_from_unit(uid)
        probe = item.get("probe") or ps.suggest_probe(uid)
        if not probe:
            sys.exit(f"{uid}: 无探针")
        words = item.get("words") or ""
        if not words:
            book = ps.load_book_text(u)
            pos = book.find(probe)
            words = ps.pick_fingerprint_words(book[ps.sent_span(book, pos)[0] : ps.sent_span(book, pos)[1]])
        ve = ps.validate_words(probe, words, u)
        if ve:
            sys.exit(f"{uid}: {ve[0]}")
        claim = (item.get("claim") or "").strip()
        if not claim:
            sys.exit(f"{uid}: manifest 缺少 claim")
        typ = item.get("type", "原理")
        if typ not in VALID_TYPES:
            sys.exit(f"{uid}: type 须为 {VALID_TYPES}")
        ph = item.get("pillar_hints") or []
        for p in ph:
            if p not in pillars_ok:
                sys.exit(f"{uid}: 无效 pillar_hints {p}")
        speaker = (item.get("speaker") or "吴军本人").strip()
        cid = f"P3b-{uid}-K01"
        rc, out = ps.anchor_make(uid, probe, words, cid)
        if rc:
            sys.exit(f"{uid} anchor: {out}")
        ledger_rows.append(out.strip())
        caps = item.get("capability_tags")
        if not caps:
            caps = ["沟", "思"] if "问" in u["title"] or "答" in u["title"] else ["思", "做"]
        card = {
            "unit_id": uid,
            "book_code": code,
            "title": u["title"],
            "batch": batch_id,
            "disposition_unit": "K",
            "layer": "B",
            "cards": [{
                "card_id": cid,
                "speaker": speaker,
                "claim": claim,
                "type": typ,
                "disposition": "K",
                "pillar_hints": ph,
                "capability_tags": caps,
                "stable": "稳定",
            }],
        }
        d = CARDS / code
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{uid}.json").write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not ps.LEDGER_P3B.is_file():
        ps.LEDGER_P3B.write_text(
            "# 锚点表（P3b 来信问答 B 层）\n\n"
            "| 卡ID | 书文件名 | 行起 | 行止 | 字符起 | 字符止 | SHA1 | 指纹词 |\n"
            "|---|---|---|---|---|---|---|---|\n",
            encoding="utf-8",
        )
    ledger = ps.LEDGER_P3B.read_text(encoding="utf-8")
    first_cid = ledger_rows[0].split("|")[1].strip() if ledger_rows else ""
    if first_cid and first_cid not in ledger:
        ps.LEDGER_P3B.write_text(ledger.rstrip() + "\n" + "\n".join(ledger_rows) + "\n", encoding="utf-8")
    print(f"commit: {len(units)} 张卡 + 锚点")


def lint_card(path: Path, pillars_ok: set[str]) -> list[str]:
    errs = []
    doc = json.loads(path.read_text(encoding="utf-8"))
    uid = doc.get("unit_id", "")
    for c in doc.get("cards", []):
        sp = c.get("speaker", "")
        if not sp:
            errs.append(f"{uid}: speaker 为空")
        claim = c.get("claim", "")
        if not claim or len(claim) > 200:
            errs.append(f"{uid}: claim 空或超长(>200)")
        if c.get("type") not in VALID_TYPES:
            errs.append(f"{uid}: type 非法")
        for t in c.get("capability_tags") or []:
            if t not in VALID_CAPS:
                errs.append(f"{uid}: capability_tags 非法 {t}")
        for p in c.get("pillar_hints") or []:
            if p not in pillars_ok:
                errs.append(f"{uid}: pillar_hints 非法 {p}")
        cid = c.get("card_id", "")
        if not CARD_ID_RE.fullmatch(cid):
            errs.append(f"{uid}: card_id 须为 P3b-<书码>-Uxxxx-Knn，当前 {cid}")
    return errs


def cmd_lint(args):
    pillars_ok = _load_pillar_codes()
    paths = []
    for uid in ps.parse_batch_md(args.batch):
        code = ps.book_code_from_unit(uid)
        p = CARDS / code / f"{uid}.json"
        if not p.is_file():
            print(f"MISSING {p}")
            sys.exit(1)
        paths.append(p)
    all_errs = []
    for p in paths:
        all_errs.extend(lint_card(p, pillars_ok))
    if all_errs:
        for e in all_errs:
            print("FAIL", e)
        sys.exit(1)
    print(f"lint OK: {len(paths)} 张卡")


def main():
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd", required=True)
    pr = sp.add_parser("probes")
    pr.add_argument("--batch", required=True)
    pr.add_argument("-o", "--output", required=True)
    pr.set_defaults(func=cmd_probes)
    cm = sp.add_parser("commit")
    cm.add_argument("--manifest", required=True)
    cm.set_defaults(func=cmd_commit)
    lt = sp.add_parser("lint")
    lt.add_argument("--batch", required=True)
    lt.set_defaults(func=cmd_lint)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
