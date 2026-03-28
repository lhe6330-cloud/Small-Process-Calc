"""
涡轮发电机组计算模块
支持：
- 单一介质（H2O/N2/O2/Air/CO2/H2）
- 混合介质（N2+O2+H2O 等）
- 进口含液自动判断（0-5% 含水量）
- 相变潜热修正（二分法 + 低温饱和蒸气压公式）
"""
import sys
import math
sys.stdout.reconfigure(encoding='utf-8')

try:
    from .thermodynamics import (
        gauge_to_absolute, WaterProperty, GasProperty, MixProperty,
        get_fluid_property, get_water_saturation_pressure, get_water_latent_heat,
        get_gas_cp
    )
    from .vle import calc_inlet_liquid_frac
except ImportError:
    from thermodynamics import (
        gauge_to_absolute, WaterProperty, GasProperty, MixProperty,
        get_fluid_property, get_water_saturation_pressure, get_water_latent_heat,
        get_gas_cp
    )
    from vle import calc_inlet_liquid_frac
from typing import Dict
from CoolProp.CoolProp import PropsSI


def p_sat_water(t_celsius: float) -> float:
    """
    计算水的饱和蒸气压（支持 -60°C 到 +200°C）
    分段公式：
    1. T >= 0°C: CoolProp (IAPWS-IF97)
    2. -40°C <= T < 0°C: Wexler-Hyland (ASHRAE 标准)
    3. T < -40°C: Goff-Gratch (气象学标准)
    """
    if t_celsius >= 0:
        # 0°C 以上：CoolProp (IAPWS-IF97)
        try:
            return PropsSI('P', 'T', t_celsius + 273.15, 'Q', 1, 'H2O')
        except:
            pass

    if t_celsius >= -40:
        # -40°C 到 0°C: Wexler-Hyland (ASHRAE 标准)
        T = t_celsius + 273.15
        ln_p = (
            -5800.2206 / T
            + 1.3914993
            - 0.048640239 * T
            + 0.41764768e-4 * T**2
            - 0.14452093e-7 * T**3
            + 6.5459673 * math.log(T)
        )
        return math.exp(ln_p)
    else:
        # -60°C 到 -40°C: Goff-Gratch
        T = t_celsius + 273.15
        T0 = 373.15
        log10_p = (
            -7.90298 * (T0 / T - 1)
            + 5.02808 * math.log10(T0 / T)
            - 1.3816e-7 * (10 ** (11.344 * (1 - T / T0)) - 1)
            + 8.1328e-3 * (10 ** (-3.49149 * (T0 / T - 1)) - 1)
            + math.log10(101324.6)
        )
        return 10 ** log10_p


def h_fg_water(t_celsius: float) -> float:
    """
    计算水的汽化潜热（kJ/kg）（支持 -60°C 到 +200°C）
    """
    if t_celsius >= 0:
        # 0°C 以上：CoolProp
        try:
            h_l = PropsSI('H', 'T', t_celsius + 273.15, 'Q', 0, 'H2O') / 1000
            h_g = PropsSI('H', 'T', t_celsius + 273.15, 'Q', 1, 'H2O') / 1000
            return h_g - h_l
        except:
            pass
    # 0°C 以下或 CoolProp 失败：简化公式
    # h_fg ≈ 2500 - 2.36 * t (kJ/kg)
    return 2500 - 2.36 * t_celsius


def calc_power_for_turbine(
    t_out: float,
    t_in: float,
    p_out_abs: float,
    m_dot: float,
    mix_composition: Dict,
    composition_type: str,
    mass_N2_frac: float,
    mass_H2O_frac: float,
    y_N2_in: float,
    y_H2O_in: float,
    M_N2: float,
    M_H2O: float,
    denom: float
) -> Dict:
    """
    给定出口温度，计算涡轮轴功率（包含相变）
    """
    # 1. 饱和蒸气压
    p_sat = p_sat_water(t_out)
    p_sat_MPa = p_sat / 1e6

    # 2. 冷凝量
    y_H2O_max = p_sat_MPa / p_out_abs
    liquid_frac = max(0, y_H2O_in - y_H2O_max)

    # 3. 显热焓降
    try:
        Cp_N2 = PropsSI('Cpmass', 'T', t_out + 273.15, 'P', p_out_abs * 1e6, 'N2') / 1000
        Cp_H2O = PropsSI('Cpmass', 'T', t_out + 273.15, 'P', p_out_abs * 1e6, 'H2O') / 1000
    except:
        Cp_N2 = 1.04
        Cp_H2O = 2.0

    sensible_h = mass_N2_frac * Cp_N2 * (t_in - t_out) + mass_H2O_frac * Cp_H2O * (t_in - t_out)

    # 4. 潜热焓降
    mass_condensed = liquid_frac * M_H2O / denom
    if liquid_frac > 0.001:
        h_fg = h_fg_water(t_out)
        latent_h = mass_condensed * h_fg
    else:
        latent_h = 0

    # 5. 总焓降和功率
    delta_h = sensible_h + latent_h
    P_calc = m_dot * delta_h

    return {
        't_out': t_out,
        'p_sat': p_sat,
        'liquid_frac': liquid_frac,
        'sensible_h': sensible_h,
        'latent_h': latent_h,
        'delta_h': delta_h,
        'P_calc': P_calc,
    }

def calculate_turbine(
    p_in_gauge: float, t_in: float, p_out_gauge: float,
    flow_rate: float, flow_unit: str, adiabatic_efficiency: float,
    medium_type: str, medium: str = None,
    mix_composition: Dict = None, composition_type: str = 'mole'
) -> Dict:
    """
    涡轮计算（支持进口含液和相变潜热修正）

    计算流程：
    1. 进口 Flash 计算 → 得到进口含液量
    2. 两相进口能量平衡 → 计算混合焓/熵
    3. 等熵膨胀 + 出口潜热修正（联合迭代）→ 得到出口温度和含液量
    """
    p_in_abs = gauge_to_absolute(p_in_gauge)
    p_out_abs = gauge_to_absolute(p_out_gauge)

    # ============ 步骤 1: 入口校验和进口 Flash ============

    # 单一介质 H2O 的入口校验
    if medium_type == 'single' and medium == 'H2O':
        T_sat = WaterProperty.get_saturation_temp(p_in_abs)
        if t_in <= T_sat:
            return {
                'success': False,
                'error': True,
                'error_message': f'涡轮入口温度过低！当前温度 {t_in}°C，该压力下的饱和温度为 {T_sat:.2f}°C。请确保入口为过热蒸汽状态。'
            }
        inlet_liquid_frac = 0.0  # 过热蒸汽，无液相
    elif medium_type == 'mix' and mix_composition:
        # 混合介质：自动计算进口含液量
        # 先将百分比格式转换为小数格式
        mix_comp_decimal = {k: v / 100.0 for k, v in mix_composition.items()}
        inlet_liquid_frac = calc_inlet_liquid_frac(p_in_gauge, t_in, mix_comp_decimal)
    else:
        inlet_liquid_frac = 0.0  # 单一气体（N2/O2 等），无液相

    # ============ 步骤 2: 进口状态计算 ============

    # 初始化 vapor_comp（用于后续冷凝计算）
    # 使用小数格式
    vapor_comp = {k: v / 100.0 for k, v in mix_composition.items()} if medium_type == 'mix' and mix_composition else None

    # 计算进口焓/熵（考虑含液）
    if medium_type == 'mix' and inlet_liquid_frac > 0.001:
        # 两相进口：分别计算气相和液相

        # 气相组成（扣除冷凝的水）
        y_h2o_total = vapor_comp.get('H2O', 0) if vapor_comp else 0
        y_h2o_vapor = y_h2o_total - inlet_liquid_frac
        if vapor_comp:
            vapor_comp['H2O'] = y_h2o_vapor
            # 归一化
            total_vapor = sum(vapor_comp.values())
            if total_vapor > 0:
                vapor_comp = {k: v / total_vapor for k, v in vapor_comp.items()}

        # 气相焓/熵
        state_in_vapor = MixProperty.get_state(p_in_abs, t_in, vapor_comp, composition_type)
        h_in_vapor = state_in_vapor['h']
        s_in_vapor = state_in_vapor['s']

        # 液相焓/熵（纯水）
        h_in_liquid = WaterProperty.get_state(p_in_abs, t_in)['h']
        s_in_liquid = WaterProperty.get_state(p_in_abs, t_in)['s']

        # 混合焓/熵（质量加权平均）
        # 近似：inlet_liquid_frac 是质量分数
        h_in = (1 - inlet_liquid_frac) * h_in_vapor + inlet_liquid_frac * h_in_liquid
        s_in = (1 - inlet_liquid_frac) * s_in_vapor + inlet_liquid_frac * s_in_liquid
        rho_in = state_in_vapor['rho']  # 用气相密度近似
    else:
        # 单相进口（或含液量可忽略）
        state_in = get_fluid_property(p_in_gauge, t_in, medium_type, medium, mix_composition, composition_type)
        h_in = state_in['h']
        s_in = state_in['s']
        rho_in = state_in['rho']

    # ============ 步骤 3: 等熵膨胀（无相变近似） ============

    if medium_type == 'single' and medium == 'H2O':
        state_out_s = WaterProperty.get_state_ps(p_out_abs, s_in)
        h_out_s = state_out_s['h']
    elif medium_type == 'single':
        state_out_s = GasProperty.get_state_ps(p_out_abs, s_in, medium)
        h_out_s = state_out_s['h']
    else:
        # 混合介质：使用 CoolProp SRK 模型计算等熵膨胀
        state_out_s = MixProperty.get_state_ps(p_out_abs, s_in, mix_composition, composition_type)
        h_out_s = state_out_s['h']

    # 实际膨胀（考虑绝热效率）
    eta = adiabatic_efficiency / 100.0
    h_out_no_phase = h_in - (h_in - h_out_s) * eta

    # ============ 步骤 4: 相变潜热修正（联合迭代） ============

    liquid_percent = None
    liquid_warning = None
    t_out = None

    if medium_type == 'single' and medium == 'H2O':
        # 单一 H2O：用 IF97 直接计算（考虑相变潜热）
        # 从实际膨胀焓计算出口状态
        state_out = WaterProperty.get_state_ph(p_out_abs, h_out_no_phase)
        x_out = state_out.get('x')
        t_out = state_out['T'] - 273.15
        h_out = state_out['h']  # 保存出口焓用于后续功率计算
        if x_out is not None:
            liquid_percent = (1 - x_out) * 100
            if liquid_percent > 5:
                liquid_warning = f'出口含液率 {liquid_percent:.1f}%，超过 5% 建议值！'

    elif medium_type == 'mix' and mix_composition and mix_composition.get('H2O', 0) > 0.5:
        # 混合介质含水：需要相变潜热修正（使用二分法）
        # 注意：mix_composition 是百分比格式（如 {N2: 98, H2O: 2}），先转换为小数

        # 将百分比格式转换为小数格式
        mix_comp_decimal = {k: v / 100.0 for k, v in mix_composition.items()}

        # 计算质量分数和流量相关参数
        M_N2 = 28.01
        M_H2O = 18.02
        y_N2_in = mix_comp_decimal.get('N2', 0)
        y_H2O_in = mix_comp_decimal.get('H2O', 0)
        denom = y_N2_in * M_N2 + y_H2O_in * M_H2O
        mass_N2_frac = (y_N2_in * M_N2) / denom
        mass_H2O_frac = (y_H2O_in * M_H2O) / denom

        # 质量流量
        if flow_unit == 'T/h':
            m_dot = flow_rate * 1000 / 3600
        elif flow_unit == 'Nm3/h':
            rho_std = MixProperty.get_state(0.101325, 0, mix_composition, composition_type)['rho']
            m_dot = flow_rate * rho_std / 3600
        else:
            m_dot = flow_rate  # 默认

        # 气相组成（vapor_comp 已经是小数格式）
        y_N2_in_vapor = vapor_comp.get('N2', 0) if vapor_comp else mix_comp_decimal.get('N2', 0)
        y_H2O_in_vapor = vapor_comp.get('H2O', 0) if vapor_comp else mix_comp_decimal.get('H2O', 0)

        # 目标功率（无相变近似）
        P_target = m_dot * (h_in - h_out_no_phase)

        # 二分法求解出口温度
        t_min = -40.0  # 最低搜索温度
        t_max = t_in   # 最高搜索温度
        tolerance = 0.01  # 1% 功率误差容限
        max_iter = 50

        t_out_bisection = None
        liquid_frac_bisection = 0.0
        P_calc_bisection = 0.0
        delta_h_bisection = 0.0
        latent_h_bisection = 0.0
        sensible_h_bisection = 0.0

        for iteration in range(max_iter):
            t_mid = (t_min + t_max) / 2
            result = calc_power_for_turbine(
                t_out=t_mid,
                t_in=t_in,
                p_out_abs=p_out_abs,
                m_dot=m_dot,
                mix_composition=mix_comp_decimal,
                composition_type=composition_type,
                mass_N2_frac=mass_N2_frac,
                mass_H2O_frac=mass_H2O_frac,
                y_N2_in=y_N2_in_vapor,
                y_H2O_in=y_H2O_in_vapor,
                M_N2=M_N2,
                M_H2O=M_H2O,
                denom=denom
            )
            P_calc = result['P_calc']
            error = P_calc - P_target

            if abs(error) / abs(P_target) < tolerance:
                t_out_bisection = t_mid
                liquid_frac_bisection = result['liquid_frac']
                P_calc_bisection = P_calc
                delta_h_bisection = result['delta_h']
                latent_h_bisection = result['latent_h']
                sensible_h_bisection = result['sensible_h']
                break

            if error > 0:
                # P_calc > P_target，焓降太大，温度太高
                t_min = t_mid
            else:
                # P_calc < P_target，焓降太小，温度太低
                t_max = t_mid
        else:
            # 未收敛，使用当前值
            t_out_bisection = (t_min + t_max) / 2
            result = calc_power_for_turbine(
                t_out=t_out_bisection,
                t_in=t_in,
                p_out_abs=p_out_abs,
                m_dot=m_dot,
                mix_composition=mix_comp_decimal,
                composition_type=composition_type,
                mass_N2_frac=mass_N2_frac,
                mass_H2O_frac=mass_H2O_frac,
                y_N2_in=y_N2_in_vapor,
                y_H2O_in=y_H2O_in_vapor,
                M_N2=M_N2,
                M_H2O=M_H2O,
                denom=denom
            )
            liquid_frac_bisection = result['liquid_frac']
            P_calc_bisection = result['P_calc']
            delta_h_bisection = result['delta_h']
            latent_h_bisection = result['latent_h']
            sensible_h_bisection = result['sensible_h']

        t_out = t_out_bisection
        liquid_frac_total = inlet_liquid_frac + liquid_frac_bisection
        liquid_percent = liquid_frac_total * 100

        if liquid_percent > 5:
            liquid_warning = f'出口含液率 {liquid_percent:.1f}%，超过 5% 建议值！'

        # 出口焓（用于功率计算）
        h_out = h_in - delta_h_bisection
        x_out = None

        # 保存相变潜热值
        latent_power = m_dot * latent_h_bisection  # kW
        sensible_power = m_dot * sensible_h_bisection  # kW

        # ============ 相变补偿计算 ============
        # 经验公式：轴功率补偿 = 原轴功率 + 相变潜热 × 0.13
        # 然后根据补偿后的功率重新迭代出口温度
        power_base = m_dot * delta_h_bisection  # 基础轴功率（无补偿）
        power_compensated = power_base + latent_power * 0.13  # 补偿后的目标功率

        # 重新迭代出口温度（根据补偿后的功率）
        # 目标：找到新的 t_out，使得新温度下的基础功率 = power_compensated
        # 注意：第二次迭代时不再应用补偿公式，直接找温度使得基础功率等于目标值

        # 二分法重新迭代温度
        t_min2 = -40.0
        t_max2 = t_in
        t_out_final = t_out_bisection

        # 记录第二次迭代过程
        iteration_history = []

        for iter_idx in range(30):
            t_mid = (t_min2 + t_max2) / 2
            result = calc_power_for_turbine(
                t_out=t_mid,
                t_in=t_in,
                p_out_abs=p_out_abs,
                m_dot=m_dot,
                mix_composition=mix_comp_decimal,
                composition_type=composition_type,
                mass_N2_frac=mass_N2_frac,
                mass_H2O_frac=mass_H2O_frac,
                y_N2_in=y_N2_in_vapor,
                y_H2O_in=y_H2O_in_vapor,
                M_N2=M_N2,
                M_H2O=M_H2O,
                denom=denom
            )
            # 第二次迭代：只计算基础功率（不应用补偿公式）
            P_base = m_dot * result['delta_h']
            error = P_base - power_compensated

            iteration_history.append({
                'iter': iter_idx + 1,
                't_mid': round(t_mid, 6),
                'P_base': round(P_base, 6),
                'target_P': round(power_compensated, 6),
                'error': round(error, 6)
            })

            if abs(error) / power_compensated < 0.001:
                t_out_final = t_mid
                # 更新最终结果
                liquid_frac_bisection = result['liquid_frac']
                delta_h_bisection = result['delta_h']
                latent_h_bisection = result['latent_h']
                sensible_h_bisection = result['sensible_h']
                latent_power = m_dot * latent_h_bisection
                sensible_power = m_dot * sensible_h_bisection
                break

            if error > 0:
                t_min2 = t_mid  # 功率太大，温度太高
            else:
                t_max2 = t_mid  # 功率太小，温度太低

        t_out = t_out_final
        liquid_frac_total = inlet_liquid_frac + liquid_frac_bisection
        liquid_percent = liquid_frac_total * 100

        if liquid_percent > 5:
            liquid_warning = f'出口含液率 {liquid_percent:.1f}%，超过 5% 建议值！'

        # 最终出口焓
        h_out = h_in - delta_h_bisection

    else:
        # 不含水或单一气体：无相变
        h_out = h_out_no_phase  # 无相变时，出口焓=实际膨胀焓
        if medium_type == 'single':
            state_out = GasProperty.get_state_ph(p_out_abs, h_out, medium)
            t_out = state_out['T'] - 273.15
            x_out = None
        else:
            try:
                state_out = MixProperty.get_state_ph(p_out_abs, h_out, mix_composition, composition_type)
                t_out = state_out['T'] - 273.15
            except:
                t_out = 0  # 计算失败时的默认值
            x_out = None

        # 无相变时，显热功率=总功率，潜热功率=0
        # 注意：power_shaft 在步骤 5 计算，这里先初始化
        sensible_power = 0
        latent_power = 0

    # ============ 步骤 5: 质量流量和功率计算 ============

    # 质量流量
    if flow_unit == 'T/h':
        mass_flow = flow_rate * 1000 / 3600
    elif flow_unit == 'Nm3/h':
        if medium_type == 'single' and medium == 'H2O':
            rho_std = 0.804
        elif medium_type == 'single':
            rho_std = GasProperty.get_state(0.101325, 0, medium)['rho']
        else:
            rho_std = MixProperty.get_state(0.101325, 0, mix_composition, composition_type)['rho']
        mass_flow = flow_rate * rho_std / 3600
    else:
        raise ValueError(f"Unknown flow_unit: {flow_unit}")

    # 功率计算
    if medium_type == 'mix' and mix_composition and mix_composition.get('H2O', 0) > 0.5:
        # 相变补偿情况：第二次迭代已找到新温度，功率 = 补偿后的目标功率
        power_shaft = power_compensated if 'power_compensated' in dir() else mass_flow * (h_in - h_out)
    else:
        power_shaft = mass_flow * (h_in - h_out)

    power_electric = power_shaft * 0.9

    return {
        'success': True,
        'power_shaft': power_shaft,
        'power_electric': power_electric,
        't_out': t_out,
        'x_out': x_out,
        'liquid_percent': liquid_percent,
        'liquid_warning': liquid_warning,
        'h_in': h_in,
        'h_out': h_out,
        'mass_flow': mass_flow,
        'rho_in': rho_in,
        'sensible_power': sensible_power if medium_type == 'mix' and mix_composition and mix_composition.get('H2O', 0) > 0.5 else 0,
        'latent_power': latent_power if medium_type == 'mix' and mix_composition and mix_composition.get('H2O', 0) > 0.5 else 0,
        'iteration_history': iteration_history if medium_type == 'mix' and mix_composition and mix_composition.get('H2O', 0) > 0.5 else [],
    }

if __name__ == '__main__':
    print("=== Turbine Test ===\n")
    print("1. H2O Turbine (0.5 MPa.G, 200C -> 0.1 MPa.G, eta=85%, 1 T/h):")
    r = calculate_turbine(0.5, 200, 0.1, 1.0, 'T/h', 85, 'single', 'H2O')
    print(f"   Shaft: {r['power_shaft']:.2f} kW, Electric: {r['power_electric']:.2f} kW")
    print(f"   T_out: {r['t_out']:.2f} C, x_out: {r['x_out']}")

    print("\n2. N2 Turbine (0.5 MPa.G, 200C -> 0.1 MPa.G, eta=85%, 1000 Nm3/h):")
    r = calculate_turbine(0.5, 200, 0.1, 1000, 'Nm3/h', 85, 'single', 'N2')
    print(f"   Shaft: {r['power_shaft']:.2f} kW, Electric: {r['power_electric']:.2f} kW")
    print(f"   T_out: {r['t_out']:.2f} C")

    print("\n3. Mix Turbine - Air (0.5 MPa.G, 200C -> 0.1 MPa.G, eta=85%, 1000 Nm3/h):")
    r = calculate_turbine(0.5, 200, 0.1, 1000, 'Nm3/h', 85, 'mix',
                          mix_composition={'N2': 79, 'O2': 21}, composition_type='mole')
    print(f"   Shaft: {r['power_shaft']:.2f} kW, Electric: {r['power_electric']:.2f} kW")
    print(f"   T_out: {r['t_out']:.2f} C")

    print("\n4. Mix Turbine - Custom (0.5 MPa.G, 200C -> 0.1 MPa.G, eta=85%, 1000 Nm3/h):")
    r = calculate_turbine(0.5, 200, 0.1, 1000, 'Nm3/h', 85, 'mix',
                          mix_composition={'N2': 90, 'CO2': 10}, composition_type='mole')
    print(f"   Shaft: {r['power_shaft']:.2f} kW, Electric: {r['power_electric']:.2f} kW")
    print(f"   T_out: {r['t_out']:.2f} C")

    print("\n5. Mix Turbine - N2+H2O with phase change (0.25 MPa.G, 40C -> 0.01 MPa.G, eta=85%, 10000 Nm3/h):")
    r = calculate_turbine(0.25, 40, 0.01, 10000, 'Nm3/h', 85, 'mix',
                          mix_composition={'N2': 0.98, 'H2O': 0.02}, composition_type='mole')
    print(f"   Shaft: {r['power_shaft']:.2f} kW, Electric: {r['power_electric']:.2f} kW")
    print(f"   T_out: {r['t_out']:.2f} C, Liquid: {r['liquid_percent']:.2f}%")

    print("\n[OK] Turbine test passed!")
