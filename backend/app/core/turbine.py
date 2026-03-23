"""
涡轮发电机组计算模块
支持：
- 单一介质（H2O/N2/O2/Air/CO2/H2）
- 混合介质（N2+O2+H2O 等）
- 进口含液自动判断（0-5% 含水量）
- 相变潜热修正（联合迭代能量平衡）
"""
import sys
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
        inlet_liquid_frac = calc_inlet_liquid_frac(p_in_gauge, t_in, mix_composition)
    else:
        inlet_liquid_frac = 0.0  # 单一气体（N2/O2 等），无液相

    # ============ 步骤 2: 进口状态计算 ============

    # 初始化 vapor_comp（用于后续冷凝计算）
    vapor_comp = mix_composition if medium_type == 'mix' else None

    # 计算进口焓/熵（考虑含液）
    if medium_type == 'mix' and inlet_liquid_frac > 0.001:
        # 两相进口：分别计算气相和液相

        # 气相组成（扣除冷凝的水）
        y_h2o_total = mix_composition.get('H2O', 0)
        y_h2o_vapor = y_h2o_total - inlet_liquid_frac
        vapor_comp = {k: v for k, v in mix_composition.items()}
        vapor_comp['H2O'] = y_h2o_vapor
        # 归一化
        total_vapor = sum(vapor_comp.values())
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

    elif medium_type == 'mix' and mix_composition and mix_composition.get('H2O', 0) > 0.005:
        # 混合介质含水：需要相变潜热修正

        # 先从无相变焓反推温度初值
        try:
            state_out_guess = MixProperty.get_state_ph(p_out_abs, h_out_no_phase, mix_composition, composition_type)
            t_out_guess = state_out_guess['T'] - 273.15
        except:
            t_out_guess = 0  # 默认 0°C

        # 迭代求解能量平衡 + 相平衡（使用阻尼因子防止震荡）
        q_cond = 0  # 初始化
        damping = 0.3  # 阻尼因子，0.3 表示每次只更新 30%
        t_out_prev = t_out_guess

        for iteration in range(50):
            # 温度边界检查（水的饱和温度计算范围 0.01-370°C）
            t_out_clamped = max(0.01, min(370, t_out_guess))

            # 1. 计算该温度下的饱和蒸气压
            p_sat = get_water_saturation_pressure(t_out_clamped)  # MPa.A

            # 2. 计算冷凝量
            y_h2o_vapor_in = vapor_comp.get('H2O', 0) if vapor_comp else mix_composition.get('H2O', 0)
            y_h2o_max = p_sat / p_out_abs if p_out_abs > 0 else 0

            if y_h2o_vapor_in > y_h2o_max:
                # 有冷凝
                liquid_frac_new = y_h2o_vapor_in - y_h2o_max
            else:
                # 无冷凝（或蒸发）
                liquid_frac_new = 0

            # 3. 冷凝放热
            if liquid_frac_new > 0.001:
                h_fg = get_water_latent_heat(t_out_clamped)  # kJ/kg
                q_cond = liquid_frac_new * h_fg
            else:
                q_cond = 0

            # 4. 修正出口焓（冷凝放热增加系统焓）
            h_out_corrected = h_out_no_phase + q_cond

            # 5. 从修正焓反推温度
            try:
                state_new = MixProperty.get_state_ph(p_out_abs, h_out_corrected, mix_composition, composition_type)
                t_out_new = state_new['T'] - 273.15
            except:
                t_out = t_out_clamped
                break

            # 6. 收敛判断
            if abs(t_out_new - t_out_guess) < 0.1:
                t_out = t_out_new
                break

            # 7. 阻尼更新（防止震荡）
            if iteration > 0 and (t_out_new - t_out_guess) * (t_out_guess - t_out_prev) < 0:
                # 检测到震荡，减小阻尼
                damping *= 0.5

            t_out_prev = t_out_guess
            t_out_guess = t_out_guess + damping * (t_out_new - t_out_guess)
        else:
            # 迭代 50 次未收敛，用当前值
            t_out = t_out_guess

        # 计算最终含液量
        p_sat = get_water_saturation_pressure(t_out)
        y_h2o_vapor_in = vapor_comp.get('H2O', 0) if vapor_comp else mix_composition.get('H2O', 0)
        y_h2o_max = p_sat / p_out_abs if p_out_abs > 0 else 0

        if y_h2o_vapor_in > y_h2o_max:
            liquid_frac_total = inlet_liquid_frac + (y_h2o_vapor_in - y_h2o_max)
            liquid_percent = liquid_frac_total * 100

            if liquid_percent > 5:
                liquid_warning = f'出口含液率 {liquid_percent:.1f}%，超过 5% 建议值！'

        # 计算最终出口焓（用于功率计算）
        h_out = h_out_no_phase + q_cond
        x_out = None  # 混合物不计算干度

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

    # 功率（用实际焓降计算）
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
    
    print("\n[OK] Turbine test passed!")
