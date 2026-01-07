# band_gap.py
# Compare forward voltage of RED vs BLUE LEDs

# Uses (1) MCP4725 DAC
# Uses (1) PN2222A BJT
# Uses (1) 330 Ohm Resistor
# Uses (1) 10K Ohm Resistor
# Uses (1) Blue LED

import time

import adafruit_mcp4725
import board
import busio
from tqdm import tqdm

# Initialize I2C bus
i2c_bus = busio.I2C(board.SCL0, board.SDA0)

# Configure MCP4725 DAC
dac = adafruit_mcp4725.MCP4725(i2c_bus)

required_voltage = 1.97

# Set DAC output voltage
# The NPN BJT emitter follower causes a 0.6V drop from 3.3V
dac.normalized_value = required_voltage / (3.3 - 0.6)
print(f"DAC output set to {required_voltage:.2f} V")

# Wait five seconds
for _ in tqdm(range(100)):
    time.sleep(0.05)

# Turn off DAC voltage to circuit
dac.raw_value = 0
print("DAC OFF (0.0 V output)")
