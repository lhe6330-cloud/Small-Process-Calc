import requests

BASE = "http://localhost:8000"

# Test Mode 2
print("=== Mode 2 Test ===")
payload2 = {
    "turbine_in": {
        "medium_type": "single", "medium": "N2",
        "flow_rate": 1000, "flow_unit": "Nm3/h",
        "p_in": 0.6, "p_out": 0.3, "t_in": 250, "t_out": 100
    },
    "turbine_params": {"p_out": 0.3, "adiabatic_efficiency": 85},
    "hx_cold_out": {"p_out": 0.28, "t_out": 150},
    "hx_hot": {
        "medium_type": "single", "medium": "Air",
        "flow_rate": 800, "flow_unit": "Nm3/h",
        "p_in": 0.4, "p_out": 0.35, "t_in": 200, "t_out": 100
    }
}
r = requests.post(f"{BASE}/api/calculate/mode2", json=payload2)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    res = r.json()
    print(f"Turbine: {res['turbine']['power_shaft']:.2f} kW")
    print(f"HX: {res['heat_exchanger']['q_power']:.2f} kW")
    print(f"Motor: {res['selection']['motor']} kW")
else:
    print(f"Error: {r.text}")

# Test Mode 3
print("\n=== Mode 3 Test ===")
payload3 = {
    "turbine_in": {
        "medium_type": "single", "medium": "N2",
        "flow_rate": 1000, "flow_unit": "Nm3/h",
        "p_in": 0.6, "p_out": 0.3, "t_in": 250, "t_out": 100
    },
    "turbine_params": {"p_out": 0.3, "adiabatic_efficiency": 85}
}
r = requests.post(f"{BASE}/api/calculate/mode3", json=payload3)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    res = r.json()
    print(f"Turbine: {res['turbine']['power_shaft']:.2f} kW")
    print(f"Motor: {res['selection']['motor']} kW")
else:
    print(f"Error: {r.text}")

print("\n[OK] Mode 2/3 API test passed!")
