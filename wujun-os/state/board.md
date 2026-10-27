# 工单板

状态：backlog / ready / doing / blocked / review / done。单写者更新。

| 工单 | 名称 | 前置 | 状态 | 角色 |
|---|---|---|---|---|
| T-00-09 | 快照与恢复包机制（pack.py、restore-check） | — | review（雏形已实现并自测） | R-OPS |
| T-00-01 | 初始化仓库结构并放入冻结原文 | — | blocked（待用户确认 ★1–★4） | R-OPS/R-ORCH |
| T-00-02 | 规格落库 | — | backlog | R-OPS/R-ORCH |
| T-00-03 | 脚本 S00–S08 及自测 | — | review（脚本雏形已有） | R-OPS/R-ORCH |
| T-00-04 | 闸门与 lint 骨架 | — | backlog | R-OPS/R-ORCH |
| T-00-05 | 状态与日志基建、交接生成脚本 | — | backlog | R-OPS/R-ORCH |
| T-00-06 | 复水测验题库与黄金样例占位 | — | backlog | R-OPS/R-ORCH |
| T-00-07 | 角色提示词与开场提示词入库 | — | backlog | R-OPS/R-ORCH |
| T-00-08 | 压力测试规程与首次干跑 | — | backlog | R-OPS/R-ORCH |
| T-P0-01 | 建工作区，运行 S00 冻结输入 | T-00-08 | backlog | R-OPS |
| T-P0-02 | 为每本写切分规则 split_<书码>.yaml：单元层级、容器标题… | T-P0-01 | backlog | R-OPS |
| T-P0-03 | 运行 S01 切分 | T-P0-02 | backlog | R-OPS |
| T-P0-04 | 运行 S02：行覆盖与汉字守恒 | T-P0-03 | backlog | R-OPS |
| T-P0-05 | 运行 S03：编号连续 | T-P0-04 | backlog | R-OPS |
| T-P0-06 | 运行 S04：自动目录一致性（a）和谷歌作者目录（b） | T-P0-05 | backlog | R-OPS |
| T-P0-07 | 运行 S05：重复扫描 | T-P0-06 | backlog | R-OPS |
| T-P0-08 | 运行 S06：非原著与风险标注 | T-P0-07 | backlog | R-OPS |
| T-P0-09 | 运行 S07：反向抽查 | T-P0-08 | backlog | R-OPS |
| T-P0-10 | 缺号与异常逐条定性，写入异常台账 | T-P0-09 | backlog | R-OPS |
| T-P0-11 | 运行 S08：生成 D5；冻结分母（总单元、内容单元、汉字数） | T-P0-10 | backlog | R-OPS |
| T-P0-12 | 本轮交付：D5、进度台账 v0，并请用户确认缺号定性与分母 | T-P0-11 | backlog | R-OPS |
| T-P1-01 | 按 §7.5 选样（脚本按条件选，我微调），列表给用户过目 | T-P0-12 | backlog | R-EXT |
| T-P1-02 | 用户确认选样后，逐个单元按 §15.7 抽卡 | T-P1-01 | backlog | R-EXT |
| T-P1-03 | 每张卡生成锚点并校验（S11） | T-P1-02 | backlog | R-EXT |
| T-P1-04 | 对 6 个回归组运行 S13 关键词反查，判定关系类型 | T-P1-03 | backlog | R-EXT |
| T-P1-05 | **隔一轮**对同一批单元做双盲重抽（不看首次卡） | T-P1-04 | backlog | R-EXT |
| T-P1-06 | 运行 S14 计算重合率 | T-P1-05 | backlog | R-EXT |
| T-P1-07 | 来信3 样本单元对照"划重点"算召回 | T-P1-06 | backlog | R-EXT |
| T-P1-08 | 统计：能力标签可标注率、归属歧义率 | T-P1-07 | backlog | R-EXT |
| T-P1-09 | 记录单批耗时与上下文占用，建议每轮 2 批还是 3 批 | T-P1-08 | backlog | R-EXT |
| T-P1-10 | 复盘：列出规则问题，走变更控制，冻结规则 v1 | T-P1-09 | backlog | R-EXT |
| T-P1-11 | 输出《试点报告》，请用户确认结论与是否触发降级 | T-P1-10 | backlog | R-EXT |
| T-P1-12 | 压力测试 ST-2 压缩模拟、ST-3 漂移回归（补充工单，EP 稳定性方案） | T-P1-11 | backlog | R-AUD |
| T-P2-01 | 运行 S09 生成单元卡 | T-P1-12 | backlog | R-EXT |
| T-P2-02 | 运行 S10 把单元卡装箱为 3–5 万字的批 | T-P2-01 | backlog | R-EXT |
| T-P2-03 | 每批前复述规则摘要（§15.11） | T-P2-02 | backlog | R-EXT |
| T-P2-04 | 逐批读单元卡并标：读法层 A/B/C、候选支柱提示（≤2）、能力标签… | T-P2-03 | backlog | R-EXT |
| T-P2-05 | 脚本核对强制规则：问答 B、周末互动 A、骨架 A、领域直连 A | T-P2-04 | backlog | R-EXT |
| T-P2-06 | 系列单元成组（91 个） | T-P2-05 | backlog | R-EXT |
| T-P2-07 | 批末回顾 | T-P2-06 | backlog | R-EXT |
| T-P2-08 | X 候选抽样回读 ≥30 个 | T-P2-07 | backlog | R-EXT |
| T-P2-09 | 汇总：各层单元数、字数；更新批数与轮次估算；评估是否触发 Z1 | T-P2-08 | backlog | R-EXT |
| T-P2-10 | 交付：分诊表（并入进度台账），请用户确认读法层规模 | T-P2-09 | backlog | R-EXT |
| T-P3a-B-nnn | 成书与骨架 A 层批次工单（模板，由 S10 装箱后逐批生成，约 28 批） | T-P2-10 | backlog | R-EXT |
| T-P3b-B-nnn | 来信与问答 B 层批次工单（模板，约 30–47 批；C 层并行处置） | T-P3a-B-最后一批 | backlog | R-EXT |
| T-P4-01 | 冻结 P3 产物：记录台账快照版本与哈希 | T-P3b-B-最后一批 | backlog | R-ORCH |
| T-P4-02 | 概念键归一：同一概念一个键，别名登记（§15.8） | T-P4-01 | backlog | R-ORCH |
| T-P4-03 | 用脚本的指纹和相似度列出近似卡对，人工判定 | T-P4-02 | backlog | R-ORCH |
| T-P4-04 | 按 7 类关系标注，冲突登记到冲突台账（F 编号） | T-P4-03 | backlog | R-ORCH |
| T-P4-05 | 支柱归属：按 §15.9 决策树，遇歧义写判例 | T-P4-04 | backlog | R-ORCH |
| T-P4-06 | 聚合 L3 核心模型节点，按增长门检验（§5.3.3） | T-P4-05 | backlog | R-ORCH |
| T-P4-07 | L2 定稿，执行薄簇条款 | T-P4-06 | backlog | R-ORCH |
| T-P4-08 | 创新与产品方法的三道门裁决，汇总证据 | T-P4-07 | backlog | R-ORCH |
| T-P4-09 | 数量核对：目标区间、预警线、红线 | T-P4-08 | backlog | R-ORCH |
| T-P4-10 | 盲重标：随机抽 5%（不少于 60 张）不看首次归属重新归属，S16… | T-P4-09 | backlog | R-ORCH |
| T-P4-11 | 你抽查 20 张 | T-P4-10 | backlog | R-ORCH |
| T-P4-12 | K 卡冻结，分母锁定，生成 K 降级审计表 | T-P4-11 | backlog | R-ORCH |
| T-P4-13 | 对照 §13，生成"字典变更报告"（若有变更，走 §15.13），请… | T-P4-12 | backlog | R-ORCH |
| T-P5-01 | 按 §14.7 的顺序逐章写（每章走下面 2–9 步） | T-P4-13 | backlog | R-WRT |
| T-P5-02 | 取本章模型清单，写核心模型卡（9 字段） | T-P5-01 | backlog | R-WRT |
| T-P5-03 | 写变体卡、条件分支卡、应用卡 | T-P5-02 | backlog | R-WRT |
| T-P5-04 | 写"必检议题覆盖表"：逐议题标结局（成卡/并入/本包原著未涉及） | T-P5-03 | backlog | R-WRT |
| T-P5-05 | 写本章场景入口（来自已有卡） | T-P5-04 | backlog | R-WRT |
| T-P5-06 | 写本章行动工具（T1 每步有锚点；T2 标「整合者推演」） | T-P5-05 | backlog | R-WRT |
| T-P5-07 | 写章末覆盖声明 | T-P5-06 | backlog | R-WRT |
| T-P5-08 | 运行 S17 lint | T-P5-07 | backlog | R-WRT |
| T-P5-09 | 对照论点卡抽检 3 张核心卡 | T-P5-08 | backlog | R-WRT |
| T-P5-10 | 全章完成后：能力速查表 4 张、冲突消解表、附录、使用说明与全景、溯… | T-P5-09 | backlog | R-WRT |
| T-P5-11 | 交付 v0.9 并请用户试用（M3 使用验证） | T-P5-10 | backlog | R-WRT |
| T-P6-01 | S15 重跑 G0–G9 | T-P5-11 | backlog | R-AUD |
| T-P6-02 | 核心论点覆盖（逐书）：双向矩阵加语义核验 | T-P6-01 | backlog | R-AUD |
| T-P6-03 | 抽检召回循环：成书每本 15 条、来信每本 10 条，有漏即补抽补写 | T-P6-02 | backlog | R-AUD |
| T-P6-04 | G10 ① 关键词反查全量复跑 | T-P6-03 | backlog | R-AUD |
| T-P6-05 | G10 ③ 来信3 划重点召回 | T-P6-04 | backlog | R-AUD |
| T-P6-06 | 数理映射可检验率 | T-P6-05 | backlog | R-AUD |
| T-P6-07 | 5 个应用验证场景演练（含异常） | T-P6-06 | backlog | R-AUD |
| T-P6-08 | 24 字滑窗机械重复检测 | T-P6-07 | backlog | R-AUD |
| T-P6-09 | 锚点全量校验；生成用户自助核验说明 | T-P6-08 | backlog | R-AUD |
| T-P6-10 | 对抗式审查（5 角度，列 3–5 个高风险点，核实并修正） | T-P6-09 | backlog | R-AUD |
| T-P6-11 | 你抽查 20 张并用手册解决 3 个真实问题 | T-P6-10 | backlog | R-AUD |
| T-P6-12 | 缺陷定位到受影响卡，回 P4 或 P5 修复并重跑对应检查 | T-P6-11 | backlog | R-AUD |
| T-P7-01 | S18 渲染与链接检查 | T-P6-12 | backlog | R-ORCH |
| T-P7-02 | 汇总指标并写入 D4，附可复算的命令与路径 | T-P7-01 | backlog | R-ORCH |
| T-P7-03 | 附事实源声明与冻结哈希、版本记录 | T-P7-02 | backlog | R-ORCH |
| T-P7-04 | 打包：D1–D6 与进度台账终版 | T-P7-03 | backlog | R-ORCH |
| T-P7-05 | 向用户交付并说明：覆盖的范围、不覆盖的范围、已知局限 | T-P7-04 | backlog | R-ORCH |
