# diode_ivcurve.py
# Measure current through PN junction diode

# Uses (1) MCP4725 DAC
# Uses (1) INA219 Current Sensor
# Uses (1) 1N4001 Diode

from pathlib import Path

import adafruit_mcp4725
import board
import busio
import matplotlib.pyplot as plt
import numpy as np
from adafruit_ina219 import INA219, ADCResolution, BusVoltageRange, Gain
from matplotlib.ticker import FormatStrFormatter, MultipleLocator
from tqdm import tqdm

# Initialize I2C bus
i2c = busio.I2C(board.SCL0, board.SDA0)

# Configure MCP4725 DAC and set output voltage LOW
dac = adafruit_mcp4725.MCP4725(i2c)
dac.raw_value = 0

# Configure IN219 current sensor
ina219 = INA219(i2c)
ina219.bus_voltage_range = BusVoltageRange.RANGE_16V
ina219.gain = Gain.DIV_8_320MV
ina219.bus_adc_resolution = ADCResolution.ADCRES_12BIT_128S
ina219.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_128S

# Set number of samples
n = 200
print(f"Reading {n} samples...")

# Allocate arrays
volts = np.zeros(n, dtype=float)
amps = np.zeros(n, dtype=float)

# Increase DAC output voltage while reading amps
# through the diode using the INA219 current sensor
for i in tqdm(range(n)):
    # Set DAC output voltage
    dac.raw_value = i * 8
    volts[i] = dac.raw_value / 4096 * 3.015  # 3.015V max output
    # Calculate average amps using 100 samples
    a = 0
    for _ in range(100):
        # Read current flowing through load resistor
        a += ina219.current
    amps[i] = a / 100

# Turn off DAC voltage to circuit
dac.raw_value = 0

# Plot the graph on the main axes
plt.figure(Path(__file__).name)
plt.gca().set_facecolor("black")
plt.plot(volts, amps, color="yellow", linewidth=2)
plt.title("1N4001 Diode I-V Characteristic Curve")
plt.xlabel("Voltage (V)")
plt.ylabel("Current (mA)")
plt.gca().xaxis.set_major_locator(MultipleLocator(0.1))
plt.gca().xaxis.set_major_formatter(FormatStrFormatter("%.2f"))
plt.gca().yaxis.set_major_locator(MultipleLocator(1.0))
plt.gca().yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
plt.grid(which="both", color="lightgray", linestyle="dotted", alpha=0.5)
plt.show()
