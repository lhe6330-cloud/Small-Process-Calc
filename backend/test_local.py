import sys
sys.path.insert(0, '.')

from app.core.thermodynamics import get_fluid_property
from app.core.turbine import calculate_turbine
from app.core.heat_exchanger import calculate_heat_exchanger
from app.core.selection import select_motor

print("Testing imports... OK")

# Test heat exchanger
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

hx = calculate_heat_exchanger(cold, hot)
print(f"HX: Q={hx['q_power']:.2f} kW")

# Test turbine
t = calculate_turbine(0.48, 200, 0.1, 1000, 'Nm3/h', 85, 'single', 'N2')
print(f"Turbine: P={t['power_shaft']:.2f} kW")

# Test motor
m = select_motor(t['power_shaft'])
print(f"Motor: {m} kW")

print("\nAll local tests passed!")
