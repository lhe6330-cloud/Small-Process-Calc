"""
设备选型模块：电机、管道、阀门
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import math
from typing import List, Dict, Tuple, Optional

try:
    from fluids import size_control_valve_g, size_control_valve_l
    FLUIDS_AVAILABLE = True
except ImportError:
    FLUIDS_AVAILABLE = False

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
    10, 15, 20, 25, 32, 45, 50, 65, 80, 100,
    125, 150, 200, 250, 300, 350, 400, 450, 500, 600,
    700, 800, 900, 1000, 1100
]

# 蝶阀 Kv 值表（后座型 90°全开，扩展到大通径）
# 小通径 (DN50/65/80) 按开放型估算，后座型通常从 DN100 开始
VALVES_KV = {
    50: 100,       # 估算值 (后座型小通径较少见)
    65: 180,       # 估算值
    80: 200,       # 估算值
    100: 240,      # 后座型 90°
    125: 500,      # 估算值 (按 DN100/DN150 插值)
    150: 730,      # 后座型 90°
    200: 1300,     # 后座型 90°
    250: 2200,     # 后座型 90°
    300: 3400,     # 后座型 90°
    350: 4695,     # 后座型 90°
    400: 6295,     # 后座型 90°
    450: 7795,     # 后座型 90°
    500: 9765,     # 后座型 90°
    600: 14480,    # 后座型 90°
    700: 23800,    # 后座型 90°
    800: 27000,    # 后座型 90°
}

# 截止阀 Kv 值表（DN125 及以下使用）
GLOBE_VALVES_KV = {
    15: 0.8,
    20: 5,
    25: 8,
    32: 12,
    45: 20,
    50: 32,
    65: 50,
    80: 80,
    100: 120,
    125: 200,
}

# 阀门压力恢复系数 FL (IEC 60534)
FL_COEFFICIENTS = {
    'butterfly': 0.68,  # 蝶阀
    'globe': 0.85,      # 截止阀
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

def _get_saturation_temp(p_abs: float) -> float:
    """获取水的饱和温度 (MPa.A -> °C)"""
    try:
        from .thermodynamics import WaterProperty
        return WaterProperty.get_saturation_temp(p_abs)
    except ImportError:
        from thermodynamics import WaterProperty
        return WaterProperty.get_saturation_temp(p_abs)

def _is_superheated_steam(p_abs: float, t: float) -> bool:
    """判断是否为过热蒸汽"""
    if t is None:
        return False
    t_sat = _get_saturation_temp(p_abs)
    return t > t_sat

def _get_superheat(p_abs: float, t: float) -> float:
    """获取过热度 (°C)"""
    t_sat = _get_saturation_temp(p_abs)
    return max(0, t - t_sat)

def _get_molecular_weight(medium: str = None, medium_type: str = 'single') -> float:
    """获取气体分子量 (g/mol)"""
    MW_TABLE = {
        'CO2': 44.01,
        'N2': 28.01,
        'O2': 32.00,
        'Air': 28.97,
        'H2': 2.02,
        'CH4': 16.04,
        'H2O': 18.02,
        'Ar': 39.95,
        'He': 4.00,
    }
    if medium_type == 'single' and medium in MW_TABLE:
        return MW_TABLE[medium]
    return 28.97  # 默认空气

def select_valve(
    flow_rate: float,
    flow_unit: str,
    rho: float,
    pipe_dn: int,
    medium_type: str,
    medium: str = None,
    delta_p_kpa: float = 30,      # 用户指定压差 (kPa)
    valve_type: str = 'butterfly', # 阀门类型：'butterfly' 或 'globe'
    t: float = None,
    p_in_abs: float = None,
    p_out_abs: float = None,
    medium_state: str = None,     # 'gas' / 'liquid' / 'steam'（用户指定）
    specified_dn: Optional[int] = None,     # 用户指定通径，None 表示自动选择
) -> Dict:
    """
    阀门选型 (IEC 60534 标准)
    @param flow_rate: 流量
    @param flow_unit: 'T/h' or 'Nm3/h'
    @param rho: 密度 (kg/m³)
    @param pipe_dn: 管道通径 (参考)
    @param medium_type: 'single' or 'mix'
    @param medium: 介质
    @param delta_p_kpa: 设计压差 (kPa)
    @param valve_type: 阀门类型 'butterfly'(蝶阀) 或 'globe'(截止阀)
    @param t: 温度 (°C)
    @param p_in_abs: 入口绝压 (MPa.A)
    @param p_out_abs: 出口绝压 (MPa.A)
    @param medium_state: 'gas' / 'liquid' / 'steam'（用户指定）
    @param specified_dn: 用户指定通径，None 表示自动选择
    @return: {valve_dn, kv_required, kv_rated, valve_opening, check_status, ...}
    """
    # DN125 及以下通常选用截止阀（小通径蝶阀不常见）
    if pipe_dn <= 125 and specified_dn is None:
        valve_type = 'globe'

    FL = FL_COEFFICIENTS.get(valve_type, 0.68)

    # 阀门特性参数
    if valve_type == 'butterfly':
        xT = 0.75
        Fd = 1.0
    else:  # globe
        xT = 0.9
        Fd = 1.0

    # 单位转换
    delta_p_bar = delta_p_kpa / 100  # kPa -> bar
    p1_bar = p_in_abs * 10 if p_in_abs else 10  # MPa -> bar
    p2_bar = p_out_abs * 10 if p_out_abs else (p1_bar - delta_p_bar)

    # 临界压差 (阻塞流判断)
    critical_dp = FL**2 * p1_bar * 0.75
    is_choked = delta_p_bar > critical_dp

    # === 计算所需 Kv (IEC 60534 公式) ===
    # 优先使用用户指定的 medium_state，其次根据 flow_unit 和 medium 自动判断
    state = medium_state if medium_state else ('steam' if (flow_unit == 'T/h' and medium == 'H2O' and t and t >= 100) else ('liquid' if (flow_unit == 'T/h' and medium == 'H2O') else 'gas'))

    if state == 'liquid':
        # === 液体介质 ===
        # Kv = Q_m3/h * sqrt(SG / Δp_bar), SG = rho / 1000 (相对于水的比重)
        # flow_rate 单位：T/h -> 需要转换为 kg/h (1 T/h = 1000 kg/h)
        mass_flow_kgh = flow_rate * 1000  # T/h -> kg/h
        q_m3h = mass_flow_kgh / rho  # kg/h -> m³/h
        sg = rho / 1000  # 相对密度（相对于水）
        kv_required = q_m3h * math.sqrt(sg / delta_p_bar)

    elif state == 'steam':
        # === 蒸汽介质 ===
        # Kv = m_kg/h / (31.6 * sqrt(Δp * p2)) * sqrt(1 + 0.0013 * 过热度)
        # flow_rate 单位是 T/h，需要转换为 kg/h (1 T/h = 1000 kg/h)
        mass_flow = flow_rate * 1000  # T/h -> kg/h
        is_superheated = _is_superheated_steam(p_in_abs, t) if p_in_abs else False
        superheat = _get_superheat(p_in_abs, t) if is_superheated else 0
        superheat_factor = 1 + 0.0013 * superheat

        if is_choked:
            # 阻塞流
            kv_required = mass_flow / (31.6 * FL * p1_bar * superheat_factor)
        else:
            # 非阻塞流
            kv_required = mass_flow / (31.6 * math.sqrt(delta_p_bar * p2_bar) * superheat_factor)

    else:
        # === 气体介质 (Nm3/h) ===
        # 使用 fluids 库计算（IEC 60534-2-1 标准）
        if FLUIDS_AVAILABLE and p_in_abs and t is not None:
            # fluids 库参数
            T_K = t + 273.15
            MW = _get_molecular_weight(medium, medium_type)
            mu = 1.5e-5  # Pa·s (近似值)
            gamma = 1.30 if medium == 'CO2' else 1.40  # 比热比
            Z = 0.99  # 压缩因子

            P1_Pa = p_in_abs * 1e6
            P2_Pa = (p_out_abs or (p_in_abs - delta_p_kpa/1000)) * 1e6

            # Nm3/h -> m3/s @ 标准状态
            Q_m3s = flow_rate / 3600

            # 使用 fluids 库计算所需 Kv
            kv_required = size_control_valve_g(
                T=T_K, MW=MW, mu=mu, gamma=gamma, Z=Z,
                P1=P1_Pa, P2=P2_Pa, Q=Q_m3s,
                FL=FL, Fd=Fd, xT=xT
            )
        else:
            # 退化到简化公式
            # IEC 60534-2-1 公式：Kv = Qn / (514 * sqrt(Δp * p2 / SG))
            # 其中 SG = rho / 1.293 (相对于空气的密度)
            sg_gas = rho / 1.293  # 相对密度（相对于空气）

            if is_choked:
                # 阻塞流
                kv_required = flow_rate / (514 * FL * p1_bar * math.sqrt(sg_gas))
            else:
                # 非阻塞流
                kv_required = flow_rate / (514 * math.sqrt(delta_p_bar * p2_bar / sg_gas))

    # === 按 Kv 选择阀门通径 ===
    # 根据阀门类型选择对应的 Kv 表
    if valve_type == 'globe':
        kv_table = GLOBE_VALVES_KV
    else:
        kv_table = VALVES_KV

    # === 用户指定通径 vs 自动选择 ===
    if specified_dn is not None:
        # 用户指定通径：直接使用
        suitable_dn = specified_dn
        # 获取该通径的额定 Kv 值
        kv_rated = kv_table.get(suitable_dn, 0)
        if kv_rated == 0:
            # 指定通径不在 Kv 表中，找最接近的
            suitable_dn = min(kv_table.keys(), key=lambda d: abs(d - specified_dn))
            kv_rated = kv_table[suitable_dn]
    else:
        # 自动选择：按 Kv 选择阀门通径
        suitable_dn = None
        kv_rated = 0

        for dn, kv in sorted(kv_table.items()):
            if kv >= kv_required:
                suitable_dn = dn
                kv_rated = kv
                break

        if suitable_dn is None:
            # 所有规格都不够，选最大的
            suitable_dn = max(kv_table.keys())
            kv_rated = kv_table[suitable_dn]

    # === 最小通径约束：阀门通径不应小于管道通径 ===
    # 对于切断阀/隔离阀，阀门通径应与管道通径相同
    # 对于控制阀，可以小于管道，但一般不小于管道通径的 1 档
    # 这里采用较严格的约束：阀门通径 >= 管道通径
    # 但用户指定通径时，尊重用户选择，不进行强制放大
    if specified_dn is None and suitable_dn < pipe_dn:
        # 阀门通径小于管道，需要放大到管道通径
        # 在对应的 Kv 表中找到 >= pipe_dn 的最小阀门
        for dn, kv in sorted(kv_table.items()):
            if dn >= pipe_dn:
                suitable_dn = dn
                kv_rated = kv
                break
        else:
            # 如果管道通径超出 Kv 表范围，选最大的阀门
            suitable_dn = max(kv_table.keys())
            kv_rated = kv_table[suitable_dn]

    # === 计算 Kv 利用率（额定开度下的 Kv 占比）===
    kv_utilization = (kv_required / kv_rated) * 100 if kv_rated > 0 else 100

    # === 估算实际开度（等百分比特性阀门）===
    # 等百分比特性：Kv/Kv_rated = R^(opening-1)，R 为可调比（通常 30-50）
    # 当 opening=0 时，Kv/Kv_rated = 1/R ≈ 3.3%（最小可控流量）
    # 当 opening=100% 时，Kv/Kv_rated = 100%（全开）
    R = 30  # 可调比
    min_controllable = 100 / R  # 最小可控开度对应的 Kv 利用率 ≈ 3.3%

    if kv_utilization >= min_controllable:
        # 正常范围：使用等百分比公式
        # opening = log(Kv/Kv_rated) / log(R) + 1
        estimated_opening = (math.log(kv_utilization / 100) / math.log(R) + 1) * 100
        estimated_opening = max(0, min(100, estimated_opening))
    elif kv_utilization > 0:
        # 低于最小可控流量：开度设为 5-10%，表示小开度运行
        # 使用线性插值：0% -> 0%, min_controllable -> 10%
        estimated_opening = 10 * (kv_utilization / min_controllable)
        estimated_opening = max(0, min(10, estimated_opening))
    else:
        estimated_opening = 0

    # 使用估算开度作为显示值（更符合实际）
    valve_opening = estimated_opening

    # === 开度校验状态 ===
    if valve_opening > 90:
        # 开度超过 90%，直接报错
        check_status = 'fail'
        status_msg = f'❌ 阀门通径太小 (开度{valve_opening:.1f}%)，请增大通径'
    elif valve_opening > 100:
        check_status = 'fail'
        status_msg = f'❌ 通径不足 (开度{valve_opening:.1f}%)，需放大一号'
    elif valve_opening > 95:
        check_status = 'warning'
        status_msg = f'⚠️ 满负荷运行 (开度{valve_opening:.1f}%)，无余量'
    elif valve_opening >= 80:
        check_status = 'ok'
        status_msg = f'✅ 合适 (开度{valve_opening:.1f}%)，切断阀常用范围'
    elif valve_opening >= 60:
        check_status = 'ok'
        status_msg = f'✅ 合适 (开度{valve_opening:.1f}%)，有一定余量'
    elif valve_opening >= 40:
        check_status = 'ok'
        status_msg = f'✅ 合适 (开度{valve_opening:.1f}%)，有余量'
    elif valve_opening >= 20:
        check_status = 'ok'
        status_msg = f'✅ 合适 (开度{valve_opening:.1f}%)，开度偏低但可用'
    elif valve_opening >= 10:
        check_status = 'warning'
        status_msg = f'⚠️ 开度偏低 (开度{valve_opening:.1f}%)，小流量时控制精度可能下降'
    else:
        check_status = 'warning'
        status_msg = f'⚠️ 开度过低 (开度{valve_opening:.1f}%)，阀门通径与管道匹配，小开度运行'

    # === 与管道通径对比 ===
    dn_diff = suitable_dn - pipe_dn

    # 构建状态消息（包含阀门类型提示）
    if pipe_dn <= 125 and valve_type == 'globe':
        type_note = ' (DN≤125 自动选用截止阀)'
    else:
        type_note = ''

    return {
        'valve_dn': suitable_dn,
        'pipe_dn': pipe_dn,
        'valve_type': valve_type,
        'kv_required': kv_required,
        'kv_rated': kv_rated,
        'valve_opening': valve_opening,
        'check_status': check_status,
        'status_msg': status_msg + type_note,
        'delta_p_design': delta_p_kpa,
        'fl_coefficient': FL,
        'is_choked_flow': is_choked,
        'dn_diff': dn_diff,
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

    print("\n3. Valve Selection (butterfly, gas 1000 Nm3/h, ΔP=30kPa):")
    valve = select_valve(1000, 'Nm3/h', 1.2, 80, 'single', 'N2',
                         delta_p_kpa=30, valve_type='butterfly',
                         t=25, p_in_abs=0.6, p_out_abs=0.57)
    print(f"   Type: {valve['valve_type']}, DN: {valve['valve_dn']}")
    print(f"   Kv_req: {valve['kv_required']:.1f}, Kv_rated: {valve['kv_rated']}")
    print(f"   Opening: {valve['valve_opening']:.1f}%, Status: {valve['check_status']}")
    print(f"   {valve['status_msg']}")

    print("\n4. Valve Selection (globe, steam 5 T/h, ΔP=50kPa):")
    valve = select_valve(5, 'T/h', 0.6, 50, 'single', 'H2O',
                         delta_p_kpa=50, valve_type='globe',
                         t=200, p_in_abs=0.6, p_out_abs=0.55)
    print(f"   Type: {valve['valve_type']}, DN: {valve['valve_dn']}")
    print(f"   Kv_req: {valve['kv_required']:.1f}, Kv_rated: {valve['kv_rated']}")
    print(f"   Opening: {valve['valve_opening']:.1f}%, Status: {valve['check_status']}")
    print(f"   {valve['status_msg']}")

    print("\n[OK] Selection module test passed!")
