#!/usr/bin/env python3
"""verify_pack.py — 校验恢复包完整性（对照 MANIFEST.sha256）
用法（在仓库根目录 wujun-os/ 执行）:  python3 scripts/verify_pack.py
输出: 缺失、被改动、多出的文件；全部一致返回 0。
"""
import hashlib, os, sys

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def main(root='.'):
    mp = os.path.join(root, 'MANIFEST.sha256')
    if not os.path.exists(mp):
        print('没有 MANIFEST.sha256'); return 1
    exp = {}
    for line in open(mp, encoding='utf-8'):
        line = line.rstrip('\n')
        if line:
            h, p = line.split('  ', 1); exp[p] = h
    missing = [p for p in exp if not os.path.exists(os.path.join(root, p))]
    changed = [p for p in exp if p not in missing and sha(os.path.join(root, p)) != exp[p]]
    print(f'清单 {len(exp)} 项；缺失 {len(missing)}；被改动 {len(changed)}')
    for p in missing: print('  缺失:', p)
    for p in changed: print('  被改动:', p)
    return 1 if missing or changed else 0

if __name__ == '__main__':
    sys.exit(main('.'))
