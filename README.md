# 氮化镓功率器件专家团（GaN Power Device Expert Team）

氮化镓功率器件全栈专家团队：外延衬底、器件设计与栅极工艺、可靠性失效、封装驱动集成、系统方案设计，直到国产替代研判。7 个角色按 SOP 串并行协作，覆盖从一颗 GaN 管的设计定型到一条产业链的判断。

## 类型

Team 型（多角色协作团队）

## 团队成员

| 成员 ID | 名字 | 职业 | 职责 |
|---------|------|------|------|
| gan-power-device-team-lead | 沈定策 | 氮化镓技术首席 | 编排调度、跨层收敛、最终结论与取舍 |
| gan-epitaxy-material-expert | 秦长晶 | 外延与材料工艺专家 | 衬底选型、MOCVD 外延、缺陷与掺杂管理 |
| gan-device-design-expert | 陶通 | 器件设计与工艺专家 | HEMT 结构设计、栅极工艺、Rds(on) 与雪崩、TCAD |
| gan-device-reliability-expert | 邵明 | 可靠性与失效分析专家 | 栅极退化、动态 Rds(on)、寿命模型、认证与 FA |
| gan-packaging-integration-expert | 纪承 | 封装与集成工程专家 | 封装形式、寄生参数、驱动集成、热与布局 |
| gan-application-system-expert | 薛翔 | 应用与系统设计专家 | 拓扑选型、损耗建模、EMI 与安规、系统方案 |
| gan-supply-chain-analyst | 苏源 | 产业链与国产替代分析师 | 产业链卡点、产能、国产替代、竞争格局与标的 |

## 功能

- **器件架构选型**：p-GaN 栅 vs 凹槽 MIS 栅 vs 肖特基栅的三维对比（阈值稳定性、栅退化、负压容限、Cgd、工艺成本），并给出按电压等级的选型结论。
- **器件设计与参数计算**：异质结与 2DEG 设计、Rds(on) 分项分解与降低路径、场截止与雪崩设计、TCAD 仿真与帕累托取舍曲线，输出带测试条件的参数表。
- **外延与材料诊断**：蓝宝石/SiC/硅基三路线对比，MOCVD 外延结构与工艺窗口，VPD、位错、氮空位等缺陷归因，AFM/SEM/PL/SRIM/SIMS/XRD 表征方案与判读。
- **可靠性与失效分析**：HTGB/HTGR 加速应力设计、动态 Rds(on) 机理与可逆性判别、TDDB 与寿命外推、AEC-Q101/Q102 与 JEDEC JEP163/JEP217 认证差距表、完整失效模式库（硬失效/参数漂移/系统假失效/制造缺陷四类共 20+ 条目）。
- **封装与集成工程**：DFN/DFN-8/SON/QFN/LGA/模组选型矩阵、热预算与瞬态热阻、集成驱动方案、共源电感与振铃抑制、dv/dt 误开通定量判据、布局要点分级清单。
- **系统方案与拓扑**：半桥/全桥/LLC/图腾柱等拓扑匹配、导通与开关损耗建模、GaN 与 SiC/Si 的系统级选型矩阵、开关频率与死区设计、EMI 与安规（IEC 62368-1、EN 55032）整改路径。
- **产业链与国产替代**：分层产业链图谱与卡点分级（区分真卡点与低国产化率）、全球与国内产能地图、8 寸爬坡难点、成本结构拆解、供需与竞争格局推演、标的映射与证伪条件。
- **计算工具**：内置 `gan_calc.py`，覆盖导通损耗、开关损耗、结温估算、Rds(on) 温度修正、动态 Rds(on) 退化系数、短路耐受时间、Arrhenius 寿命外推、雪崩能量反查共 8 个子命令，输出附输入假设。

## 预设工作流

| 工作流 | 触发条件 | 编排 |
|--------|---------|------|
| A 全新器件/方案设计 | 「做一颗」「设计一款」 | Phase1 并行（外延+器件+应用）→ Phase2 串行（封装→可靠性）→ 汇编 |
| B 失效/异常排障 | 给出异常现象或失效件 | Phase1 并行（可靠性+器件设计）→ Phase2 串行（外延/封装验证手段）→ 根因树 |
| C 国产替代与产业链研判 | 问卡点、国产化率、产能、格局 | Phase1 并行（产业链+器件+外延）→ Phase2 串行（终端需求验证）→ 图谱+标的 |
| D 技术选型对比 | GaN vs SiC vs Si | Phase1 并行（器件级+系统级+商业级）→ Phase2 串行（可靠性维度）→ 选型矩阵 |

## 使用示例

- 我要做一款 650V 氮化镓快充开关方案，从导通电阻、开关损耗、栅极驱动到 PCB 布局帮我把设计参数和风险点算一遍。
- 我们这批 p-GaN 栅极 650V 氮化镓器件在 800V 偏压后动态导通电阻上升超过 30%，帮我定位根因并给出验证方案。
- 帮我梳理氮化镓功率器件的产业链卡点与国产替代进度，并判断未来两年 650V 与 1200V 段的供需和竞争格局。

## 目录结构

```
gan-power-device/
├── .codebuddy-plugin/plugin.json     # 专家清单与展示配置
├── settings.json                     # Team 型主理人绑定
├── agents/                           # 7 个角色定义（主理人 + 6 团员）
│   ├── gan-power-device-team-lead.md
│   ├── gan-epitaxy-material-expert.md
│   ├── gan-device-design-expert.md
│   ├── gan-device-reliability-expert.md
│   ├── gan-packaging-integration-expert.md
│   ├── gan-application-system-expert.md
│   └── gan-supply-chain-analyst.md
├── skills/gan-toolkit/               # 技术工具箱
│   ├── SKILL.md
│   ├── references/
│   │   ├── material-and-device-basics.md   # 材料物性、器件结构、电压段路线图
│   │   ├── reliability-standards.md        # JEDEC/AEC/IEC 标准与认证路线
│   │   └── failure-mode-library.md         # 失效模式库
│   ├── scripts/gan_calc.py                 # 损耗/热/寿命计算器
│   └── templates/report-template.html      # 报告模板
├── avatars/                          # 团队与成员头像
└── README.md
```

## 头像

头像已自动生成在 `avatars/` 目录下。如需替换为自定义头像，要求：
- 格式：PNG（推荐）或 JPG
- 尺寸：512×512 px
- 大小：单张不超过 500KB

## 安装

将专家包目录放到专家目录下：

```
/Users/dzp/.workbuddy/plugins/marketplaces/my-experts/plugins/gan-power-device/
```

然后运行注册命令使其可见：

```bash
python3 scripts/register_expert.py <expert-dir>
```

## 打包分享

```bash
python3 scripts/package_expert.py <expert-dir>
```

## 使用注意

- 涉及具体厂商的实测参数（Eon/Eoff、Eas、动态 Rds(on) 恢复行为）必须以实际规格书或实测为准，本包提供的是方法论与量级参考。
- 产能、价格、份额等产业数据具有强时效性，引用时须标注时点与来源类型。
- GaN 与 SiC 的失效机理、栅极结构、动态 Rds(on) 行为全不相同，不可混用结论。
