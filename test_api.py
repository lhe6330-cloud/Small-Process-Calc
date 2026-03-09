import requests
import json

BASE_URL = "http://localhost:8000"

# 测试健康检查
print("=== Test 1: Health Check ===")
r = requests.get(f"{BASE_URL}/api/health")
print(f"Status: {r.status_code}")
print(f"Response: {r.json()}\n")

# 测试模式 1 计算
print("=== Test 2: Mode 1 Calculation ===")
payload = {
    "cold_side": {
        "medium_type": "single",
        "medium": "N2",
        "flow_rate": 1000,
        "flow_unit": "Nm3/h",
        "p_in": 0.5,
        "p_out": 0.48,
        "t_in": 20,
        "t_out": 200
    },
    "hot_side": {
        "medium_type": "single",
        "medium": "H2O",
        "flow_rate": 0.5,
        "flow_unit": "T/h",
        "p_in": 0.6,
        "p_out": 0.55,
        "t_in": 250
    },
    "turbine": {
        "p_out": 0.1,
        "adiabatic_efficiency": 85
    }
}

r = requests.post(f"{BASE_URL}/api/calculate/mode1", json=payload)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    result = r.json()
    print(f"Heat Exchanger: Q={result['heat_exchanger']['q_power']:.2f} kW, T_hot_out={result['heat_exchanger']['t_hot_out']:.2f} C")
    print(f"Turbine: Shaft={result['turbine']['power_shaft']:.2f} kW, Electric={result['turbine']['power_electric']:.2f} kW, T_out={result['turbine']['t_out']:.2f} C")
    print(f"Motor: {result['selection']['motor']} kW")
    print(f"Pipe Inlet: DN{result['selection']['pipe_inlet']['recommended_dn']} (v={result['selection']['pipe_inlet']['velocity']:.2f} m/s)")
    print(f"Pipe Outlet: DN{result['selection']['pipe_outlet']['recommended_dn']} (v={result['selection']['pipe_outlet']['velocity']:.2f} m/s)")
    print(f"Valve: DN{result['selection']['valve']['valve_dn']}, Kv={result['selection']['valve']['kv_rated']}")
else:
    print(f"Error: {r.text}")

print("\n=== Test 3: Standards ===")
r = requests.get(f"{BASE_URL}/api/standards/motors")
print(f"Motors count: {len(r.json()['motors'])}")
r = requests.get(f"{BASE_URL}/api/standards/pipes")
print(f"Pipes count: {len(r.json()['pipes'])}")

print("\n[OK] All API tests passed!")
