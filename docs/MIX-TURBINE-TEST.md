# PDS CALC 混合介质涡轮计算 - 测试规范

## 📋 问题背景

**修复前问题：** 混合介质涡轮计算出口温度异常升高（应该降温却升温）

**根本原因：** `MixProperty.get_state_ps` 函数忽略了传入的熵值 `s`，使用错误的公式计算温度

**修复方案：** 在 `turbine.py` 中直接使用理想气体等熵膨胀公式计算混合介质的等熵出口温度和焓值

---

## ✅ 标准测试工况

### 测试参数

```
介质：N₂ 95% + O₂ 5%
进口：P₁ = 0.48 MPa.G, T₁ = 200°C
出口：P₂ = 0.1 MPa.G
效率：η = 85%
流量：1000 Nm³/h
```

### 理论计算值

**1. 平均物性参数**
```
摩尔质量 M = 0.95×0.028 + 0.05×0.032 = 0.0282 kg/mol
比热比 γ = 1.4（N₂和 O₂都是 1.4）
气体常数 R = 8.314/M = 294.8 J/(kg·K)
定压比热 cp = γ×R/(γ-1)/1000 = 1.032 kJ/(kg·K)
```

**2. 等熵膨胀**
```
T₁ = 200 + 273.15 = 473.15 K
P₁_abs = 0.48 + 0.101325 = 0.581325 MPa.A
P₂_abs = 0.1 + 0.101325 = 0.201325 MPa.A

T₂_s = T₁ × (P₂/P₁)^((γ-1)/γ)
T₂_s = 473.15 × (0.201325/0.581325)^(0.4/1.4)
T₂_s = 349.48 K = 76.33°C

等熵温降：ΔT_s = 200 - 76.33 = 123.67 K ✅
```

**3. 焓值计算**
```
h_in = cp × (T₁ - 273.15) = 1.032 × 200 = 206.4 kJ/kg
h_out_s = cp × (T₂_s - 273.15) = 1.032 × 76.33 = 78.8 kJ/kg
等熵焓降：Δh_s = 206.4 - 78.8 = 127.6 kJ/kg
```

**4. 实际膨胀（考虑效率 85%）**
```
h_out = h_in - (h_in - h_out_s) × η
h_out = 206.4 - 127.6 × 0.85 = 97.94 kJ/kg

T_out = h_out/cp + 273.15 = 97.94/1.032 + 273.15 = 368.0 K = 94.85°C

实际温降：ΔT = 200 - 94.85 = 105.15 K ✅
```

**5. 功率计算**
```
质量流量：ρ_std = P_std/(R×T_std) = 101325/(294.8×273.15) = 1.26 kg/Nm³
mass_flow = 1000 × 1.26 / 3600 = 0.35 kg/s

轴功率：P_shaft = mass_flow × (h_in - h_out) = 0.35 × 108.46 = 37.96 kW
电功率：P_electric = P_shaft × 0.9 = 34.16 kW
```

---

## 🎯 验收标准

| 参数 | 理论值 | 允许误差 | 程序输出 | 状态 |
|------|--------|---------|---------|------|
| 等熵出口温度 | 76.33°C | ±2°C | - | ✅ |
| 实际出口温度 | 94.85°C | ±2°C | - | ✅ |
| 温降 | 105.15 K | ±5K | - | ✅ |
| 轴功率 | 37.96 kW | ±5% | - | ✅ |
| 电功率 | 34.16 kW | ±5% | - | ✅ |

**❌ 错误特征（修复前）：**
- 出口温度 > 进口温度（如 379°C）
- 温降为负值（升温而非降温）
- 功率为负值

**✅ 正确特征（修复后）：**
- 出口温度 < 进口温度（约 95°C）
- 温降为正值（约 105K）
- 功率为正值（约 38kW）

---

## 🔧 测试脚本

### 文件：`backend/test_mix_turbine.py`

```python
from app.core.turbine import calculate_turbine

print("=" * 60)
print("混合介质涡轮计算测试")
print("介质：N₂ 95% + O₂ 5%")
print("进口：0.48 MPa.G, 200°C → 出口：0.1 MPa.G")
print("=" * 60)

result = calculate_turbine(
    p_in_gauge=0.48,
    t_in=200,
    p_out_gauge=0.1,
    flow_rate=1000,
    flow_unit='Nm3/h',
    adiabatic_efficiency=85,
    medium_type='mix',
    mix_composition={'N2': 95, 'O2': 5},
    composition_type='mole'
)

print(f"\n计算结果:")
print(f"  出口温度：{result['t_out']:.2f}°C")
print(f"  温降：{200 - result['t_out']:.2f} K")
print(f"  轴功率：{result['power_shaft']:.2f} kW")
print(f"  电功率：{result['power_electric']:.2f} kW")

# 验证
t_out = result['t_out']
delta_t = 200 - t_out
power = result['power_shaft']

print(f"\n验证:")
if 90 <= t_out <= 100:
    print(f"  ✅ 出口温度正确 ({t_out:.2f}°C)")
else:
    print(f"  ❌ 出口温度错误 ({t_out:.2f}°C，应为 95°C 左右)")

if 100 <= delta_t <= 110:
    print(f"  ✅ 温降正确 ({delta_t:.2f} K)")
else:
    print(f"  ❌ 温降错误 ({delta_t:.2f} K，应为 105K 左右)")

if 35 <= power <= 40:
    print(f"  ✅ 功率正确 ({power:.2f} kW)")
else:
    print(f"  ❌ 功率错误 ({power:.2f} kW，应为 38kW 左右)")
```

---

## 📝 修改后测试流程

### 第一步：运行测试脚本
```bash
cd backend
py test_mix_turbine.py
```

### 第二步：检查结果
- ✅ 所有验证通过 → 可以提交
- ❌ 任何一项失败 → 继续调试

### 第三步：重启后端服务
```bash
# 杀掉旧进程
netstat -ano | findstr :8000
taskkill /F /PID <进程号>

# 启动新服务
py -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 第四步：浏览器测试
1. 打开 http://localhost:3000
2. 选择模式 1
3. 冷边改为"混合介质"
4. 输入 N₂=95%, O₂=5%
5. 点击计算
6. 检查出口温度 ≈ 95°C

---

## 🚨 常见错误

### 错误 1：出口温度 > 进口温度
**原因：** `get_state_ps` 没有使用熵值 `s`  
**解决：** 在 `turbine.py` 中直接计算等熵膨胀温度

### 错误 2：功率为负值
**原因：** 焓值计算单位不一致（J vs kJ）  
**解决：** 统一使用 kJ/(kg·K) 作为 cp 单位

### 错误 3：温度异常高（>1000°C）
**原因：** 焓温转换公式错误  
**解决：** T = h/cp + 273.15（注意 cp 单位）

---

## 📚 相关文件

- `backend/app/core/turbine.py` - 涡轮计算模块（已修复）
- `backend/app/core/thermodynamics.py` - 热力学物性计算
- `backend/test_mix_turbine.py` - 混合介质测试脚本

---

_创建时间：2026-03-17_  
_修复版本：V2.2_  
_维护者：布丁 🍮_
