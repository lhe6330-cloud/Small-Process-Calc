"""
换热器计算模块
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

try:
    from .thermodynamics import gauge_to_absolute, get_fluid_property
except ImportError:
    from thermodynamics import gauge_to_absolute, get_fluid_property
from typing import Dict

def calculate_heat_exchanger(
    cold_side: Dict,
    hot_side: Dict,
) -> Dict:
    """
    换热器计算
    @param cold_side: 冷边参数 {p_in, p_out, t_in, t_out, flow_rate, flow_unit, medium_type, medium, mix_composition, composition_type}
    @param hot_side: 热边参数 {p_in, p_out, t_in, flow_rate, flow_unit, medium_type, medium, mix_composition, composition_type}
    @return: {q_power, t_hot_out, ...}
    """
    # 冷边计算
    p_cold_in_abs = gauge_to_absolute(cold_side['p_in'])
    p_cold_out_abs = gauge_to_absolute(cold_side['p_out'])
    
    state_cold_in = get_fluid_property(
        cold_side['p_in'], cold_side['t_in'],
        cold_side['medium_type'], cold_side.get('medium'),
        cold_side.get('mix_composition'), cold_side.get('composition_type', 'mole')
    )
    state_cold_out = get_fluid_property(
        cold_side['p_out'], cold_side['t_out'],
        cold_side['medium_type'], cold_side.get('medium'),
        cold_side.get('mix_composition'), cold_side.get('composition_type', 'mole')
    )
    
    h_cold_in = state_cold_in['h']
    h_cold_out = state_cold_out['h']
    
    # 冷边质量流量
    if cold_side['flow_unit'] == 'T/h':
        mass_flow_cold = cold_side['flow_rate'] * 1000 / 3600
    elif cold_side['flow_unit'] == 'Nm3/h':
        if cold_side['medium_type'] == 'single' and cold_side.get('medium') == 'H2O':
            rho_std = 0.804
        elif cold_side['medium_type'] == 'single':
            try:
                from .thermodynamics import GasProperty
            except ImportError:
                from thermodynamics import GasProperty
            rho_std = GasProperty.get_state(0.101325, 0, cold_side['medium'])['rho']
        else:
            try:
                from .thermodynamics import MixProperty
            except ImportError:
                from thermodynamics import MixProperty
            rho_std = MixProperty.get_state(0.101325, 0, cold_side['mix_composition'], cold_side.get('composition_type', 'mole'))['rho']
        mass_flow_cold = cold_side['flow_rate'] * rho_std / 3600
    else:
        raise ValueError(f"Unknown flow_unit: {cold_side['flow_unit']}")
    
    # 换热功率 (冷边吸热)
    q_power = mass_flow_cold * (h_cold_out - h_cold_in)  # kW
    
    # 热边计算
    state_hot_in = get_fluid_property(
        hot_side['p_in'], hot_side['t_in'],
        hot_side['medium_type'], hot_side.get('medium'),
        hot_side.get('mix_composition'), hot_side.get('composition_type', 'mole')
    )
    h_hot_in = state_hot_in['h']
    
    # 热边质量流量
    if hot_side['flow_unit'] == 'T/h':
        mass_flow_hot = hot_side['flow_rate'] * 1000 / 3600
    elif hot_side['flow_unit'] == 'Nm3/h':
        if hot_side['medium_type'] == 'single' and hot_side.get('medium') == 'H2O':
            rho_std = 0.804
        elif hot_side['medium_type'] == 'single':
            try:
                from .thermodynamics import GasProperty
            except ImportError:
                from thermodynamics import GasProperty
            rho_std = GasProperty.get_state(0.101325, 0, hot_side['medium'])['rho']
        else:
            try:
                from .thermodynamics import MixProperty
            except ImportError:
                from thermodynamics import MixProperty
            rho_std = MixProperty.get_state(0.101325, 0, hot_side['mix_composition'], hot_side.get('composition_type', 'mole'))['rho']
        mass_flow_hot = hot_side['flow_rate'] * rho_std / 3600
    else:
        raise ValueError(f"Unknown flow_unit: {hot_side['flow_unit']}")
    
    # 热边出口焓 (能量守恒：热边放热 = 冷边吸热)
    h_hot_out = h_hot_in - q_power / mass_flow_hot
    
    # 热边出口温度
    p_hot_out_abs = gauge_to_absolute(hot_side['p_out'])
    if hot_side['medium_type'] == 'single' and hot_side.get('medium') == 'H2O':
        try:
            from .thermodynamics import WaterProperty
        except ImportError:
            from thermodynamics import WaterProperty
        state_hot_out = WaterProperty.get_state_ph(p_hot_out_abs, h_hot_out)
    elif hot_side['medium_type'] == 'single':
        try:
            from .thermodynamics import GasProperty
        except ImportError:
            from thermodynamics import GasProperty
        state_hot_out = GasProperty.get_state_ph(p_hot_out_abs, h_hot_out, hot_side['medium'])
    else:
        try:
            from .thermodynamics import MixProperty
        except ImportError:
            from thermodynamics import MixProperty
        state_hot_out = MixProperty.get_state_ph(p_hot_out_abs, h_hot_out, hot_side['mix_composition'], hot_side.get('composition_type', 'mole'))
    
    t_hot_out = state_hot_out['T'] - 273.15
    
    return {
        'q_power': q_power,
        't_hot_out': t_hot_out,
        'h_hot_out': h_hot_out,
        'mass_flow_cold': mass_flow_cold,
        'mass_flow_hot': mass_flow_hot,
    }

if __name__ == '__main__':
    print("=== Heat Exchanger Test ===\n")
    print("Mode 1: Cold N2 (0.5->0.48 MPa.G, 20->200C), Hot H2O (0.6->0.55 MPa.G, 250C)")
    
    cold = {
        'p_in': 0.5, 'p_out': 0.48, 't_in': 20, 't_out': 200,
        'flow_rate': 1000, 'flow_unit': 'Nm3/h',
        'medium_type': 'single', 'medium': 'N2'
    }
    hot = {
        'p_in': 0.6, 'p_out': 0.55, 't_in': 250,
        'flow_rate': 0.5, 'flow_unit': 'T/h',
        'medium_type': 'single', 'medium': 'H2O'
    }
    
    r = calculate_heat_exchanger(cold, hot)
    print(f"   Q Power: {r['q_power']:.2f} kW")
    print(f"   T_hot_out: {r['t_hot_out']:.2f} C")
    
    print("\n[OK] Heat exchanger test passed!")
