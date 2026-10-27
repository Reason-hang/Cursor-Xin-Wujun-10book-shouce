#!/usr/bin/env python3
"""s00_freeze.py — 冻结原文（S00）
用法（在仓库根目录 wujun-os/ 执行）:
  python3 scripts/s00_freeze.py --zip "_打包吴军10本电子书.zip" --out src_frozen --log logs/g0_inputs.md
作用: 把 zip 里的 10 个 md 解到 src_frozen/（还原 UTF-8 文件名），登记 SHA-256、字节、行数、汉字数、BOM、CRLF，
      与 spec/baseline_facts.json 的基线比对，并把文件设为只读。任何不一致返回非零退出码。
"""
import argparse, hashlib, json, os, re, sys, zipfile

CJK = re.compile(r'[\u4e00-\u9fff]')

def decode_name(info):
    try:
        return info.filename.encode('cp437').decode('utf-8')
    except Exception:
        return info.filename

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--zip', required=True)
    ap.add_argument('--out', default='src_frozen')
    ap.add_argument('--log', default='logs/g0_inputs.md')
    ap.add_argument('--baseline', default='spec/baseline_facts.json')
    a = ap.parse_args()
    base = {}
    if os.path.exists(a.baseline):
        base = {b['file']: b for b in json.load(open(a.baseline, encoding='utf-8'))['books']}
    os.makedirs(a.out, exist_ok=True)
    os.makedirs(os.path.dirname(a.log) or '.', exist_ok=True)
    z = zipfile.ZipFile(a.zip)
    rows = []
    bad = 0
    for info in z.infolist():
        name = os.path.basename(decode_name(info))
        if not name.endswith('.md'):
            continue
        raw = z.read(info)
        path = os.path.join(a.out, name)
        if os.path.exists(path):
            os.chmod(path, 0o644)
        open(path, 'wb').write(raw)
        os.chmod(path, 0o444)
        text = raw.decode('utf-8', 'replace')
        rec = dict(file=name, bytes=len(raw), lines=len(text.split('\n')), cjk=len(CJK.findall(text)),
                   bom=raw[:3] == b'\xef\xbb\xbf', crlf=raw.count(b'\r\n'),
                   sha256=hashlib.sha256(raw).hexdigest())
        status = '无基线'
        if name in base:
            b = base[name]
            ok = all(rec[k] == b[k] for k in ('bytes', 'lines', 'cjk', 'sha256'))
            status = 'PASS' if ok else 'FAIL'
            bad += 0 if ok else 1
        rec['status'] = status
        rows.append(rec)
    missing = [f for f in base if f not in {r['file'] for r in rows}]
    with open(a.log, 'w', encoding='utf-8') as f:
        f.write('# G0 输入冻结登记\n\n| 文件 | 字节 | 行数 | 汉字 | BOM | CRLF | SHA-256 | 基线比对 |\n|---|---|---|---|---|---|---|---|\n')
        for r in rows:
            f.write(f"| {r['file']} | {r['bytes']:,} | {r['lines']:,} | {r['cjk']:,} | {r['bom']} | {r['crlf']} | `{r['sha256']}` | {r['status']} |\n")
    print(f'已冻结 {len(rows)} 个文件 -> {a.out}；基线比对失败 {bad}；缺失 {missing}；日志 {a.log}')
    sys.exit(1 if bad or missing or len(rows) != 10 else 0)

if __name__ == '__main__':
    main()
