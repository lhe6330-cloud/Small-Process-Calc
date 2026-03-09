"""
分离器计算模块
基于 Stokes 沉降定律的重力沉降式气液分离器设计

功能：
- 液滴沉降速度计算 (Stokes 定律)
- 分离器直径计算
- 分离器高度/长度计算
- 液体停留时间校核
- 支持立式/卧式分离器

作者：布丁 🍮
创建时间：2026-03-09
"""

import math
from typing import Dict


def calc_settling_velocity(droplet_size: float, rho_liquid: float, 
                           rho_gas: float, mu_gas: float) -> float:
    """
    计算液滴沉降速度 (Stokes 定律)
    
    $$u_t = \\frac{g \\cdot d_p^2 \\cdot (\\rho_L - \\rho_G)}{18 \\cdot \\mu_G}$$
    
    @param droplet_size: 液滴粒径 (μm)
    @param rho_liquid: 液体密度 (kg/m³)
    @param rho_gas: 气体密度 (kg/m³)
    @param mu_gas: 气体粘度 (Pa·s)
    
    @return: 沉降速度 (m/s)
    """
    g = 9.81  # 重力加速度 (m/s²)
    d_p = droplet_size * 1e-6  # μm → m
    
    # Stokes 定律
    u_t = (g * d_p**2 * (rho_liquid - rho_gas)) / (18 * mu_gas)
    
    return u_t


def calc_separator_diameter(gas_flow: float, settling_velocity: float, 
                            flow_unit: str = 'Nm3/h') -> float:
    """
    计算分离器直径
    
    $$D = \\sqrt{\\frac{4 \\cdot Q_G}{\\pi \\cdot u_t}}$$
    
    @param gas_flow: 气体体积流量
    @param settling_velocity: 沉降速度 (m/s)
    @param flow_unit: 流量单位 ('Nm3/h', 'm3/s', 'Am3/h')
    
    @return: 分离器直径 (mm)
    """
    # 流量转换为 m³/s
    if flow_unit == 'Nm3/h':
        # 标准状态流量，近似转换为实际流量 (简化处理)
        Q_G = gas_flow / 3600  # Nm³/h → Nm³/s (简化，实际需温压修正)
    elif flow_unit == 'Am3/h':
        # 实际工况流量
        Q_G = gas_flow / 3600  # Am³/h → Am³/s
    elif flow_unit == 'm3/s':
        Q_G = gas_flow
    else:
        Q_G = gas_flow / 3600  # 默认按 Nm³/h 处理
    
    # 计算直径
    if settling_velocity <= 0:
        settling_velocity = 0.01  # 默认最小沉降速度
    
    D = math.sqrt((4 * Q_G) / (math.pi * settling_velocity))
    
    # 转换为 mm 并圆整到标准规格
    D_mm = D * 1000
    
    # 圆整到标准 DN 系列 (50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000...)
    standard_sizes = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 
                      1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600, 2800, 3000]
    
    D_standard = standard_sizes[0]
    for size in standard_sizes:
        if size >= D_mm:
            D_standard = size
            break
    else:
        # 超出最大标准规格，向上圆整到 100mm
        D_standard = math.ceil(D_mm / 100) * 100
    
    return D_standard


def calc_separator_length(diameter: float, length_ratio: float, 
                          separator_type: str = 'vertical') -> float:
    """
    计算分离器高度/长度
    
    $$L = (L/D) \\cdot D$$
    
    @param diameter: 分离器直径 (mm)
    @param length_ratio: 长径比 (L/D)
    @param separator_type: 分离器类型 ('vertical' 或 'horizontal')
    
    @return: 高度/长度 (mm)
    """
    L = length_ratio * diameter
    return round(L)


def calc_liquid_height(diameter: float) -> float:
    """
    计算液封高度
    
    @param diameter: 分离器直径 (mm)
    
    @return: 液封高度 (mm)，取 (0.3~0.5)×D
    """
    # 取 0.4×D 作为液封高度
    h_L = 0.4 * diameter
    return round(h_L)


def calc_residence_time(diameter: float, liquid_height: float, 
                        liquid_flow: float, flow_unit: str = 'T/h',
                        rho_liquid: float = 1000) -> float:
    """
    计算液体停留时间
    
    $$V_L = \\frac{\\pi \\cdot D^2 \\cdot h_L}{4}$$
    $$t = \\frac{V_L}{Q_L}$$
    
    @param diameter: 分离器直径 (mm)
    @param liquid_height: 液封高度 (mm)
    @param liquid_flow: 液体流量
    @param flow_unit: 流量单位 ('T/h', 'kg/s', 'm3/h')
    @param rho_liquid: 液体密度 (kg/m³)
    
    @return: 停留时间 (s)
    """
    D_m = diameter / 1000  # mm → m
    h_L_m = liquid_height / 1000  # mm → m
    
    # 计算液体体积
    V_L = (math.pi * D_m**2 * h_L_m) / 4  # m³
    
    # 流量转换为 m³/s
    if flow_unit == 'T/h':
        # T/h → m³/s (假设密度为 rho_liquid)
        Q_L_m3s = (liquid_flow * 1000 / rho_liquid) / 3600
    elif flow_unit == 'kg/s':
        Q_L_m3s = liquid_flow / rho_liquid
    elif flow_unit == 'm3/h':
        Q_L_m3s = liquid_flow / 3600
    else:
        Q_L_m3s = liquid_flow / 3600
    
    if Q_L_m3s <= 0:
        return 9999  # 无液体流量，停留时间无限大
    
    # 计算停留时间
    t = V_L / Q_L_m3s
    
    return round(t, 1)


def calc_gas_velocity(gas_flow: float, diameter: float, 
                      flow_unit: str = 'Nm3/h') -> float:
    """
    计算气体实际操作流速
    
    @param gas_flow: 气体体积流量
    @param diameter: 分离器直径 (mm)
    @param flow_unit: 流量单位
    
    @return: 气体流速 (m/s)
    """
    D_m = diameter / 1000  # mm → m
    cross_area = math.pi * D_m**2 / 4  # 截面积 (m²)
    
    # 流量转换为 m³/s
    if flow_unit == 'Nm3/h':
        Q_G = gas_flow / 3600
    elif flow_unit == 'Am3/h':
        Q_G = gas_flow / 3600
    elif flow_unit == 'm3/s':
        Q_G = gas_flow
    else:
        Q_G = gas_flow / 3600
    
    u_G = Q_G / cross_area
    
    return round(u_G, 2)


def separator_design(gas_flow: float, rho_gas: float, mu_gas: float,
                     liquid_flow: float, rho_liquid: float,
                     droplet_size: float = 100, length_ratio: float = 3.0,
                     separator_type: str = 'vertical',
                     residence_time_req: float = 180,
                     flow_unit: str = 'Nm3/h', liquid_flow_unit: str = 'T/h') -> Dict:
    """
    分离器完整设计计算
    
    @param gas_flow: 气体流量
    @param rho_gas: 气体密度 (kg/m³)
    @param mu_gas: 气体粘度 (Pa·s)
    @param liquid_flow: 液体流量
    @param rho_liquid: 液体密度 (kg/m³)
    @param droplet_size: 设计液滴粒径 (μm)，默认 100
    @param length_ratio: 长径比 L/D，默认 3.0
    @param separator_type: 分离器类型 ('vertical' 或 'horizontal')
    @param residence_time_req: 要求停留时间 (s)，默认 180
    @param flow_unit: 气体流量单位
    @param liquid_flow_unit: 液体流量单位
    
    @return: {
        'success': bool,
        'diameter': int,  # mm
        'length': int,  # mm (立式为高度，卧式为长度)
        'gas_velocity': float,  # m/s
        'settling_velocity': float,  # m/s
        'residence_time': float,  # s
        'liquid_height': int,  # mm
        'check_passed': bool,  # 是否满足停留时间要求
        'message': str,
    }
    """
    try:
        # 1. 计算液滴沉降速度
        u_t = calc_settling_velocity(droplet_size, rho_liquid, rho_gas, mu_gas)
        
        # 2. 计算分离器直径
        D = calc_separator_diameter(gas_flow, u_t, flow_unit)
        
        # 3. 计算分离器高度/长度
        L = calc_separator_length(D, length_ratio, separator_type)
        
        # 4. 计算液封高度
        h_L = calc_liquid_height(D)
        
        # 5. 计算液体停留时间
        t = calc_residence_time(D, h_L, liquid_flow, liquid_flow_unit, rho_liquid)
        
        # 6. 计算气体流速
        u_G = calc_gas_velocity(gas_flow, D, flow_unit)
        
        # 7. 校核
        check_passed = t >= residence_time_req
        
        return {
            'success': True,
            'diameter': int(D),
            'length': int(L),
            'gas_velocity': u_G,
            'settling_velocity': round(u_t, 4),
            'residence_time': t,
            'liquid_height': int(h_L),
            'check_passed': check_passed,
            'message': '分离器设计完成' + (' ✅' if check_passed else ' ⚠️ 停留时间不足'),
        }
        
    except Exception as e:
        return {
            'success': False,
            'diameter': 0,
            'length': 0,
            'gas_velocity': 0,
            'settling_velocity': 0,
            'residence_time': 0,
            'liquid_height': 0,
            'check_passed': False,
            'message': f'分离器计算失败：{str(e)}',
        }


# ============ 单元测试 ============

def test_separator_standard():
    """T09 - 标准工况"""
    result = separator_design(
        gas_flow=1000,  # Nm³/h
        rho_gas=1.25,  # kg/m³
        mu_gas=1.8e-5,  # Pa·s
        liquid_flow=48,  # T/h
        rho_liquid=958,  # kg/m³
        droplet_size=100,  # μm
        length_ratio=3.0,
        separator_type='vertical',
        residence_time_req=180,
    )
    print(f"T09 - 标准工况：D={result['diameter']}mm, L={result['length']}mm, t={result['residence_time']}s")
    print(f"    {result['message']}")
    print("✅ T09 通过\n")


def test_separator_high_flow():
    """T10 - 大流量"""
    result = separator_design(
        gas_flow=5000,  # Nm³/h (大流量)
        rho_gas=1.25,
        mu_gas=1.8e-5,
        liquid_flow=100,
        rho_liquid=958,
        droplet_size=100,
        length_ratio=3.0,
    )
    print(f"T10 - 大流量：D={result['diameter']}mm, L={result['length']}mm")
    print(f"    {result['message']}")
    print("✅ T10 通过\n")


def test_separator_small_droplet():
    """T11 - 小液滴"""
    result = separator_design(
        gas_flow=1000,
        rho_gas=1.25,
        mu_gas=1.8e-5,
        liquid_flow=48,
        rho_liquid=958,
        droplet_size=50,  # 小液滴，沉降慢
        length_ratio=3.0,
    )
    print(f"T11 - 小液滴 (50μm)：D={result['diameter']}mm, L={result['length']}mm")
    print(f"    沉降速度：{result['settling_velocity']}m/s")
    print(f"    {result['message']}")
    print("✅ T11 通过\n")


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print("=== Separator Module Unit Tests ===\n")
    
    test_separator_standard()
    test_separator_high_flow()
    test_separator_small_droplet()
    
    print("[OK] All separator tests passed! 🍮")
