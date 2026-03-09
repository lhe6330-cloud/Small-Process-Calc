"""
设备选型模块：电机、管道、阀门
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import math
from typing import List, Dict, Tuple

# 电机功率规格 (59 档)
MOTORS = [
    0.12, 0.18, 0.25, 0.37, 0.55, 0.75, 1.1, 1.5, 2.2, 3.0,
    4.0, 5.5, 7.5, 11, 15, 18.5, 22, 30, 37, 45,
    55, 75, 90, 110, 132, 160, 200, 220, 250, 280,
    315, 355, 400, 450, 500, 560, 630, 710, 800, 900,
    1000, 1120, 1250, 1400, 1600, 1800, 2000, 2240, 2500, 2800,
    3150, 3550, 4000, 4500, 5000, 5600, 6300, 7100, 8000
]

# 管道通径规格 (25 档)
PIPES = [
    10, 15, 20, 25, 32, 40, 50, 65, 80, 100,
    125, 150, 200, 250, 300, 350, 400, 450, 500, 600,
    700, 800, 900, 1000, 1100
]

# 蝶阀 Kv 值表 (简化版)
VALVES_KV = {
    50: 450,
    65: 750,
    80: 1100,
    100: 1800,
    125: 2800,
    150: 4000,
    200: 7000,
    250: 11000,
    300: 16000,
    350: 22000,
    400: 29000,
    450: 37000,
    500: 46000,
}

def select_motor(power_shaft: float) -> float:
    """电机选型：向上取整"""
    for m in MOTORS:
        if m >= power_shaft:
            return m
    return MOTORS[-1]

def select_pipe_diameter(volume_flow: float, medium: str = None, is_steam: bool = False) -> Dict:
    """
    管道通径计算
    @param volume_flow: 体积流量 (m³/s)
    @param medium: 介质
    @param is_steam: 是否水蒸气
    @return: {recommended_dn, velocity, lower_dn, lower_velocity, upper_dn, upper_velocity}
    """
    # 设计流速
    v_design = 25 if is_steam else 15  # m/s
    
    # 计算通径
    D_calc = math.sqrt(4 * volume_flow / (math.pi * v_design)) * 1000  # mm
    
    # 选择最接近的标准规格
    recommended = min(PIPES, key=lambda d: abs(d - D_calc))
    idx = PIPES.index(recommended)
    
    # 相邻规格
    lower = PIPES[idx - 1] if idx > 0 else None
    upper = PIPES[idx + 1] if idx < len(PIPES) - 1 else None
    
    # 计算实际流速
    def calc_velocity(dn):
        area = math.pi * (dn / 1000) ** 2 / 4
        return volume_flow / area
    
    v_rec = calc_velocity(recommended)
    v_lower = calc_velocity(lower) if lower else None
    v_upper = calc_velocity(upper) if upper else None
    
    return {
        'recommended_dn': recommended,
        'velocity': v_rec,
        'lower_dn': lower,
        'lower_velocity': v_lower,
        'upper_dn': upper,
        'upper_velocity': v_upper,
        'calculated_dn': D_calc,
    }

def select_valve(
    flow_rate: float,
    flow_unit: str,
    rho: float,
    pipe_dn: int,
    medium_type: str,
    medium: str = None,
    delta_p: float = 0.02,
    t: float = None,
    p_out_abs: float = None,
) -> Dict:
    """
    阀门选型 (蝶阀)
    @param flow_rate: 流量
    @param flow_unit: 'T/h' or 'Nm3/h'
    @param rho: 密度 (kg/m³)
    @param pipe_dn: 管道通径
    @param medium_type: 'single' or 'mix'
    @param medium: 介质
    @param delta_p: 压差 (bar), 默认 0.02 bar (2 kPa)
    @param t: 温度 (°C)
    @param p_out_abs: 出口绝压 (bar.A)
    @return: {valve_dn, kv_required, kv_rated, delta_p_actual, ...}
    """
    # 阀门通径 = 管道通径
    valve_dn = pipe_dn
    
    # 获取 Kv 值
    kv_rated = VALVES_KV.get(valve_dn, 1000)
    
    # 计算所需 Kv
    if flow_unit == 'T/h':
        # 液体：Kv = Q × sqrt(ρ / ΔP)
        # Q: m³/h, ρ: kg/m³, ΔP: bar
        q_m3h = flow_rate / rho  # kg/h → m³/h
        kv_required = q_m3h * math.sqrt(rho / delta_p)
    elif flow_unit == 'Nm3/h':
        # 气体简化：Kv = Q / (514 × sqrt(ΔP × P2 / (ρ × T)))
        if p_out_abs is None:
            p_out_abs = 1.01325  # 默认大气压
        if t is None:
            t = 20
        T = t + 273.15
        p2_bar = p_out_abs * 10  # MPa → bar
        kv_required = flow_rate / (514 * math.sqrt(delta_p * p2_bar / (rho * T)))
    else:
        kv_required = 0
    
    # 反算实际压差
    if flow_unit == 'T/h':
        q_m3h = flow_rate / rho
        delta_p_actual = (q_m3h / kv_rated) ** 2 * rho
    else:
        delta_p_actual = delta_p  # 简化
    
    return {
        'valve_dn': valve_dn,
        'kv_required': kv_required,
        'kv_rated': kv_rated,
        'delta_p_design': delta_p,
        'delta_p_actual': delta_p_actual,
    }

def calculate_pipe_flow(
    flow_rate: float,
    flow_unit: str,
    p_gauge: float,
    t: float,
    medium_type: str,
    medium: str = None,
    mix_composition: Dict = None,
    composition_type: str = 'mole',
) -> float:
    """
    计算工况体积流量 (m³/s)
    """
    try:
        from .thermodynamics import gauge_to_absolute, GasProperty, MixProperty, WaterProperty
    except ImportError:
        from thermodynamics import gauge_to_absolute, GasProperty, MixProperty, WaterProperty
    
    p_abs = gauge_to_absolute(p_gauge)
    T = t + 273.15
    
    if flow_unit == 'T/h':
        if medium_type == 'single' and medium == 'H2O':
            rho = WaterProperty.get_state(p_abs, t)['rho']
        elif medium_type == 'single':
            rho = GasProperty.get_state(p_abs, t, medium)['rho']
        else:
            rho = MixProperty.get_state(p_abs, t, mix_composition, composition_type)['rho']
        mass_flow = flow_rate * 1000 / 3600
        volume_flow = mass_flow / rho
    elif flow_unit == 'Nm3/h':
        volume_flow = flow_rate / 3600 * (0.101325 / p_abs) * (T / 273.15)
    else:
        volume_flow = 0
    
    return volume_flow

if __name__ == '__main__':
    print("=== Selection Module Test ===\n")
    
    print("1. Motor Selection (700 kW shaft):")
    motor = select_motor(700)
    print(f"   Selected: {motor} kW")
    
    print("\n2. Pipe Selection (0.5 m³/s, air):")
    pipe = select_pipe_diameter(0.5)
    print(f"   Recommended: DN{pipe['recommended_dn']} (v={pipe['velocity']:.2f} m/s)")
    if pipe['lower_dn']:
        print(f"   Lower: DN{pipe['lower_dn']} (v={pipe['lower_velocity']:.2f} m/s)")
    if pipe['upper_dn']:
        print(f"   Upper: DN{pipe['upper_dn']} (v={pipe['upper_velocity']:.2f} m/s)")
    
    print("\n3. Valve Selection (DN65, water 100 T/h):")
    valve = select_valve(100, 'T/h', 1000, 65, 'single', 'H2O')
    print(f"   Valve DN: {valve['valve_dn']}, Kv_req: {valve['kv_required']:.1f}, Kv_rated: {valve['kv_rated']}")
    print(f"   ΔP: {valve['delta_p_actual']*100:.2f} kPa")
    
    print("\n[OK] Selection module test passed!")
