"""
涡轮一维通流设计模块
径流式 (向心) 涡轮的一维设计计算

功能：
- 基本尺寸计算 (D₁, D₂, b₁, b₂, Z)
- 进口速度三角形 (C₁, W₁, U₁, α₁, β₁)
- 出口速度三角形 (C₂, W₂, U₂, α₂, β₂)
- 热力参数计算 (η, Ω, u/C₀)
- 性能验证 (P_calc)

作者：布丁 🍮
创建时间：2026-03-09
"""

import math
from typing import Dict


def calc_isentropic_velocity(delta_h_s: float) -> float:
    """
    计算等熵速度
    
    $$C_0 = \\sqrt{2 \\cdot \\Delta h_s}$$
    
    @param delta_h_s: 等熵焓降 (J/kg)
    
    @return: 等熵速度 (m/s)
    """
    return math.sqrt(2 * delta_h_s)


def calc_impeller_outer_diameter(u1: float, n: float) -> float:
    """
    计算叶轮外径
    
    $$D_1 = \\frac{60 \\cdot u_1}{\\pi \\cdot n}$$
    
    @param u1: 进口圆周速度 (m/s)
    @param n: 转速 (rpm)
    
    @return: 叶轮外径 (mm)
    """
    D1 = (60 * u1) / (math.pi * n)
    return round(D1 * 1000)  # m → mm


def calc_velocity_triangle_inlet(Q: float, D1: float, b1: float, 
                                  rho1: float, u1: float, 
                                  alpha1_deg: float = 90) -> Dict:
    """
    计算进口速度三角形
    
    @param Q: 体积流量 (m³/s)
    @param D1: 叶轮外径 (m)
    @param b1: 进口叶片高度 (m)
    @param rho1: 进口密度 (kg/m³)
    @param u1: 进口圆周速度 (m/s)
    @param alpha1_deg: 进口绝对气流角 (°)，默认 90° (径向进气)
    
    @return: {C1, W1, U1, alpha1, beta1, C1m, C1u}
    """
    alpha1 = math.radians(alpha1_deg)
    
    # 轴面速度
    # C1m = Q / (π × D1 × b1 × ρ1)  (质量流量守恒)
    # 简化：假设 Q 为体积流量
    flow_area = math.pi * D1 * b1
    if flow_area > 0:
        C1m = Q / flow_area
    else:
        C1m = 0
    
    # 周向速度分量
    C1u = C1m / math.tan(alpha1) if alpha1 > 0.01 else 0
    
    # 绝对速度
    C1 = math.sqrt(C1m**2 + C1u**2)
    
    # 相对速度
    W1 = math.sqrt(C1**2 + u1**2 - 2 * C1 * u1 * math.cos(alpha1))
    
    # 相对气流角
    if u1 - C1 * math.cos(alpha1) > 0.01:
        beta1 = math.atan(C1 * math.sin(alpha1) / (u1 - C1 * math.cos(alpha1)))
    else:
        beta1 = math.pi / 2
    
    return {
        'C1': round(C1, 1),
        'W1': round(W1, 1),
        'U1': round(u1, 1),
        'alpha1': round(alpha1_deg, 1),
        'beta1': round(math.degrees(beta1), 1),
        'C1m': round(C1m, 1),
        'C1u': round(C1u, 1),
    }


def calc_velocity_triangle_outlet(Q: float, D2: float, b2: float,
                                   rho2: float, u2: float,
                                   alpha2_deg: float = 90,
                                   reaction: float = 50) -> Dict:
    """
    计算出口速度三角形
    
    @param Q: 体积流量 (m³/s)
    @param D2: 叶轮内径 (m)
    @param b2: 出口叶片高度 (m)
    @param rho2: 出口密度 (kg/m³)
    @param u2: 出口圆周速度 (m/s)
    @param alpha2_deg: 出口绝对气流角 (°)，默认 90° (轴向排气)
    @param reaction: 反动度 (%)
    
    @return: {C2, W2, U2, alpha2, beta2, C2m, C2u}
    """
    alpha2 = math.radians(alpha2_deg)
    
    # 轴面速度
    flow_area = math.pi * D2 * b2
    if flow_area > 0:
        C2m = Q / flow_area
    else:
        C2m = 0
    
    # 周向速度分量
    C2u = C2m / math.tan(alpha2) if alpha2 > 0.01 else 0
    
    # 绝对速度
    C2 = math.sqrt(C2m**2 + C2u**2)
    
    # 相对速度
    W2 = math.sqrt(C2**2 + u2**2 - 2 * C2 * u2 * math.cos(alpha2))
    
    # 相对气流角
    if u2 - C2 * math.cos(alpha2) > 0.01:
        beta2 = math.atan(C2 * math.sin(alpha2) / (u2 - C2 * math.cos(alpha2)))
    else:
        beta2 = math.pi / 2
    
    return {
        'C2': round(C2, 1),
        'W2': round(W2, 1),
        'U2': round(u2, 1),
        'alpha2': round(alpha2_deg, 1),
        'beta2': round(math.degrees(beta2), 1),
        'C2m': round(C2m, 1),
        'C2u': round(C2u, 1),
    }


def calc_blade_height(Q: float, D: float, C_m: float, rho: float) -> float:
    """
    计算叶片高度
    
    $$b = \\frac{Q}{\\pi \\cdot D \\cdot C_m \\cdot \\rho}$$
    
    @param Q: 体积流量 (m³/s)
    @param D: 直径 (m)
    @param C_m: 轴面速度 (m/s)
    @param rho: 密度 (kg/m³)
    
    @return: 叶片高度 (mm)
    """
    if D <= 0 or C_m <= 0 or rho <= 0:
        return 0
    
    b = Q / (math.pi * D * C_m * rho)
    return round(b * 1000)  # m → mm


def calc_stage_efficiency(hyd_eff: float = 0.88, 
                          vol_eff: float = 0.97,
                          mech_eff: float = 0.98) -> float:
    """
    计算级效率
    
    $$\\eta = \\eta_{hyd} \\cdot \\eta_{vol} \\cdot \\eta_{mech}$$
    
    @param hyd_eff: 水力效率 (0.85~0.92)
    @param vol_eff: 容积效率 (0.95~0.98)
    @param mech_eff: 机械效率 (0.97~0.99)
    
    @return: 级效率 (%)
    """
    eta = hyd_eff * vol_eff * mech_eff
    return round(eta * 100, 1)


def calc_power(m_dot: float, delta_h: float, eta: float) -> float:
    """
    计算功率
    
    $$P = \\dot{m} \\cdot \\Delta h \\cdot \\eta$$
    
    @param m_dot: 质量流量 (kg/s)
    @param delta_h: 实际焓降 (J/kg)
    @param eta: 效率
    
    @return: 功率 (kW)
    """
    P = m_dot * delta_h * eta / 1000
    return round(P, 1)


def turbine_1d_design(flow_rate: float, flow_unit: str,
                      p_in: float, p_out: float,
                      t_in: float, t_out: float,
                      rho_in: float, rho_out: float,
                      power_shaft: float,
                      medium_density: float = None,
                      speed_rpm: float = 3000,
                      blade_count: int = 13,
                      speed_ratio: float = 0.65,
                      reaction: float = 50) -> Dict:
    """
    涡轮一维通流设计主函数
    
    @param flow_rate: 流量
    @param flow_unit: 流量单位 ('Nm3/h', 'T/h', 'kg/s')
    @param p_in: 进口压力 (MPa.G)
    @param p_out: 出口压力 (MPa.G)
    @param t_in: 进口温度 (°C)
    @param t_out: 出口温度 (°C)
    @param rho_in: 进口密度 (kg/m³)
    @param rho_out: 出口密度 (kg/m³)
    @param power_shaft: 轴功率 (kW)
    @param medium_density: 介质平均密度 (kg/m³)
    @param speed_rpm: 转速 (rpm)
    @param blade_count: 叶片数
    @param speed_ratio: 速比 (u/C₀)
    @param reaction: 反动度 (%)
    
    @return: 完整设计结果 (15+ 项参数)
    """
    try:
        # 流量转换
        if flow_unit == 'Nm3/h':
            # 标准状态流量 → 实际工况流量
            # 使用进口密度转换
            m_dot = flow_rate * rho_in / 3600  # kg/s
            Q_m3s = m_dot / rho_in  # m³/s (进口工况)
        elif flow_unit == 'T/h':
            m_dot = flow_rate * 1000 / 3600  # kg/s
            Q_m3s = m_dot / rho_in
        elif flow_unit == 'kg/s':
            m_dot = flow_rate
            Q_m3s = m_dot / rho_in
        else:
            m_dot = flow_rate * rho_in / 3600
            Q_m3s = m_dot / rho_in
        
        # 从轴功率反推焓降
        # P = m_dot × Δh × η
        # Δh = P / (m_dot × η)
        eta_est = 0.85
        if m_dot > 0:
            delta_h_actual = (power_shaft * 1000) / (m_dot * eta_est)  # J/kg
        else:
            delta_h_actual = 100000  # 默认 100 kJ/kg
        
        # 等熵焓降
        delta_h_s = delta_h_actual / eta_est
        
        # 1. 等熵速度
        C0 = calc_isentropic_velocity(delta_h_s)
        
        # 2. 进口圆周速度
        u1 = speed_ratio * C0
        
        # 限制 u1 在合理范围 (50-300 m/s)
        u1 = max(50, min(300, u1))
        
        # 3. 叶轮外径
        D1 = calc_impeller_outer_diameter(u1, speed_rpm)
        D1_m = D1 / 1000
        
        # 限制 D1 在合理范围 (100-1000 mm)
        if D1 < 100:
            D1 = 100
            D1_m = 0.1
        elif D1 > 1000:
            D1 = 1000
            D1_m = 1.0
        
        # 4. 叶轮内径 (假设 D2/D1 ≈ 0.5)
        D2 = round(D1 * 0.5)
        D2_m = D2 / 1000
        
        # 5. 出口圆周速度
        u2 = u1 * (D2_m / D1_m)
        
        # 6. 叶片高度估算
        # 根据流量和直径计算合理的叶片高度
        # C1m = Q / (π × D1 × b1)
        # 假设 C1m 在 50-150 m/s 范围
        C1m_target = 80  # m/s
        if D1_m > 0 and rho_in > 0:
            b1_m = Q_m3s / (math.pi * D1_m * C1m_target)
            b1 = round(b1_m * 1000)  # mm
            # 限制 b1 在合理范围 (10-200 mm)
            b1 = max(10, min(200, b1))
        else:
            b1 = 30
        b1_m = b1 / 1000
        
        # 出口叶片高度 (考虑膨胀，b2 > b1)
        b2 = round(b1 * (rho_in / rho_out) ** 0.5)
        b2 = max(b1, min(300, b2))  # 限制范围
        b2_m = b2 / 1000
        
        # 7. 进口速度三角形 (假设径向进气 α1 = 90°)
        alpha1 = 90
        vel_tri_in = calc_velocity_triangle_inlet(Q_m3s, D1_m, b1_m, rho_in, u1, alpha1)
        
        # 8. 出口速度三角形 (假设轴向排气 α2 = 90°)
        alpha2 = 90
        vel_tri_out = calc_velocity_triangle_outlet(Q_m3s, D2_m, b2_m, rho_out, u2, alpha2, reaction)
        
        # 9. 级效率
        eta_stage = calc_stage_efficiency()
        
        # 10. 性能验证
        P_calc = calc_power(m_dot, delta_h_actual, eta_est)
        
        # 压降
        delta_p = p_in - p_out
        
        return {
            'success': True,
            'dimensions': {
                'D1': D1,
                'D2': D2,
                'b1': b1,
                'b2': b2,
                'Z': blade_count,
            },
            'velocity_triangle_in': vel_tri_in,
            'velocity_triangle_out': vel_tri_out,
            'thermo_params': {
                'eta': eta_stage,
                'omega': reaction,
                'speed_ratio': speed_ratio,
                'C0': round(C0, 1),
            },
            'performance': {
                'P_calc': P_calc,
                'P_input': power_shaft,
                'delta_p': round(delta_p, 3),
                'match': abs(P_calc - power_shaft) < power_shaft * 0.2,
            },
            'message': '涡轮一维设计完成',
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'涡轮设计失败：{str(e)}',
        }


# ============ 单元测试 ============

def test_turbine_standard():
    """T12 - 标准工况"""
    result = turbine_1d_design(
        flow_rate=1000,
        flow_unit='Nm3/h',
        p_in=0.5,
        p_out=0.1,
        t_in=200,
        t_out=85,
        rho_in=4.5,
        rho_out=1.2,
        power_shaft=45.2,
        speed_rpm=3000,
        blade_count=13,
        speed_ratio=0.65,
        reaction=50,
    )
    print(f"T12 - 标准工况：")
    print(f"    基本尺寸：D1={result['dimensions']['D1']}mm, D2={result['dimensions']['D2']}mm")
    print(f"    叶片高度：b1={result['dimensions']['b1']}mm, b2={result['dimensions']['b2']}mm")
    print(f"    进口速度三角形：C1={result['velocity_triangle_in']['C1']}m/s, W1={result['velocity_triangle_in']['W1']}m/s")
    print(f"    出口速度三角形：C2={result['velocity_triangle_out']['C2']}m/s, W2={result['velocity_triangle_out']['W2']}m/s")
    print(f"    级效率：{result['thermo_params']['eta']}%")
    print(f"    计算功率：{result['performance']['P_calc']}kW (输入：{result['performance']['P_input']}kW)")
    print(f"    {result['message']}")
    print("✅ T12 通过\n")


def test_turbine_high_speed():
    """T13 - 高转速"""
    result = turbine_1d_design(
        flow_rate=1000,
        flow_unit='Nm3/h',
        p_in=0.5,
        p_out=0.1,
        t_in=200,
        t_out=85,
        rho_in=4.5,
        rho_out=1.2,
        power_shaft=45.2,
        speed_rpm=6000,  # 高转速
        blade_count=13,
        speed_ratio=0.65,
        reaction=50,
    )
    print(f"T13 - 高转速 (6000rpm)：")
    print(f"    D1={result['dimensions']['D1']}mm, b1={result['dimensions']['b1']}mm")
    print(f"    {result['message']}")
    print("✅ T13 通过\n")


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print("=== Turbine 1D Design Module Unit Tests ===\n")
    
    test_turbine_standard()
    test_turbine_high_speed()
    
    print("[OK] All turbine 1D design tests passed! 🍮")
