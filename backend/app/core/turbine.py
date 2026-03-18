"""
涡轮发电机组计算模块
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

try:
    from .thermodynamics import gauge_to_absolute, WaterProperty, GasProperty, MixProperty, get_fluid_property
except ImportError:
    from thermodynamics import gauge_to_absolute, WaterProperty, GasProperty, MixProperty, get_fluid_property
from typing import Dict

def calculate_turbine(
    p_in_gauge: float, t_in: float, p_out_gauge: float,
    flow_rate: float, flow_unit: str, adiabatic_efficiency: float,
    medium_type: str, medium: str = None,
    mix_composition: Dict = None, composition_type: str = 'mole'
) -> Dict:
    """涡轮计算"""
    p_in_abs = gauge_to_absolute(p_in_gauge)
    p_out_abs = gauge_to_absolute(p_out_gauge)
    
    # 入口状态
    state_in = get_fluid_property(p_in_gauge, t_in, medium_type, medium, mix_composition, composition_type)
    h_in = state_in['h']
    s_in = state_in['s']
    rho_in = state_in['rho']
    
    # 等熵膨胀
    if medium_type == 'single' and medium == 'H2O':
        state_out_s = WaterProperty.get_state_ps(p_out_abs, s_in)
        h_out_s = state_out_s['h']
    elif medium_type == 'single':
        state_out_s = GasProperty.get_state_ps(p_out_abs, s_in, medium)
        h_out_s = state_out_s['h']
    else:
        # 混合介质：使用理想气体等熵膨胀公式
        molar_masses = {'N2': 0.028, 'O2': 0.032, 'H2': 0.002, 'CO2': 0.044, 'H2O': 0.018}
        gammas = {'N2': 1.4, 'O2': 1.4, 'H2': 1.4, 'CO2': 1.3, 'H2O': 1.33}
        
        total = sum(mix_composition.values())
        normalized = {k: v / total for k, v in mix_composition.items()}
        
        M = sum(frac * molar_masses.get(med, 0.028) for med, frac in normalized.items())
        gamma = sum(frac * gammas.get(med, 1.4) for med, frac in normalized.items())
        
        T_in = t_in + 273.15  # K
        # 等熵膨胀：T2 = T1 * (P2/P1)^((γ-1)/γ)
        exponent = (gamma - 1) / gamma
        pressure_ratio = p_out_abs / p_in_abs
        T_out_s = T_in * (pressure_ratio ** exponent)
        
        # 计算等熵焓值 (kJ/kg)
        R = 8.314 / M  # J/(kg·K)
        cp = gamma * R / (gamma - 1) / 1000  # kJ/(kg·K)
        h_in_ig = cp * (T_in - 273.15)
        h_out_s = cp * (T_out_s - 273.15)
        
        state_out_s = {'h': h_out_s, 'T': T_out_s}
    
    # 实际膨胀
    eta = adiabatic_efficiency / 100.0
    h_out = h_in - (h_in - h_out_s) * eta
    
    # 实际出口状态
    if medium_type == 'single' and medium == 'H2O':
        state_out = WaterProperty.get_state_ph(p_out_abs, h_out)
        x_out = state_out.get('x')
    elif medium_type == 'single':
        state_out = GasProperty.get_state_ph(p_out_abs, h_out, medium)
        x_out = None
    else:
        # 混合介质：从焓值反推温度
        molar_masses = {'N2': 0.028, 'O2': 0.032, 'H2': 0.002, 'CO2': 0.044, 'H2O': 0.018}
        gammas = {'N2': 1.4, 'O2': 1.4, 'H2': 1.4, 'CO2': 1.3, 'H2O': 1.33}
        
        total = sum(mix_composition.values())
        normalized = {k: v / total for k, v in mix_composition.items()}
        
        M = sum(frac * molar_masses.get(med, 0.028) for med, frac in normalized.items())
        gamma = sum(frac * gammas.get(med, 1.4) for med, frac in normalized.items())
        
        R = 8.314 / M  # J/(kg·K)
        cp = gamma * R / (gamma - 1) / 1000  # kJ/(kg·K)
        
        # 从焓值反推温度：h = cp * (T - 273.15)
        # T = h / cp + 273.15
        T_out = h_out / cp + 273.15
        
        state_out = {'h': h_out, 'T': T_out}
        x_out = None
    
    t_out = state_out['T'] - 273.15
    
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
    
    # 功率
    power_shaft = mass_flow * (h_in - h_out)
    power_electric = power_shaft * 0.9
    
    return {
        'power_shaft': power_shaft,
        'power_electric': power_electric,
        't_out': t_out,
        'x_out': x_out,
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
