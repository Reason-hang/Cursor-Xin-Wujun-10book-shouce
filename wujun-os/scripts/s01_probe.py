#!/usr/bin/env python3
"""s01_probe.py — P0 前置探测（可复跑，只读）
用法（在仓库根目录 wujun-os/ 执行）:
  python3 scripts/s01_probe.py --src src_frozen --out logs/p0_probe.md                # 与基线比对
  python3 scripts/s01_probe.py --src src_frozen --write-baseline spec/baseline_facts.json   # 首次生成基线（仅在核对无误后）
作用: 按 v2 方案 §5.6 / §6 的口径切分单元并复算前置数字（单元数、容器与非内容、编号连续性、
      谷歌作者目录对账、精确重复段落、划重点、问答体量、系列单元）。与 spec/baseline_facts.json 比对，任何不符返回非零。
"""
import argparse, collections, glob, hashlib, itertools, json, os, re, sys

CJK = re.compile(r'[\u4e00-\u9fff]')
# 文件名关键词 -> (书名, 书码, 单元标题层级)；顺序即匹配优先级
BOOKS = [('来信1', '硅谷来信1', 'SG1', 2), ('来信2', '吴军来信2', 'WJ2', 2), ('来信3', '硅谷来信3', 'SG3', 2),
         ('谷歌方法论', '谷歌方法论', 'GG', 2), ('见识', '见识', 'JS', 2), ('数学通识', '数学通识50讲', 'SX', 3),
         ('格局', '格局', 'GJ', 2), ('境界', '境界', 'JJ', 3), ('富足', '富足', 'FZ', 3), ('态度', '态度', 'TD', 2)]
NONCONTENT = re.compile(r'^目录$|^《.*》目录$|导航|第二季来啦|收藏丨|^谷歌方法论：')
QA = re.compile(r'答读者问|周末问答|回用户|回同学')
INTERACT = re.compile(r'周末互动|周末放送|回信精选|精选')
SERIES = re.compile(r'[（(](上|下|中|一|二|三|四|五)[）)]|[上下]篇|之[一二三四]')

def cjk(s):
    return len(CJK.findall(s))

def load(src):
    out = {}
    for p in sorted(glob.glob(os.path.join(src, '*.md'))):
        name = os.path.basename(p)
        for key, book, code, lvl in BOOKS:
            if key in name:
                out[code] = dict(path=p, book=book, lvl=lvl, text=open(p, 'rb').read().decode('utf-8'))
                break
    return out

def split_units(text, lvl):
    lines = text.split('\n')
    units, cur, start, buf = [], None, 0, 0
    for i, l in enumerate(lines):
        m = re.match(r'^(#{1,6})\s+(.*)', l)
        if m and len(m.group(1)) <= lvl:
            if cur is not None:
                units.append(dict(title=cur, start=start, end=i, chars=buf))
            cur, start, buf = m.group(2).strip(), i, 0
        else:
            buf += cjk(l)
    if cur is not None:
        units.append(dict(title=cur, start=start, end=len(lines), chars=buf))
    for u in units:
        u['text'] = '\n'.join(lines[u['start']:u['end']])
        u['cls'] = 'N' if NONCONTENT.search(u['title']) else ('S' if u['chars'] < 100 else 'C')
    return units

def numbering(units, pat):
    nums = []
    for u in units:
        m = re.search(pat, u['title'])
        if m:
            nums.append(int(m.groups()[-1]))
    cnt = collections.Counter(nums)
    mx = max(nums) if nums else 0
    return dict(count=len(nums), max=mx, missing=sorted(set(range(1, mx + 1)) - set(nums)), dup=sorted(k for k, v in cnt.items() if v > 1))

def paras(text):
    out = []
    for l in text.split('\n'):
        s = l.strip()
        if cjk(s) >= 40 and not re.match(r'^([-*]\s*\[|!\[|>|#)', s):
            out.append(s)
    return out

def probe(src):
    B = load(src)
    if len(B) != 10:
        raise SystemExit(f'在 {src} 里只找到 {len(B)} 本，期望 10 本')
    f = dict(per_book={}, totals={})
    allu = {}
    for code, d in B.items():
        us = split_units(d['text'], d['lvl'])
        allu[code] = us
        c = collections.Counter(u['cls'] for u in us)
        f['per_book'][code] = dict(total=len(us), content=c['C'], container=c['S'], noncontent=c['N'],
                                    content_chars=sum(u['chars'] for u in us if u['cls'] == 'C'))
    tot = collections.Counter()
    for v in f['per_book'].values():
        for k in ('total', 'content', 'container', 'noncontent', 'content_chars'):
            tot[k] += v[k]
    f['totals'] = dict(tot)
    f['file_chars'] = sum(cjk(d['text']) for d in B.values())
    f['letters'] = {c: numbering(allu[c], r'第\s*0*(\d+)\s*封信') for c in ('SG1', 'WJ2', 'SG3', 'GG')}
    f['qa_numbering'] = dict(WJ2=numbering(allu['WJ2'], r'周末问答\s*0*(\d+)'),
                             SG3=numbering(allu['SG3'], r'答读者问\s*0*(\d+)'),
                             GG=numbering(allu['GG'], r'答读者问\s*0*(\d+)'))
    cat = next((u for u in allu['GG'] if u['title'].startswith('收藏丨全年课程目录')), None)
    covered = sorted({int(x) for x in re.findall(r'第\s*0*(\d{1,3})\s*封信', cat['text'])}) if cat else []
    f['gg_author_catalog'] = dict(covered=len(covered), missing=sorted(set(range(1, 224)) - set(covered)))
    P = {c: paras(d['text']) for c, d in B.items()}
    inbook = {c: sum(1 for v in collections.Counter(p).values() if v > 1) for c, p in P.items()}
    f['dup_inbook'] = {c: n for c, n in inbook.items() if n}
    pairs, tp, tc = {}, 0, 0
    for a, b in itertools.combinations(sorted(P), 2):
        inter = set(P[a]) & set(P[b])
        if inter:
            pairs[f'{a}<->{b}'] = dict(paragraphs=len(inter), chars=sum(cjk(x) for x in inter))
            tp += len(inter); tc += sum(cjk(x) for x in inter)
    f['dup_cross'] = dict(paragraphs=tp, chars=tc, pairs=pairs)
    lines = B['SG3']['text'].split('\n'); n = ch = 0; inh = False
    for l in lines:
        m = re.match(r'^(#{1,6})\s+(.*)', l)
        if m:
            inh = (m.group(2).strip() == '划重点'); n += inh
        elif inh:
            ch += cjk(l)
    f['sg3_huazhongdian'] = dict(sections=n, chars=ch)
    valid = [u for us in allu.values() for u in us if u['cls'] != 'N']
    qa = [u for u in valid if QA.search(u['title'])]
    it = [u for u in valid if INTERACT.search(u['title'])]
    f['qa_units'] = dict(count=len(qa), chars=sum(u['chars'] for u in qa))
    f['interact_units'] = dict(count=len(it), chars=sum(u['chars'] for u in it))
    f['series_units'] = sum(1 for us in allu.values() for u in us if SERIES.search(u['title']))
    return f

def flat(d, pre=''):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(flat(v, f'{pre}{k}.'))
        else:
            out[f'{pre}{k}'] = v
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default='src_frozen')
    ap.add_argument('--baseline', default='spec/baseline_facts.json')
    ap.add_argument('--out', default='logs/p0_probe.md')
    ap.add_argument('--write-baseline', default='')
    a = ap.parse_args()
    f = probe(a.src)
    if a.write_baseline:
        cur = json.load(open(a.write_baseline, encoding='utf-8')) if os.path.exists(a.write_baseline) else {}
        cur['probe'] = f
        json.dump(cur, open(a.write_baseline, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
        print('已写入基线（probe 部分）:', a.write_baseline); return
    base = json.load(open(a.baseline, encoding='utf-8')).get('probe')
    if base is None:
        raise SystemExit('基线里没有 probe 部分；先核对数字，再用 --write-baseline 生成')
    fa, fb = flat(f), flat(base)
    keys = sorted(set(fa) | set(fb))
    bad = [(k, fb.get(k), fa.get(k)) for k in keys if fa.get(k) != fb.get(k)]
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    with open(a.out, 'w', encoding='utf-8') as g:
        g.write(f'# P0 前置探测结果\n\n- 比对项 {len(keys)}，不一致 {len(bad)}\n- 总单元 {f["totals"]["total"]:,} = 内容 {f["totals"]["content"]:,} + 容器 {f["totals"]["container"]} + 非内容 {f["totals"]["noncontent"]}；内容单元汉字 {f["totals"]["content_chars"]:,}\n\n')
        if bad:
            g.write('## 不一致项\n\n| 项 | 基线 | 本次 |\n|---|---|---|\n' + '\n'.join(f'| {k} | {x} | {y} |' for k, x, y in bad) + '\n')
    print(f'比对项 {len(keys)}，不一致 {len(bad)}；总单元 {f["totals"]["total"]}（内容 {f["totals"]["content"]}，容器 {f["totals"]["container"]}，非内容 {f["totals"]["noncontent"]}）；日志 {a.out}')
    for k, x, y in bad[:20]:
        print('  不一致:', k, '基线', x, '本次', y)
    sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
