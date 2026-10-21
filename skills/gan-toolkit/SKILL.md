---
name: gan-toolkit
description: "Technical toolkit for GaN power device experts. Provides GaN material property reference tables, 650V/900V/1200V roadmap comparison, JEDEC/AEC reliability standard checklist, failure mode library, and a Python calculator for conduction loss, switching loss, junction temperature, Rds(on) temperature correction, dynamic Rds(on) derating, and reliability life extrapolation. Use when GaN power device quantitative analysis or standards lookup is needed."
---

# GaN 功率器件技术工具箱

本技能包为氮化镓功率器件专家团提供底层技术基准与计算工具，供成员在分析中直接引用，避免重复推导和口径不一致。

## 目录

| 资源 | 用途 |
|------|------|
| `references/material-and-device-basics.md` | GaN/Si/SiC 材料参数对比、器件结构、关键电学参数、电压段路线图 |
| `references/reliability-standards.md` | JEDEC / AEC / IEC 可靠性标准清单、测试项与判据、认证路线 |
| `references/failure-mode-library.md` | GaN 失效模式库：机理、特征、检测手段、纠正措施 |
| `scripts/gan_calc.py` | 损耗、热、动态 Rds(on)、寿命外推计算器 |
| `templates/report-template.html` | 器件/系统分析报告 HTML 模板 |

## 使用方式

### 1. 查材料与器件基准
需要 GaN 与 Si/SiC 的物性对比、典型电压段规格区间、或 650V/900V/1200V 的设计要点差异时，读取 `references/material-and-device-basics.md`。

### 2. 查可靠性标准与认证路径
需要确认某项测试是否必测、标准条款号、应力条件、样本量要求或认证差距时，读取 `references/reliability-standards.md`。

### 3. 查失效模式
需要按现象反查可能失效机理、选择检测手段、或给出纠正预防措施时，读取 `references/failure-mode-library.md`。

### 4. 算数
用 `scripts/gan_calc.py` 做定量计算，避免心算错误：

```bash
# 导通损耗（多管并联、按占空比）
python3 scripts/gan_calc.py cond --i-rms 20 --rds-on 70 --duty 0.5 --n-par 2

# 开关损耗（Eon/Eoff 实测值 + Coss 硬开关能量）
python3 scripts/gan_calc.py sw --e-on 8.0 --e-off 12.0 --e-coss 15.0 --f 500e3 --n-par 2

# 结温估算（含瞬态热阻抗修正）
python3 scripts/gan_calc.py junction --p 4.5 --rth-ja 25 --t-amb 45

# Rds(on) 温度修正（GaN 温度系数显著低于 Si）
python3 scripts/gan_calc.py rds --rds25 70 --t 125 --tc 0.003

# 动态 Rds(on) 退化修正（充电/放电不对称）
python3 scripts/gan_calc.py dyn-rds --rds-dc 70 --rds-dyn 95 --v-ds 800

# 短路耐受时间估算（GaN 硬约束，验证 SiC 替代必要性）
python3 scripts/gan_calc.py short-circuit --v-ds 400 --rds 70 --tja 80 --rth-ja 25

# 可靠性寿命外推（Arrhenius，标注模型适用边界）
python3 scripts/gan_calc.py life --accel-temp 175 --use-temp 55 --ea 0.7 --accel-time 1000

# 雪崩能量能力反查
python3 scripts/gan_calc.py avalanche --e-as 200 --v-ds 400 --rds 70
```

所有命令均支持 `--help` 查看参数。脚本输出为可读表格，参数与假设会一并打印，便于在报告中标注来源。

## 引用规范

- 引用材料参数时，注明数据来源类型：公开数据手册 / 行业普遍水平 / 需实测确认
- 计算结果必须连同输入假设一起引用，不得只给数字
- 脚本无法覆盖的量（例如具体厂商的实测 Eon/Eoff）必须标注"需实测确认"，不得用估算值冒充
- 寿命外推结果必须附带模型名、加速条件与适用边界说明

## 边界

本工具箱不替代实测与仿真：
- 动态 Rds(on) 恢复行为、陷阱能级等需 DLTS/TDR 测量确认
- 死区时间、环路电感等布局相关参数需按实际 PCB 提取
- 产能、价格、份额等产业数据不在本工具箱范围
