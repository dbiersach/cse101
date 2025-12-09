# bjt_amplification.py
# Measure BJT voltage over cutoff, active, and saturation
# regions when configured as a Common-Emitter amplifier

# Uses (1) PN2222A NPN BJT
# Uses (2) 1K Ohm Resistors
# Uses (1) MCP4725 DAC
# Uses (1) ADS1115 ADC

from pathlib import Path

import adafruit_ads1x15.ads1115 as ads
import adafruit_mcp4725
import board
import busio
import matplotlib.pyplot as plt
import numpy as np
from adafruit_ads1x15.analog_in import AnalogIn
from tqdm import tqdm

# Initialize I2C bus
i2c_bus = busio.I2C(board.SCL0, board.SDA0)

# Configure MCP4725 DAC and set output voltage LOW
dac = adafruit_mcp4725.MCP4725(i2c_bus)
dac.raw_value = 0

# Configure ADS1115 ADC in differential mode (P0+, P1-)
adc = ads.ADS1115(i2c_bus)
adc_chan = AnalogIn(adc, ads.P0, ads.P1)

# Set number of samples
n = 450
print(f"Reading {n} samples...")
volts_be = np.zeros(n, dtype=float)
volts_ce = np.zeros(n, dtype=float)

# Read volts from ADC
for i in tqdm(range(n)):
    # Set DAC output voltage which is the volts between
    # the BJT base and emitter as emitter is at GND
    dac.raw_value = 572 + i
    volts_be[i] = dac.raw_value / 4095 * 3.3
    # Read the voltage drop across the collector's resistor
    volts_ce[i] = adc_chan.voltage

# Turn off DAC voltage to circuit
dac.raw_value = 0

# Find points of within the active region of the BJT
i1 = np.where(volts_be > 0.6)[0][0]
i2 = np.where(volts_be > 0.7)[0][0]
vb0 = volts_be[0]
vb1, vc1 = volts_be[i1], volts_ce[i1]
vb2, vc2 = volts_be[i2], volts_ce[i2]

# Plot samples
plt.figure(Path(__file__).name)
plt.gca().set_facecolor("black")
plt.plot(volts_be, volts_ce, color="yellow", linewidth=2)
plt.title("PN2222A (NPN) BJT Amplification")
plt.xlabel("Base-Emitter Voltage (V)")
plt.ylabel("Collector-Emitter Voltage (V)")
plt.grid(which="both", color="grey", linestyle="dotted", alpha=0.5)
plt.vlines(vb1, 0, vc1, color="g", linestyle="--")
plt.hlines(vc1, vb0, vb1, color="g", ls="--")
plt.vlines(vb2, 0, vc2, color="r", linestyle="--")
plt.hlines(vc2, vb0, vb2, color="r", ls="--")
plt.show()
