#!/usr/bin/env python3
"""
GaN 功率器件计算工具

子命令:
  cond          导通损耗
  sw            开关损耗
  junction      结温估算（含瞬态热阻抗修正）
  rds           Rds(on) 温度修正
  dyn-rds       动态 Rds(on) 退化修正
  short-circuit 短路耐受时间估算
  life          可靠性寿命外推（Arrhenius）
  avalanche     雪崩能量能力反查

所有子命令均打印输入参数与假设，便于在报告中标注来源。
"""

import argparse
import math
import sys

# GaN 功率器件 Rds(on) 正温度系数典型范围（比 Si 小）
TC_SI_TYPICAL = 0.004      # 1/°C，硅 MOSFET 典型
TC_GAN_TYPICAL = 0.0025     # 1/°C，GaN 典型（不同工艺差异大）


def _fmt(x, n=3):
    return f"{x:,.{n}f}"


def cmd_cond(a):
    r_ohm = a.rds_on / 1000.0  # mΩ → Ω
    p_single = a.i_rms ** 2 * r_ohm * a.duty
    p_total = p_single * a.n_par
    print("=" * 62)
    print("导通损耗计算 (Conduction Loss)")
    print("=" * 62)
    print(f"  假设: I_rms={a.i_rms} A, Rds(on)={a.rds_on} mΩ ({r_ohm} Ω), D={a.duty}, 并联数={a.n_par}")
    print(f"  公式: P = I_rms² × Rds(on) × D × N")
    print("-" * 62)
    print(f"  单管导通损耗      : {_fmt(p_single, 3)} W")
    print(f"  总导通损耗 ({a.n_par} 管并联): {_fmt(p_total, 3)} W")
    if a.tj and a.rth_ja:
        t_rise = p_total / a.rth_ja
        print(f"  结温升 (Rth(j-a)={a.rth_ja} °C/W): {_fmt(t_rise, 1)} °C")
        print(f"  估算结温 (T_amb={a.t_amb} °C): {_fmt(a.t_amb + t_rise, 1)} °C")
    print("-" * 62)
    print("  注意: Rds(on) 应先用 rds 子命令做温度修正后再代入本计算")
    return p_total


def cmd_sw(a):
    # uJ → J, P = E(J) × f(Hz)
    e_sw_j = (a.e_on + a.e_off + a.e_coss) * 1e-6
    p_single = e_sw_j * a.f
    p_total = p_single * a.n_par
    print("=" * 62)
    print("开关损耗计算 (Switching Loss)")
    print("=" * 62)
    print(f"  假设: Eon={a.e_on} uJ, Eoff={a.e_off} uJ, Ecoss={a.e_coss} uJ, f={a.f/1e3:.1f} kHz, 并联数={a.n_par}")
    print("  公式: P = (Eon + Eoff + Ecoss) × f × N")
    print("  说明: Ecoss 为硬开关 Coss 换流能量（软开关下可大幅降低）")
    print("-" * 62)
    print(f"  单管开关损耗      : {_fmt(p_single, 3)} W")
    print(f"  总开关损耗 ({a.n_par} 管并联): {_fmt(p_total, 3)} W")
    print("-" * 62)
    print("  注意: Eon/Eoff 必须来自数据手册在对应 Vds/Id/结温下的实测值")
    return p_total


def cmd_junction(a):
    p = a.p
    t_rise_steady = p * a.rth_ja
    t_j = a.t_amb + t_rise_steady
    print("=" * 62)
    print("结温估算 (Junction Temperature)")
    print("=" * 62)
    print(f"  假设: P={p} W, Rth(j-a)={a.rth_ja} °C/W, T_amb={a.t_amb} °C")
    print("  公式: Tj = T_amb + P × Rth(j-a)")
    print("-" * 62)
    print(f"  稳态温升          : {_fmt(t_rise_steady, 1)} °C")
    print(f"  估算结温          : {_fmt(t_j, 1)} °C")
    if a.tj_max:
        margin = a.tj_max - t_j
        print(f"  结温余量 (限值 {a.tj_max} °C): {_fmt(margin, 1)} °C")
        if margin < 0:
            print("  ⚠️  超温: 需降损耗、提散热或降 Tj 限值")
        elif margin < 20:
            print("  ⚠️  余量偏小: 建议复核热路径与工况假设")
    print("-" * 62)
    print("  注意: 脉冲工况需用瞬态热阻抗曲线 Zth(t) 而非稳态 Rth")
    print("  注意: Rth(j-a) 依赖具体封装与散热条件, 需实测或数据手册值")
    return t_j


def cmd_rds(a):
    r_t = a.rds25 * (1 + a.tc * (a.t - 25))
    ratio = r_t / a.rds25
    print("=" * 62)
    print("Rds(on) 温度修正")
    print("=" * 62)
    print(f"  假设: Rds(on,25C)={a.rds25} mΩ, Tj={a.t} °C, 温度系数={a.tc*100:.3f} %/°C")
    print("  公式: Rds(T) = Rds(25) × [1 + TC × (T - 25)]")
    print("-" * 62)
    print(f"  修正后 Rds(on)    : {_fmt(r_t, 2)} mΩ")
    print(f"  相对 25°C 增幅    : {ratio:.3f}×  (+{(ratio-1)*100:.1f}%)")
    print("-" * 62)
    print("  参考: 硅 MOSFET 典型 TC≈0.4 %/°C, GaN 典型 TC≈0.25 %/°C")
    print("  注意: 以数据手册实测曲线为准, 高温段 GaN 曲线可能非线性")
    return r_t


def cmd_dyn_rds(a):
    ratio = a.rds_dyn / a.rds_dc
    print("=" * 62)
    print("动态 Rds(on) 退化修正")
    print("=" * 62)
    print(f"  假设: Rds(dc)={a.rds_dc} mΩ, Rds(dyn)={a.rds_dyn} mΩ, Vds 应力={a.v_ds} V")
    print("  公式: 损耗修正系数 = Rds(dyn) / Rds(dc)")
    print("-" * 62)
    print(f"  退化倍数          : {ratio:.3f}×  (+{(ratio-1)*100:.1f}%)")
    print(f"  导通损耗乘以该系数: 导通损耗上升 {(ratio-1)*100:.1f}%")
    print("-" * 62)
    print("  典型现象: 高压偏压后动态 Rds(on) 抬升 10%~50%, 高 Vds 下更显著")
    print("  判别: 室温静置后恢复→可逆陷阱; 不可恢复→结构或界面退化")
    print("  提示: 充电与放电方向抬升幅度通常不对称, 需分别测量")
    return ratio


def cmd_short_circuit(a):
    r_ohm = a.rds / 1000.0  # mΩ → Ω
    i_v = a.v_ds / r_ohm
    p_inst = a.v_ds * i_v
    # 绝热近似: 短路初期热量来不及传出, ΔT ≈ P·t/Cth
    # Cth 为器件+封装+PCB 铜箔的有效热容 (J/K)
    cth = a.cth
    t = cth * a.tja / p_inst
    print("=" * 62)
    print("短路耐受时间估算 (Short-Circuit Withstand)")
    print("=" * 62)
    print(f"  假设: Vds={a.v_ds} V, Rds(on)={a.rds} mΩ ({r_ohm} Ω), 允许温升={a.tja} °C, Cth={a.cth*1e3:.0f} mJ/K")
    print(f"  估算: 短路电流 = Vds/Rds = {_fmt(i_v, 1)} A, 瞬时功率 = {_fmt(p_inst/1e3, 1)} kW")
    print("  模型: 绝热近似 ΔT = P·t/Cth, 长时需叠加瞬态热阻 Rth(t)")
    print("-" * 62)
    print(f"  估算短路耐受时间  : {t*1e6:.2f} us")
    print("-" * 62)
    print("  ⚠️  GaN 短路耐受时间通常仅数微秒量级, 远短于 SiC")
    print("  提示: 必须配软关断/分级保护, 不可依赖传统过流保护")
    print("  注意: Cth 需按实际封装与 PCB 校准, 精确值以短路测试为准")
    return t


def cmd_life(a):
    k = math.exp(a.ea / 8.617e-5 * (1 / (a.use_temp + 273.15) - 1 / (a.accel_temp + 273.15)))
    life = a.accel_time * k
    print("=" * 62)
    print("可靠性寿命外推 (Arrhenius)")
    print("=" * 62)
    print(f"  假设: 加速温度={a.accel_temp} °C, 使用温度={a.use_temp} °C, Ea={a.ea} eV, 加速时长={a.accel_time} h")
    print("  公式: L = t_accel × exp[ Ea/k × (1/T_use - 1/T_acc) ]")
    print("-" * 62)
    print(f"  加速因子 AF       : {k:,.1f}×")
    print(f"  外推使用寿命      : {life/1e6:,.2f} 百万小时  ({life:,.0f} h)")
    if life > 25 * 365 * 24:
        print(f"  折合年限          : {life/(365*24):.1f} 年")
    print("-" * 62)
    print("  ⚠️  适用边界: 单一 Arrhenius 模型仅在同一失效机理主导时有效")
    print("  ⚠️  GaN 陷阱主导失效可能出现模式转换, 外推结果必须标注模型假设")
    print("  提示: 栅极寿命建议同时参考 JEDEC JEP217 流程")
    return life


def cmd_avalanche(a):
    r_ohm = a.rds / 1000.0  # mΩ → Ω
    e_j = a.e_as / 1000.0  # mJ → J
    # 雪崩期间电流近似线性上升, 三角积分: E = V·I·t/2
    i_av = a.v_ds / r_ohm
    p_avg = a.v_ds * i_av / 2
    t_av = e_j / p_avg if p_avg > 0 else 0
    print("=" * 62)
    print("雪崩能力反查 (Avalanche Capability)")
    print("=" * 62)
    print(f"  假设: E_as={a.e_as} mJ ({e_j} J), Vds={a.v_ds} V, Rds(on)={a.rds} mΩ ({r_ohm} Ω)")
    print(f"  估算: 雪崩峰值电流 = Vds/Rds = {_fmt(i_av, 1)} A, 平均功率 = {_fmt(p_avg/1e3, 1)} kW")
    print("-" * 62)
    print(f"  雪崩持续时间估算  : {t_av*1e6:.3f} us")
    print(f"  累计释放能量      : {_fmt(e_j, 4)} J")
    print("-" * 62)
    print("  ⚠️  静态 E_as 需按数据手册; 动态雪崩耐受通常显著低于静态值")
    print("  提示: 频繁进入雪崩会累积损伤, 设计应避免重复雪崩")
    print("  注意: 雪崩钳位需配合 TVS 选型, 评估过压倍数")
    return t_av


def main():
    p = argparse.ArgumentParser(
        description="GaN 功率器件计算工具",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("cond", help="导通损耗")
    c.add_argument("--i-rms", type=float, required=True, help="有效电流 RMS (A)")
    c.add_argument("--rds-on", type=float, required=True, help="导通电阻 (mΩ)")
    c.add_argument("--duty", type=float, default=1.0, help="占空比 (0~1)")
    c.add_argument("--n-par", type=int, default=1, help="并联管数")
    c.add_argument("--tj", action="store_true", help="同时估算结温")
    c.add_argument("--rth-ja", type=float, help="热阻 (°C/W), 与 --tj 同用")
    c.add_argument("--t-amb", type=float, default=40.0, help="环境温度 (°C)")
    c.set_defaults(func=cmd_cond)

    s = sub.add_parser("sw", help="开关损耗")
    s.add_argument("--e-on", type=float, required=True, help="开通能量 (uJ)")
    s.add_argument("--e-off", type=float, required=True, help="关断能量 (uJ)")
    s.add_argument("--e-coss", type=float, default=0.0, help="Coss 换流能量 (uJ), 软开关可填 0")
    s.add_argument("--f", type=float, required=True, help="开关频率 (Hz)")
    s.add_argument("--n-par", type=int, default=1, help="并联管数")
    s.set_defaults(func=cmd_sw)

    j = sub.add_parser("junction", help="结温估算")
    j.add_argument("--p", type=float, required=True, help="总损耗 (W)")
    j.add_argument("--rth-ja", type=float, required=True, help="热阻 (°C/W)")
    j.add_argument("--t-amb", type=float, required=True, help="环境温度 (°C)")
    j.add_argument("--tj-max", type=float, help="结温限值 (°C)")
    j.set_defaults(func=cmd_junction)

    r = sub.add_parser("rds", help="Rds(on) 温度修正")
    r.add_argument("--rds25", type=float, required=True, help="25°C 导通电阻 (mΩ)")
    r.add_argument("--t", type=float, required=True, help="结温 (°C)")
    r.add_argument("--tc", type=float, default=TC_GAN_TYPICAL, help="温度系数 (1/°C), 默认 GaN 0.0025")
    r.set_defaults(func=cmd_rds)

    d = sub.add_parser("dyn-rds", help="动态 Rds(on) 退化修正")
    d.add_argument("--rds-dc", type=float, required=True, help="静态导通电阻 (mΩ)")
    d.add_argument("--rds-dyn", type=float, required=True, help="动态导通电阻 (mΩ)")
    d.add_argument("--v-ds", type=float, default=800.0, help="偏压应力 (V)")
    d.set_defaults(func=cmd_dyn_rds)

    sc = sub.add_parser("short-circuit", help="短路耐受时间估算")
    sc.add_argument("--v-ds", type=float, required=True, help="短路时 Vds (V)")
    sc.add_argument("--rds", type=float, required=True, help="导通电阻 (mΩ)")
    sc.add_argument("--tja", type=float, default=80.0, help="允许温升 (°C)")
    sc.add_argument("--cth", type=float, default=0.05, help="有效热容 (J/K), 默认 0.05 即 50 mJ/K")
    sc.set_defaults(func=cmd_short_circuit)

    l = sub.add_parser("life", help="可靠性寿命外推")
    l.add_argument("--accel-temp", type=float, required=True, help="加速温度 (°C)")
    l.add_argument("--use-temp", type=float, required=True, help="使用温度 (°C)")
    l.add_argument("--ea", type=float, default=0.7, help="活化能 (eV), 常见 0.65~0.75")
    l.add_argument("--accel-time", type=float, required=True, help="加速测试时长 (h)")
    l.set_defaults(func=cmd_life)

    av = sub.add_parser("avalanche", help="雪崩能力反查")
    av.add_argument("--e-as", type=float, required=True, help="雪崩能量 (mJ)")
    av.add_argument("--v-ds", type=float, required=True, help="雪崩时 Vds (V)")
    av.add_argument("--rds", type=float, required=True, help="导通电阻 (mΩ)")
    av.set_defaults(func=cmd_avalanche)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
