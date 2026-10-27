#!/usr/bin/env python3
"""pack.py — 刷新状态并打包成可下载的恢复包（每次收工前运行）
用法（在仓库根目录 wujun-os/ 执行）:  python3 scripts/pack.py
步骤: ① 渲染 STATE.md ② 生成 MANIFEST.sha256 ③ 打成 dist/wujun-os-pack_<日期>.zip（含顶层目录 wujun-os/）
不打包: src_frozen/（原文由你保管，用哈希核对）、logs/、dist/、__pycache__。
"""
import datetime, hashlib, os, sys, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import status

EXCLUDE_DIRS = {'src_frozen', 'logs', 'dist', '__pycache__', '.git', '.venv'}

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

def files(root):
    out = []
    for d, ds, fs in os.walk(root):
        ds[:] = [x for x in ds if x not in EXCLUDE_DIRS]
        for f in fs:
            p = os.path.relpath(os.path.join(d, f), root)
            if p != 'MANIFEST.sha256' and not f.endswith('.pyc') and not f.endswith('.zip'):
                out.append(p)
    return sorted(out)

def main(root='.'):
    status.render(root)
    fs = files(root)
    with open(os.path.join(root, 'MANIFEST.sha256'), 'w', encoding='utf-8') as m:
        for p in fs:
            m.write(f'{sha(os.path.join(root, p))}  {p}\n')
    os.makedirs(os.path.join(root, 'dist'), exist_ok=True)
    name = f"wujun-os-pack_{datetime.date.today():%Y%m%d}.zip"
    zp = os.path.join(root, 'dist', name)
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in fs + ['MANIFEST.sha256']:
            z.write(os.path.join(root, p), os.path.join('wujun-os', p))
        for d in ('src_frozen', 'logs', 'out', 'data'):
            z.writestr(f'wujun-os/{d}/.gitkeep', '')
    print(f'已打包 {len(fs) + 1} 个文件 -> {zp}；SHA-256 {sha(zp)}')

if __name__ == '__main__':
    main('.')
