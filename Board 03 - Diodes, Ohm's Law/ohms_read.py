# ohms_read.py
# Measure current through various resistor

# Uses (1) MCP4725 DAC
# Uses (1) INA219 Current Sensor
# Uses (1) PN2222A BJT
# Uses (1) 330 Ohm and (1) 10K Ohm Resistor
# Uses (1) 47 Ohm, (1) 56 Ohm, and (1) 68 Ohm Resistor

import time
from pathlib import Path

import adafruit_mcp4725
import board
import busio
import numpy as np
from adafruit_ina219 import INA219, ADCResolution, BusVoltageRange, Gain
from tqdm import tqdm

# Initialize I2C bus
i2c_bus = busio.I2C(board.SCL0, board.SDA0)

# Configure MCP4725 DAC and set output voltage LOW
dac = adafruit_mcp4725.MCP4725(i2c_bus)
dac.raw_value = 0

# Configure IN219 current sensor
ina219 = INA219(i2c_bus)
ina219.bus_voltage_range = BusVoltageRange.RANGE_16V
ina219.gain = Gain.DIV_8_320MV
ina219.bus_adc_resolution = ADCResolution.ADCRES_12BIT_128S
ina219.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_128S

# Query the user for the resistor number to be measured
while True:
    try:
        resistor_num = int(input("Resistor # (1, 2, or 3)? "))
        if 1 <= resistor_num <= 3:
            break
        else:
            print("Please enter an integer between 1 and 3 inclusive.")
    except ValueError:
        print("That is not a valid integer. Please try again.")


# Set number of samples
n = 50
print(f"Reading {n} samples...")

# Allocate arrays
volts = np.zeros(n, dtype=float)
amps = np.zeros(n, dtype=float)

# Increase DAC output voltage while reading amps
# through the diode using the INA219 current sensor
for i in tqdm(range(n)):
    # Set DAC output voltage
    # 1125 + (49) * 60 = 4065 (out of a max 4095)
    dac.raw_value = 1125 + i * 60
    # Max voltage at the Emitter of PN2222A BJT is 2.36V
    volts[i] = dac.raw_value / 4095 * 2.36
    time.sleep(0.2)
    # Calculate average amps using 100 samples
    a = 0
    for _ in range(50):
        # Read current flowing through load resistor
        a += ina219.current
        time.sleep(0.01)
    amps[i] = a / 50

# Turn off DAC voltage to circuit
dac.raw_value = 0

# Save samples to a CSV file
samples = np.column_stack((volts, amps))
file_name = f"resistor{resistor_num:n}.csv"
file_path = Path(__file__).parent / file_name
np.savetxt(file_path, samples, fmt="%3.6f", delimiter=",")
print(f'Saved file "{file_name}"')
