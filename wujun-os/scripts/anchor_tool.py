#!/usr/bin/env python3
"""anchor_tool.py — 溯源锚点生成与校验（只读，不改原文）
生成: python3 anchor_tool.py make  --book 文件.md --probe "起句内任意≤15字短语" [--probe2 "止句内短语"] --words 词1,词2,词3 --id K-001
校验: python3 anchor_tool.py verify --ledger 溯源与处置台账.md --books-dir .
锚点 = 起句至止句的 [字符起,字符止) + 行号 + SHA1（上限800字，句末以。！？或空行为界，硬换行不影响）；字符位置按 UTF-8 解码后的 Python 字符串下标计。
"""
import sys, re, hashlib, argparse, os

def load(path):
    raw = open(path, 'rb').read()
    return raw.decode('utf-8')

def sent_span(text, pos):
    s = pos
    while s > 0 and text[s-1] not in '。！？' and text[max(0, s-2):s] != '\n\n':
        s -= 1
    e, n = pos, len(text)
    while e < n:
        if text[e] in '。！？':
            e += 1
            while e < n and text[e] in '”’」』）':
                e += 1
            break
        if text[e:e+2] == '\n\n':
            break
        e += 1
    while s < e and text[s] in ' \n\t':
        s += 1
    return s, e

def make(a):
    text = load(a.book)
    pos = text.find(a.probe)
    if pos < 0 or text.count(a.probe) != 1:
        sys.exit(f'探针短语需在文件中恰好出现1次，当前出现 {text.count(a.probe)} 次')
    s, e = sent_span(text, pos)
    if a.probe2:
        p2 = text.find(a.probe2, pos)
        if p2 < 0 or text.count(a.probe2) != 1:
            sys.exit('probe2 需在文件中恰好出现1次且位于 probe 之后')
        e = sent_span(text, p2)[1]
    if e - s > 800:
        sys.exit(f'锚点过长({e-s}字>800)，请拆成多条论点卡')
    seg = text[s:e]
    words = [w for w in a.words.split(',') if w] if a.words else []
    miss = [w for w in words if w not in seg]
    if miss: sys.exit(f'指纹词不在该段内: {miss}')
    ls = text.count('\n', 0, s) + 1
    le = text.count('\n', 0, e) + 1
    h = hashlib.sha1(seg.encode('utf-8')).hexdigest()
    print(f'| {a.id} | {os.path.basename(a.book)} | {ls} | {le} | {s} | {e} | {h} | {",".join(words)} |')

def verify(a):
    ok = bad = 0
    cache = {}
    for line in open(a.ledger, encoding='utf-8'):
        if not line.startswith('|'): continue
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(c) < 8 or not re.fullmatch(r'\d+', c[2]) : continue
        cid, book, ls, le, cs, ce, sha, words = c[0], c[1], int(c[2]), int(c[3]), int(c[4]), int(c[5]), c[6], c[7]
        path = os.path.join(a.books_dir, book)
        if book not in cache: cache[book] = load(path)
        t = cache[book]; seg = t[cs:ce]
        errs = []
        if hashlib.sha1(seg.encode('utf-8')).hexdigest() != sha: errs.append('SHA1不符')
        if t.count('\n', 0, cs) + 1 != ls or t.count('\n', 0, ce) + 1 != le: errs.append('行号不符')
        for w in [w for w in words.split(',') if w]:
            if w not in seg: errs.append(f'指纹词缺失:{w}')
        if errs: bad += 1; print('FAIL', cid, book, errs)
        else: ok += 1
    print(f'校验完成: 通过 {ok}，失败 {bad}')
    sys.exit(1 if bad else 0)

p = argparse.ArgumentParser(); sp = p.add_subparsers(dest='cmd', required=True)
m = sp.add_parser('make'); m.add_argument('--book', required=True); m.add_argument('--probe', required=True); m.add_argument('--probe2', default=''); m.add_argument('--words', default=''); m.add_argument('--id', required=True); m.set_defaults(f=make)
v = sp.add_parser('verify'); v.add_argument('--ledger', required=True); v.add_argument('--books-dir', default='.'); v.set_defaults(f=verify)
a = p.parse_args(); a.f(a)
