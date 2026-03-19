"""
模式 2/3 计算接口
模式 2: 先膨胀后回热 (涡轮 → 换热器)
模式 3: 直接膨胀 (仅涡轮)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

from turbine import calculate_turbine
from heat_exchanger import calculate_heat_exchanger
from selection import select_motor, select_pipe_diameter, select_valve, calculate_pipe_flow
from thermodynamics import get_fluid_property
from typing import Dict

def calculate_mode2(turbine_in: Dict, turbine_params: Dict, hx_cold_params: Dict, hx_hot_params: Dict) -> Dict:
    """模式 2: 先膨胀后回热"""
    # 1. 涡轮计算
    turbine_result = calculate_turbine(
        p_in_gauge=turbine_in['p_in'], t_in=turbine_in['t_in'],
        p_out_gauge=turbine_params['p_out'],
        flow_rate=turbine_in['flow_rate'], flow_unit=turbine_in['flow_unit'],
        adiabatic_efficiency=turbine_params['adiabatic_efficiency'],
        medium_type=turbine_in['medium_type'], medium=turbine_in['medium'],
        mix_composition=turbine_in.get('mix_composition'),
        composition_type=turbine_in.get('composition_type', 'mole'),
    )

    # 检查涡轮计算是否失败（如入口温度过低）
    if not turbine_result.get('success', True):
        return turbine_result

    # 2. 换热器计算 (冷边入口=涡轮出口)
    hx_cold_params['p_in'] = turbine_params['p_out']
    hx_cold_params['t_in'] = turbine_result['t_out']
    hx_result = calculate_heat_exchanger(hx_cold_params, hx_hot_params)
    
    # 3. 设备选型
    motor = select_motor(turbine_result['power_shaft'])
    vol_in = calculate_pipe_flow(turbine_in['flow_rate'], turbine_in['flow_unit'],
        turbine_in['p_in'], turbine_in['t_in'], turbine_in['medium_type'],
        turbine_in['medium'], turbine_in.get('mix_composition'), turbine_in.get('composition_type', 'mole'))
    pipe_in = select_pipe_diameter(vol_in, turbine_in['medium'], turbine_in['medium'] == 'H2O' and turbine_in['t_in'] > 100)
    
    vol_out = calculate_pipe_flow(turbine_in['flow_rate'], turbine_in['flow_unit'],
        hx_cold_params['p_out'], hx_cold_params['t_out'], turbine_in['medium_type'],
        turbine_in['medium'], turbine_in.get('mix_composition'), turbine_in.get('composition_type', 'mole'))
    pipe_out = select_pipe_diameter(vol_out, turbine_in['medium'], turbine_in['medium'] == 'H2O' and hx_cold_params['t_out'] > 100)
    
    state_in = get_fluid_property(turbine_in['p_in'], turbine_in['t_in'],
        turbine_in['medium_type'], turbine_in['medium'],
        turbine_in.get('mix_composition'), turbine_in.get('composition_type', 'mole'))
    valve = select_valve(turbine_in['flow_rate'], turbine_in['flow_unit'],
        state_in['rho'], pipe_in['recommended_dn'],
        turbine_in['medium_type'], turbine_in['medium'])
    
    return {
        "success": True,
        "turbine": {
            # 输入参数
            "p_in": turbine_in['p_in'],
            "t_in": turbine_in['t_in'],
            "p_out": turbine_params['p_out'],
            "flow_rate": turbine_in['flow_rate'],
            "flow_unit": turbine_in['flow_unit'],
            "medium_type": turbine_in['medium_type'],
            "medium": turbine_in['medium'],
            "mix_composition": turbine_in.get('mix_composition'),
            "composition_type": turbine_in.get('composition_type', 'mole'),
            # 计算结果
            "t_out": turbine_result['t_out'],
            "x_out": turbine_result['x_out'],
            "liquid_percent": turbine_result.get('liquid_percent'),
            "liquid_warning": turbine_result.get('liquid_warning'),
            "power_shaft": turbine_result['power_shaft'],
            "power_electric": turbine_result['power_electric'],
            "rho_in": turbine_result.get('rho_in'),
            "rho_out": turbine_result.get('rho_out'),
            "mass_flow": turbine_result.get('mass_flow'),
        },
        "heat_exchanger": {"q_power": hx_result['q_power'], "t_hot_out": hx_result['t_hot_out']},
        "selection": {"motor": motor, "pipe_inlet": pipe_in, "pipe_outlet": pipe_out, "valve": valve}
    }

def calculate_mode3(turbine_in: Dict, turbine_params: Dict) -> Dict:
    """模式 3: 直接膨胀"""
    turbine_result = calculate_turbine(
        p_in_gauge=turbine_in['p_in'], t_in=turbine_in['t_in'],
        p_out_gauge=turbine_params['p_out'],
        flow_rate=turbine_in['flow_rate'], flow_unit=turbine_in['flow_unit'],
        adiabatic_efficiency=turbine_params['adiabatic_efficiency'],
        medium_type=turbine_in['medium_type'], medium=turbine_in['medium'],
        mix_composition=turbine_in.get('mix_composition'),
        composition_type=turbine_in.get('composition_type', 'mole'),
    )

    # 检查涡轮计算是否失败（如入口温度过低）
    if not turbine_result.get('success', True):
        return turbine_result

    motor = select_motor(turbine_result['power_shaft'])
    vol_in = calculate_pipe_flow(turbine_in['flow_rate'], turbine_in['flow_unit'],
        turbine_in['p_in'], turbine_in['t_in'], turbine_in['medium_type'],
        turbine_in['medium'], turbine_in.get('mix_composition'), turbine_in.get('composition_type', 'mole'))
    pipe_in = select_pipe_diameter(vol_in, turbine_in['medium'], turbine_in['medium'] == 'H2O' and turbine_in['t_in'] > 100)
    
    vol_out = calculate_pipe_flow(turbine_in['flow_rate'], turbine_in['flow_unit'],
        turbine_params['p_out'], turbine_result['t_out'], turbine_in['medium_type'],
        turbine_in['medium'], turbine_in.get('mix_composition'), turbine_in.get('composition_type', 'mole'))
    pipe_out = select_pipe_diameter(vol_out, turbine_in['medium'], turbine_in['medium'] == 'H2O' and turbine_result['t_out'] > 100)
    
    state_in = get_fluid_property(turbine_in['p_in'], turbine_in['t_in'],
        turbine_in['medium_type'], turbine_in['medium'],
        turbine_in.get('mix_composition'), turbine_in.get('composition_type', 'mole'))
    valve = select_valve(turbine_in['flow_rate'], turbine_in['flow_unit'],
        state_in['rho'], pipe_in['recommended_dn'],
        turbine_in['medium_type'], turbine_in['medium'])
    
    return {
        "success": True,
        "turbine": {
            # 输入参数
            "p_in": turbine_in['p_in'],
            "t_in": turbine_in['t_in'],
            "p_out": turbine_params['p_out'],
            "flow_rate": turbine_in['flow_rate'],
            "flow_unit": turbine_in['flow_unit'],
            "medium_type": turbine_in['medium_type'],
            "medium": turbine_in['medium'],
            "mix_composition": turbine_in.get('mix_composition'),
            "composition_type": turbine_in.get('composition_type', 'mole'),
            # 计算结果
            "t_out": turbine_result['t_out'],
            "x_out": turbine_result['x_out'],
            "liquid_percent": turbine_result.get('liquid_percent'),
            "liquid_warning": turbine_result.get('liquid_warning'),
            "power_shaft": turbine_result['power_shaft'],
            "power_electric": turbine_result['power_electric'],
            "rho_in": turbine_result.get('rho_in'),
            "rho_out": turbine_result.get('rho_out'),
            "mass_flow": turbine_result.get('mass_flow'),
        },
        "selection": {"motor": motor, "pipe_inlet": pipe_in, "pipe_outlet": pipe_out, "valve": valve}
    }

if __name__ == '__main__':
    print("=== Mode 2/3 Test ===\n")
    turbine_in = {'p_in': 0.6, 't_in': 250, 'flow_rate': 1000, 'flow_unit': 'Nm3/h', 'medium_type': 'single', 'medium': 'N2'}
    turbine_params = {'p_out': 0.3, 'adiabatic_efficiency': 85}
    hx_cold = {'p_out': 0.28, 't_out': 150, 'flow_rate': 1000, 'flow_unit': 'Nm3/h', 'medium_type': 'single', 'medium': 'N2'}
    hx_hot = {'p_in': 0.4, 'p_out': 0.35, 't_in': 200, 'flow_rate': 800, 'flow_unit': 'Nm3/h', 'medium_type': 'single', 'medium': 'Air'}
    
    r2 = calculate_mode2(turbine_in, turbine_params, hx_cold, hx_hot)
    print(f"Mode 2: Turbine={r2['turbine']['power_shaft']:.2f} kW, HX={r2['heat_exchanger']['q_power']:.2f} kW")
    
    r3 = calculate_mode3(turbine_in, turbine_params)
    print(f"Mode 3: Turbine={r3['turbine']['power_shaft']:.2f} kW, Motor={r3['selection']['motor']} kW")
    print("\n[OK] Mode 2/3 test passed!")
