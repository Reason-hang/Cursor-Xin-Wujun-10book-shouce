#!/usr/bin/env python3
"""status.py — 由 state/state.json 渲染 state/STATE.md，并打印进度条
用法（在仓库根目录 wujun-os/ 执行）:  python3 scripts/status.py
"""
import json, os, sys

REQUIRED = ['project', 'pack_version', 'updated', 'phase', 'progress', 'in_flight', 'next_ticket', 'blocked_by', 'open_items', 'risks_top']

def bar(done, total, width=30):
    if not total:
        return '[' + '-' * width + '] 0.0%'
    n = int(width * done / total)
    return '[' + '#' * n + '-' * (width - n) + f'] {100 * done / total:.1f}%'

def render(root='.'):
    p = os.path.join(root, 'state', 'state.json')
    s = json.load(open(p, encoding='utf-8'))
    miss = [k for k in REQUIRED if k not in s]
    if miss:
        raise SystemExit(f'state.json 缺字段: {miss}')
    pr = s['progress']
    L = []
    L.append(f"# STATE（由 state.json 渲染，勿手改）\n")
    L.append(f"- 项目：{s['project']}　包版本：{s['pack_version']}　最后更新：{s['updated']}")
    L.append(f"- 阶段：{s['phase']}　{s.get('step', '')}")
    L.append(f"- 规格版本：{json.dumps(s.get('spec', {}), ensure_ascii=False)}")
    L.append(f"- 冻结状态：{json.dumps(s.get('frozen', {}), ensure_ascii=False)}")
    L.append(f"- 单元进度：{pr['units_done']}/{pr['units_total']} {bar(pr['units_done'], pr['units_total'])}（内容单元 {pr.get('units_content', '—')}）")
    L.append(f"- 汉字进度：{pr['chars_done']:,}/{pr['chars_total']:,} {bar(pr['chars_done'], pr['chars_total'])}")
    L.append(f"- 已完成批次：{pr.get('batches_done', 0)}（估算总批数 {pr.get('batches_est', '—')}）")
    L.append(f"- 估算：{json.dumps(s.get('estimates', {}), ensure_ascii=False)}")
    inf = s['in_flight']
    L.append(f"\n## 当前检查点（in_flight）\n- 工单：{inf.get('ticket')}　处理中的单元：{inf.get('unit_ids')}\n- 尚未落盘的内容：{inf.get('unsaved')}\n- 备注：{inf.get('note', '')}")
    L.append(f"\n## 工单\n- 上一张：{s.get('last_ticket')}　下一张：{s['next_ticket']}")
    L.append("- 阻塞项：" + ('；'.join(s['blocked_by']) if s['blocked_by'] else '无'))
    L.append("\n## 待确认事项")
    L += [f"- {x}" for x in s['open_items']] or ['- 无']
    L.append("\n## 风险（前几项）")
    L += [f"- {x}" for x in s['risks_top']]
    out = os.path.join(root, 'state', 'STATE.md')
    open(out, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    return s

if __name__ == '__main__':
    s = render('.')
    pr = s['progress']
    print(f"阶段：{s['phase']}｜单元 {pr['units_done']}/{pr['units_total']} {bar(pr['units_done'], pr['units_total'])}｜下一张工单：{s['next_ticket']}｜阻塞：{len(s['blocked_by'])} 项")
