# code.py for Raspberry Pi Pico 2
# Lab: bjt_amplification
# Measure BJT voltage over cutoff, active, and saturation
# regions when configured as a Common-Emitter amplifier

# Uses (1) PN2222A NPN BJT
# Uses (2) 1K Ohm Resistors
# Uses (1) MCP4725 DAC
# Uses (1) ADS1115 ADC

import board
import busio
import supervisor
import time
import usb_cdc
import adafruit_mcp4725
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Wait until USB console port is ready
while not supervisor.runtime.usb_connected:
    pass
print("Lab: bjt_amplification")

# Create USB data port
ser = usb_cdc.data

# Initialize I2C bus
i2c = board.STEMMA_I2C()

# Configure MCP4725 DAC and set output voltage LOW
dac = adafruit_mcp4725.MCP4725(i2c)
dac.raw_value = 0

# Configure ADS1115 ADC in differential mode (P0+, P1-)
adc = ADS.ADS1115(i2c)
adc_chan = AnalogIn(adc, ADS.P0, ADS.P1)


def usb_readline():
    return ser.readline().decode("utf-8").strip()


def usb_writeline(x):
    ser.write(bytes(str(x) + "\n", "utf-8"))
    ser.flush()


def read_samples():
    # Read 100 dummy values to initialize ADC
    for _ in range(100):
        _ = adc_chan.voltage

    # Set number of samples (NOT number of seconds!)
    n = 450
    volts_be = [float] * n  # Base-Emitter voltage
    volts_ce = [float] * n  # Collector-Emitter voltage

    # Read volts from ADC
    print("Reading samples")
    for i in range(n):
        # Set DAC output voltage which is the volts between
        # the BJT base and emitter as emitter is at GND
        dac.raw_value = 572 + i
        volts_be[i] = dac.raw_value / 4096 * 3.3
        # Read the voltage drop across the collector's resistor
        volts_ce[i] = adc_chan.voltage

    # Turn off DAC voltage to circuit
    dac.raw_value = 0

    # Transfer data over USB
    print("Sending samples")
    usb_writeline(n)  # number of samples
    for val in volts_be:
        usb_writeline(val)  # Base-Emitter volts array
    for val in volts_ce:
        usb_writeline(val)  # Collector-Emitter volts array


while True:
    print("Waiting")
    cmd = usb_readline()
    if cmd == "r":
        read_samples()
