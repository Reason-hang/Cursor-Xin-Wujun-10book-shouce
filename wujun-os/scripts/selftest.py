#!/usr/bin/env python3
"""selftest.py — 脚本自测（make test）
用法（在仓库根目录 wujun-os/ 执行）:  python3 scripts/selftest.py
覆盖: ① 锚点脚本（原文通过、篡改一字被检出、前插一行被检出）② s01 基线比对通过 ③ s01 在被破坏的原文上必须失败
      ④ status 能渲染 ⑤ 若有 MANIFEST 则包校验通过。需要 src_frozen/ 里已有 10 本原文（make freeze）。
"""
import glob, os, re, shutil, subprocess, sys, tempfile

PY = sys.executable
ROOT = os.getcwd()
results = []

def run(args, cwd=ROOT):
    r = subprocess.run([PY] + args, cwd=cwd, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()

def rec(name, ok, note=''):
    results.append((name, ok, note))

def pick_probe(path):
    t = open(path, encoding='utf-8').read()
    for b in t.split('\n\n'):
        if len(b) >= 200 and not b.lstrip().startswith(('-', '[', '#', '!', '<', '>')) and '](#' not in b:
            for ln in [l.strip() for l in b.split('\n') if len(l.strip()) >= 14]:
                pr = ln[2:12]
                if t.count(pr) == 1:
                    return pr
    return None

def anchor_tests():
    books = glob.glob(os.path.join(ROOT, 'src_frozen', '*数学通识*.md')) + glob.glob(os.path.join(ROOT, 'src_frozen', '*来信3*.md'))
    if len(books) != 2:
        rec('锚点：需要 src_frozen 里的数学通识与来信3', False, f'找到 {len(books)} 本'); return
    tool = os.path.join(ROOT, 'scripts', 'anchor_tool.py')
    with tempfile.TemporaryDirectory() as tmp:
        rows = []
        for i, b in enumerate(books):
            dst = os.path.join(tmp, os.path.basename(b)); shutil.copy(b, dst)
            os.chmod(dst, 0o644)
            pr = pick_probe(dst)
            rc, out = run([tool, 'make', '--book', dst, '--probe', pr, '--id', f'T-{i}'])
            rows.append(out)
        ledger = os.path.join(tmp, 'ledger.md')
        open(ledger, 'w', encoding='utf-8').write('| 卡ID | 书文件名 | 行起 | 行止 | 字符起 | 字符止 | SHA1 | 指纹词 |\n|---|---|---|---|---|---|---|---|\n' + '\n'.join(rows) + '\n')
        rc, out = run([tool, 'verify', '--ledger', ledger, '--books-dir', tmp])
        rec('锚点：原文校验应通过', rc == 0, out.splitlines()[-1] if out else '')
        target = os.path.join(tmp, os.path.basename(books[0])); t = open(target, encoding='utf-8').read()
        cs = int(rows[0].strip('|').split('|')[4])
        open(target, 'w', encoding='utf-8').write(t[:cs + 3] + ('X' if t[cs + 3] != 'X' else 'Y') + t[cs + 4:])
        rc, out = run([tool, 'verify', '--ledger', ledger, '--books-dir', tmp])
        rec('锚点：篡改一字应被检出', rc == 1 and 'SHA1不符' in out)
        open(target, 'w', encoding='utf-8').write('多出的一行\n' + t)
        rc, out = run([tool, 'verify', '--ledger', ledger, '--books-dir', tmp])
        rec('锚点：前插一行应被检出', rc == 1 and '行号不符' in out)

def probe_tests():
    rc, out = run(['scripts/s01_probe.py', '--src', 'src_frozen', '--out', os.path.join(tempfile.gettempdir(), 'p0_probe_selftest.md')])
    rec('s01：与基线比对应通过', rc == 0, out.splitlines()[0] if out else '')
    with tempfile.TemporaryDirectory() as tmp:
        for p in glob.glob('src_frozen/*.md'):
            dst = os.path.join(tmp, os.path.basename(p))
            shutil.copy(p, dst)
            os.chmod(dst, 0o644)
        f = glob.glob(os.path.join(tmp, '*富足*.md'))[0]
        t = open(f, encoding='utf-8').read()
        i = t.index('\n### ')
        j = t.index('\n', i + 1)
        open(f, 'w', encoding='utf-8').write(t[:i] + t[j:])  # 整行删掉一个标题，两个单元会被合并
        rc, out = run(['scripts/s01_probe.py', '--src', tmp, '--out', os.path.join(tmp, 'x.md')])
        rec('s01：原文被破坏时应失败', rc == 1, out.splitlines()[0] if out else '')

def triage_test():
    if not os.path.isfile(os.path.join(ROOT, 'ledger', '分诊表.csv')):
        rec('p2：分诊表 1697 + 强制规则', False, '先 make p2-triage'); return
    rc, out = run(['scripts/p2_triage.py', '--verify-only'])
    rec('p2：分诊强制规则核对', rc == 0, out.splitlines()[0] if out else '')

def s09_test():
    path = os.path.join(ROOT, 'logs', 'unit_cards.md')
    if not os.path.isfile(path):
        rec('s09：unit_cards 存在且 1697 行', False, '先 make p2-s09'); return
    n = sum(1 for ln in open(path, encoding='utf-8') if ln.startswith('| ') and '-U' in ln)
    rec('s09：unit_cards 1697 张', n == 1697, f'实际 {n}')

def p3a_lint_test():
    rc, out = run(['scripts/p3a_batch.py', 'lint', '--batch', 'B-P3a-GJ-002'])
    rec('p3a：批次卡面 lint（GJ-002）', rc == 0, out.splitlines()[-1] if out else '')

def p5_lint_test():
    rc, out = run(['scripts/s17_manual_lint.py'])
    rec('p5：核心卡 s17 lint', rc == 0, out.splitlines()[-1] if out else '')
    scene = os.path.join(ROOT, 'drafts/p5/D06/S_场景入口_D06.md')
    if os.path.isfile(scene):
        txt = open(scene, encoding='utf-8').read()
        n = sum(1 for line in txt.splitlines() if line.startswith('| S-'))
        rec('p5：D06 场景入口 10 条', n == 10, f'计数 {n}')
    cov = os.path.join(ROOT, 'drafts/p5/D06/AC-5.8_D06必检议题覆盖表.md')
    if os.path.isfile(cov):
        rows = [ln for ln in open(cov, encoding='utf-8') if ln.startswith('| D06-')]
        rec('p5：D06 必检议题 14 项', len(rows) == 14, f'行数 {len(rows)}')
    scene_d01 = os.path.join(ROOT, 'drafts/p5/D01/S_场景入口_D01.md')
    if os.path.isfile(scene_d01):
        n1 = sum(1 for line in open(scene_d01, encoding='utf-8') if line.startswith('| S-'))
        rec('p5：D01 场景入口 6 条', n1 == 6, f'计数 {n1}')
    cov_d01 = os.path.join(ROOT, 'drafts/p5/D01/AC-5.8_D01必检议题覆盖表.md')
    if os.path.isfile(cov_d01):
        rows_d01 = [ln for ln in open(cov_d01, encoding='utf-8') if ln.startswith('| D01-')]
        rec('p5：D01 必检议题 17 项', len(rows_d01) == 17, f'行数 {len(rows_d01)}')
    scene_d02 = os.path.join(ROOT, 'drafts/p5/D02/S_场景入口_D02.md')
    if os.path.isfile(scene_d02):
        n2 = sum(1 for line in open(scene_d02, encoding='utf-8') if line.startswith('| S-'))
        rec('p5：D02 场景入口 8 条', n2 == 8, f'计数 {n2}')
    cov_d02 = os.path.join(ROOT, 'drafts/p5/D02/AC-5.8_D02必检议题覆盖表.md')
    if os.path.isfile(cov_d02):
        rows_d02 = [ln for ln in open(cov_d02, encoding='utf-8') if ln.startswith('| D02-')]
        rec('p5：D02 必检议题 15 项', len(rows_d02) == 15, f'行数 {len(rows_d02)}')
    scene_d03 = os.path.join(ROOT, 'drafts/p5/D03/S_场景入口_D03.md')
    if os.path.isfile(scene_d03):
        n3 = sum(1 for line in open(scene_d03, encoding='utf-8') if line.startswith('| S-'))
        rec('p5：D03 场景入口 4 条', n3 == 4, f'计数 {n3}')
    cov_d03 = os.path.join(ROOT, 'drafts/p5/D03/AC-5.8_D03必检议题覆盖表.md')
    if os.path.isfile(cov_d03):
        rows_d03 = [ln for ln in open(cov_d03, encoding='utf-8') if ln.startswith('| D03-')]
        rec('p5：D03 必检议题 8 项', len(rows_d03) == 8, f'行数 {len(rows_d03)}')
    scene_d05 = os.path.join(ROOT, 'drafts/p5/D05/S_场景入口_D05.md')
    if os.path.isfile(scene_d05):
        n5 = sum(1 for line in open(scene_d05, encoding='utf-8') if line.startswith('| S-'))
        rec('p5：D05 场景入口 4 条', n5 == 4, f'计数 {n5}')
    cov_d05 = os.path.join(ROOT, 'drafts/p5/D05/AC-5.8_D05必检议题覆盖表.md')
    if os.path.isfile(cov_d05):
        rows_d05 = [ln for ln in open(cov_d05, encoding='utf-8') if ln.startswith('| D05-')]
        rec('p5：D05 必检议题 9 项', len(rows_d05) == 9, f'行数 {len(rows_d05)}')
    scene_d07 = os.path.join(ROOT, 'drafts/p5/D07/S_场景入口_D07.md')
    if os.path.isfile(scene_d07):
        n7 = sum(1 for line in open(scene_d07, encoding='utf-8') if line.startswith('| S-'))
        rec('p5：D07 场景入口 4 条', n7 == 4, f'计数 {n7}')
    cov_d07 = os.path.join(ROOT, 'drafts/p5/D07/AC-5.8_D07必检议题覆盖表.md')
    if os.path.isfile(cov_d07):
        rows_d07 = [ln for ln in open(cov_d07, encoding='utf-8') if ln.startswith('| D07-')]
        rec('p5：D07 必检议题 9 项', len(rows_d07) == 9, f'行数 {len(rows_d07)}')
    scene_d04 = os.path.join(ROOT, 'drafts/p5/D04/S_场景入口_D04.md')
    if os.path.isfile(scene_d04):
        n4 = sum(1 for line in open(scene_d04, encoding='utf-8') if line.startswith('| S-'))
        rec('p5：D04 场景入口 3 条', n4 == 3, f'计数 {n4}')
    cov_d04 = os.path.join(ROOT, 'drafts/p5/D04/AC-5.8_D04必检议题覆盖表.md')
    if os.path.isfile(cov_d04):
        rows_d04 = [ln for ln in open(cov_d04, encoding='utf-8') if ln.startswith('| D04-')]
        rec('p5：D04 必检议题 16 项', len(rows_d04) == 16, f'行数 {len(rows_d04)}')
    scene_d08 = os.path.join(ROOT, 'drafts/p5/D08/S_场景入口_D08.md')
    if os.path.isfile(scene_d08):
        n8 = sum(1 for line in open(scene_d08, encoding='utf-8') if line.startswith('| S-'))
        rec('p5：D08 场景入口 3 条', n8 == 3, f'计数 {n8}')
    cov_d08 = os.path.join(ROOT, 'drafts/p5/D08/AC-5.8_D08必检议题覆盖表.md')
    if os.path.isfile(cov_d08):
        rows_d08 = [ln for ln in open(cov_d08, encoding='utf-8') if ln.startswith('| D08-')]
        rec('p5：D08 必检议题 10 项', len(rows_d08) == 10, f'行数 {len(rows_d08)}')
    scene_d09 = os.path.join(ROOT, 'drafts/p5/D09/S_场景入口_D09.md')
    if os.path.isfile(scene_d09):
        n9 = sum(1 for line in open(scene_d09, encoding='utf-8') if line.startswith('| S-'))
        rec('p5：D09 场景入口 2 条', n9 == 2, f'计数 {n9}')
    cov_d09 = os.path.join(ROOT, 'drafts/p5/D09/AC-5.8_D09必检议题覆盖表.md')
    if os.path.isfile(cov_d09):
        rows_d09 = [ln for ln in open(cov_d09, encoding='utf-8') if ln.startswith('| D09-')]
        rec('p5：D09 必检议题 9 项', len(rows_d09) == 9, f'行数 {len(rows_d09)}')
    scene_d10 = os.path.join(ROOT, 'drafts/p5/D10/S_场景入口_D10.md')
    if os.path.isfile(scene_d10):
        n10 = sum(1 for line in open(scene_d10, encoding='utf-8') if line.startswith('| S-'))
        rec('p5：D10 场景入口 2 条', n10 == 2, f'计数 {n10}')
    cov_d10 = os.path.join(ROOT, 'drafts/p5/D10/AC-5.8_D10必检议题覆盖表.md')
    if os.path.isfile(cov_d10):
        rows_d10 = [ln for ln in open(cov_d10, encoding='utf-8') if ln.startswith('| D10-')]
        rec('p5：D10 必检议题 5 项', len(rows_d10) == 5, f'行数 {len(rows_d10)}')
    d1_out = os.path.join(ROOT, 'out/认知与行动操作系统_主手册_v0.9.md')
    d2_out = os.path.join(ROOT, 'out/行动工具集_v0.9.md')
    rec('p5：D1 v0.9 集成稿', os.path.isfile(d1_out), d1_out)
    rec('p5：D2 v0.9 集成稿', os.path.isfile(d2_out), d2_out)
    if os.path.isfile(d1_out):
        qf = open(d1_out, encoding='utf-8').read()
        rec('p5：能力速查 4 节', qf.count('## 思｜') == 1 and qf.count('## 做｜') == 1, '思学沟做')
    import subprocess
    sc = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts/p5_lint_scenes.py')], capture_output=True, text=True)
    rec('p5：场景 ID S-001–046 唯一', sc.returncode == 0, (sc.stdout or sc.stderr or '').strip()[:80])
    pf = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts/p6_preflight.py')], capture_output=True, text=True)
    rec('p6：预检（112 必检+场景）', pf.returncode == 0, (pf.stdout or pf.stderr or '').strip()[:80])
    deliver_root = os.path.join(ROOT, '..', '最终所有交付物')
    d3_del = os.path.join(deliver_root, '溯源与处置台账_v0.9.md')
    d4_del = os.path.join(deliver_root, '覆盖与质检报告_v0.9.md')
    d6_del = os.path.join(deliver_root, '方案决策与裁决记录_v0.9.md')
    rec('p6：D3/D4/D6 正式副本', os.path.isfile(d3_del) and os.path.isfile(d4_del) and os.path.isfile(d6_del), '最终所有交付物')
    dup = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts/p6_dup_lint.py')], capture_output=True, text=True)
    rec('p6：主手册 24 字滑窗重复', dup.returncode == 0, (dup.stdout or dup.stderr or '').strip()[:60])
    mc_csv = os.path.join(ROOT, 'ledger/P6_必检112项汇总.csv')
    if os.path.isfile(mc_csv):
        mc_n = sum(1 for ln in open(mc_csv, encoding='utf-8')) - 1
        rec('p6：必检 112 项汇总 CSV', mc_n == 112, f'行数 {mc_n}')
    g10_stat = os.path.join(ROOT, 'ledger/P6_G10关键词去向统计.md')
    rec('p6：G10 去向统计已生成', os.path.isfile(g10_stat), g10_stat)
    if os.path.isfile(g10_stat):
        txt = open(g10_stat, encoding='utf-8').read()
        mech = '待处理 | 0 |' in txt or '完成率 | 100' in txt
        rec('p6：G10 机械去向 100%', mech, 'make p6-g10-refresh')
    bidir = os.path.join(ROOT, 'ledger/P6_双向矩阵_机械预检.md')
    rec('p6：双向矩阵机械预检产物', os.path.isfile(bidir), bidir)
    recall = os.path.join(ROOT, 'ledger/P6_抽检召回样本.csv')
    if os.path.isfile(recall):
        rn = sum(1 for ln in open(recall, encoding='utf-8')) - 1
        rec('p6：抽检召回样本 130 条', rn == 130, f'行数 {rn}')
    workbook = os.path.join(ROOT, 'ledger/P6_抽检召回工作册.md')
    rec('p6：抽检召回工作册', os.path.isfile(workbook), workbook)
    math_audit = os.path.join(ROOT, 'ledger/P6_数理映射审计.md')
    if os.path.isfile(math_audit):
        rec('p6：M 卡数理映射 50/50', '50/50' in open(math_audit, encoding='utf-8').read(), math_audit)
    rc, out = run(['scripts/p6_app_scenarios_lint.py'])
    rec('p6：应用验证 5 场景', rc == 0, out.splitlines()[-1] if out else '')
    dash = os.path.join(ROOT, 'ledger/P6_AC6_状态看板.md')
    rec('p6：AC-6 状态看板', os.path.isfile(dash), dash)
    s15 = os.path.join(ROOT, 'ledger/P6_S15_G闸门对账.md')
    rec('p6：S15 G 闸门对账表', os.path.isfile(s15), s15)
    sg3r = os.path.join(ROOT, 'ledger/P6_SG3划重点召回_全量.md')
    if os.path.isfile(sg3r):
        rec('p6：SG3 划重点全量已跑', '召回率' in open(sg3r, encoding='utf-8').read(), '见 G10③ 差距说明')
    rc, out = run(['scripts/s18_render_check.py'])
    rec('p7：S18 D1/D2 渲染链接', rc == 0, out.splitlines()[-1] if out else '')
    rc, out = run(['scripts/deliverables_audit.py'])
    rec('p7：正式夹 D1–D6 审计', rc == 0, out.splitlines()[-1] if out else '')
    preview = os.path.join(ROOT, 'ledger', 'P6_锚点修探针_预演.md')
    rec('p6：锚点队列预演', os.path.isfile(preview) and 'P3a-SX-U0043-K01' in open(preview, encoding='utf-8').read(), preview)
    rc, out = run(['scripts/p7_human_signoff_lint.py'])
    rec('p7：人审签字预检可跑', rc == 0, out.splitlines()[-1] if out else '')
    rc, out = run(['scripts/approvals_ingest.py'])
    rec('p7：批复 ingest 可跑', rc in (0, 1), out.splitlines()[-1] if out else '')

def p4_freeze_k_test():
    path = os.path.join(ROOT, 'data', 'k_card_freeze.json')
    if not os.path.isfile(path):
        rec('p4：K 卡已冻结', False, '先 make p4-freeze-k'); return
    rc, out = run(['scripts/p4_lint_freeze_k.py'])
    rec('p4：K 冻结 lint', rc == 0, out.splitlines()[-1] if out else '')

def p4_spot_check_test():
    path = os.path.join(ROOT, 'ledger', 'P4_抽查20张.csv')
    if not os.path.isfile(path):
        rec('p4：抽查 20 张表', False, '先 make p4-spot-check-20'); return
    n = sum(1 for _ in open(path, encoding='utf-8')) - 1
    rec('p4：抽查 20 张表', n == 20, f'行数 {n}')

def p4_blind_kappa_test():
    path = os.path.join(ROOT, 'ledger', 'P4_盲重标κ报告.md')
    if not os.path.isfile(path):
        rec('p4：盲重标 κ 已生成', False, '先 make p4-blind-kappa'); return
    rc, out = run(['scripts/p4_lint_blind_kappa.py'])
    rec('p4：盲重标 κ 记录', rc == 0, out.splitlines()[-1] if out else '')

def p4_count_test():
    path = os.path.join(ROOT, 'ledger', 'P4_数量核对表.csv')
    if not os.path.isfile(path):
        rec('p4：数量核对已生成', False, '先 make p4-count-audit'); return
    rc, out = run(['scripts/p4_lint_count.py'])
    rec('p4：数量核对 lint', rc == 0, out.splitlines()[-1] if out else '')

def p4_d10_gates_test():
    path = os.path.join(ROOT, 'ledger', 'P4_D10三道门裁决.csv')
    if not os.path.isfile(path):
        rec('p4：D10 三道门已裁决', False, '先 make p4-d10-gates'); return
    rc, out = run(['scripts/p4_lint_d10_gates.py'])
    rec('p4：D10 三道门 lint', rc == 0, out.splitlines()[-1] if out else '')

def p4_l2_final_test():
    path = os.path.join(ROOT, 'ledger', 'P4_L2定稿.csv')
    if not os.path.isfile(path):
        rec('p4：L2 定稿已生成', False, '先 make p4-finalize-l2'); return
    rc, out = run(['scripts/p4_lint_l2_final.py'])
    rec('p4：L2 定稿 lint', rc == 0, out.splitlines()[-1] if out else '')

def p4_l3_test():
    path = os.path.join(ROOT, 'ledger', 'P4_L3模型清单.csv')
    if not os.path.isfile(path):
        rec('p4：L3 清单已生成', False, '先 make p4-aggregate-l3'); return
    rc, out = run(['scripts/p4_lint_l3.py'])
    rec('p4：L3 聚合 lint', rc == 0, out.splitlines()[-1] if out else '')

def p4_pillars_test():
    path = os.path.join(ROOT, 'ledger', 'P4_归属表.csv')
    if not os.path.isfile(path):
        rec('p4：归属表已生成', False, '先 make p4-assign-pillars'); return
    rc, out = run(['scripts/p4_lint_pillars.py'])
    rec('p4：支柱归属 lint', rc == 0, out.splitlines()[-1] if out else '')

def p4_relations_test():
    path = os.path.join(ROOT, 'ledger', 'P4_卡对关系表.csv')
    if not os.path.isfile(path):
        rec('p4：关系表已生成', False, '先 make p4-annotate-relations'); return
    rc, out = run(['scripts/p4_lint_relations.py'])
    rec('p4：关系标注 lint', rc == 0, out.splitlines()[-1] if out else '')

def ep0_restore_log_test():
    log = os.path.join(ROOT, 'ledger/EP0_restore_check_20261028.md')
    rec('ep0：restore-check 留证', os.path.isfile(log), log)

def ep0_b3_test():
    roles = ['R-ORCH', 'R-EXT', 'R-WRT', 'R-AUD', 'R-OPS']
    for r in roles:
        p = os.path.join(ROOT, 'prompts', f'{r}.md')
        rec(f'ep0：角色提示词 {r}', os.path.isfile(p), p)
    for ph in ('P0', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6'):
        p = os.path.join(ROOT, 'prompts', f'phase_append_{ph}.md')
        rec(f'ep0：阶段追加段 {ph}', os.path.isfile(p), p)
    rec('ep0：开场提示词', os.path.isfile(os.path.join(ROOT, 'handover/开场提示词.md')), 'handover/')
    for name in ('spec/pillars.yaml', 'spec/exclusions.yaml'):
        rec(f'ep0：机读字典 {os.path.basename(name)}', os.path.isfile(os.path.join(ROOT, name)), name)
    rc, out = run(['scripts/validate_pillars.py'])
    rec('ep0：pillars L1=10 L2=25', rc == 0, out.splitlines()[-1] if out else '')

def p4_concept_keys_test():
    path = os.path.join(ROOT, 'rules', 'concept_keys.csv')
    if not os.path.isfile(path):
        rec('p4：concept_keys 已生成', False, '先 make p4-concept-keys'); return
    rc, out = run(['scripts/p4_lint_concept_keys.py'])
    rec('p4：概念键 lint（AC-4.2）', rc == 0, out.splitlines()[-1] if out else '')

def other_tests():
    ep0_restore_log_test()
    ep0_b3_test()
    s09_test()
    triage_test()
    p3a_lint_test()
    p4_concept_keys_test()
    p4_relations_test()
    p4_pillars_test()
    p4_l3_test()
    p4_l2_final_test()
    p4_d10_gates_test()
    p4_count_test()
    p4_blind_kappa_test()
    p4_spot_check_test()
    p4_freeze_k_test()
    p5_lint_test()
    rc, out = run(['scripts/status.py'])
    rec('status：能渲染 STATE.md', rc == 0, out.splitlines()[0] if out else '')
    if os.path.exists('MANIFEST.sha256'):
        rc, out = run(['scripts/verify_pack.py'])
        rec('verify_pack：包校验应通过', rc == 0, out.splitlines()[0] if out else '')

if __name__ == '__main__':
    if not glob.glob('src_frozen/*.md'):
        print('src_frozen/ 里没有原文：先 make freeze'); sys.exit(2)
    anchor_tests(); probe_tests(); other_tests()
    print('| 测试 | 结果 | 说明 |\n|---|---|---|')
    for n, ok, note in results:
        print(f"| {n} | {'PASS' if ok else 'FAIL'} | {note} |")
    sys.exit(0 if all(ok for _, ok, _ in results) else 1)
