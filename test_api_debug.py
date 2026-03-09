import requests
import json

BASE_URL = "http://localhost:8000"

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

print("Sending request...")
r = requests.post(f"{BASE_URL}/api/calculate/mode1", json=payload)
print(f"Status: {r.status_code}")
print(f"Headers: {r.headers}")
print(f"Content: {r.text[:2000]}")
