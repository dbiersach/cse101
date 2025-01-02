# code.py for Raspberry Pi Pico 2
# Lab: ohms_law
# Measure current through various resistor

# Uses (1) MCP4725 DAC
# Uses (1) INA219 Current Sensor
# Uses (1) PN2222A BJT
# Uses (1) 330 Ohm and (1) 10K Ohm Resistor
# Uses (1) 47 Ohm, (1) 56 Ohm, and (1) 68 Ohm Resistor

import time

import adafruit_mcp4725
import board
import supervisor
import usb_cdc
from adafruit_ina219 import INA219, ADCResolution, BusVoltageRange, Gain

# Wait until USB console port is ready
while not supervisor.runtime.usb_connected:
    pass
print("Lab: ohms_law")

# Create USB data port
ser = usb_cdc.data

# Initialize I2C bus
i2c = board.STEMMA_I2C()

# Configure MCP4725 DAC and set output voltage LOW
dac = adafruit_mcp4725.MCP4725(i2c)
dac.raw_value = 0

# Configure IN219 current sensor
ina219 = INA219(i2c)
ina219.bus_voltage_range = BusVoltageRange.RANGE_16V
ina219.gain = Gain.DIV_8_320MV
ina219.bus_adc_resolution = ADCResolution.ADCRES_12BIT_128S
ina219.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_128S


def usb_readline():
    return ser.readline().decode("utf-8").strip()


def usb_writeline(x):
    ser.write(bytes(str(x) + "\n", "utf-8"))
    ser.flush()


def read_samples():
    # Set number of samples (NOT number of seconds!)
    n = 100
    volts = [float] * n
    amps = [float] * n

    # Increase DAC output voltage while reading amps
    # through the diode using the INA219 current sensor
    print("Reading samples")
    for i in range(n):
        # Set DAC output voltage
        dac.raw_value = 1125 + i * 30
        volts[i] = dac.raw_value / 4095 * 2.42
        time.sleep(0.2)
        # Calculate average amps using 100 samples
        a = 0
        for _ in range(50):
            # Read current flowing through load resistor
            a += ina219.current
            time.sleep(0.001)
        amps[i] = a / 50

    # Turn off DAC voltage to circuit
    dac.raw_value = 0

    # Transfer data over USB
    print("Sending samples")
    usb_writeline(n)  # number of samples
    for val in volts:
        usb_writeline(val)  # volts array
    for val in amps:
        usb_writeline(val)  # amps array


while True:
    print("Waiting")
    cmd = usb_readline()
    if cmd == "r":
        read_samples()
