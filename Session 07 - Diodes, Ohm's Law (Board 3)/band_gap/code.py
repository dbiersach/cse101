# code.py for Raspberry Pi Pico 2
# Lab: band_gap
# Compare forward voltage of RED vs BLUE LEDs

# Uses (1) MCP4725 DAC
# Uses (1) PN2222A BJT
# Uses (1) 330 Ohm Resistor
# Uses (1) 10K Ohm Resistor
# Uses (1) Blue LED

import adafruit_mcp4725
import board

# Configure I2C bus
i2c_bus = board.STEMMA_I2C()

# Configure MCP4725 DAC
dac = adafruit_mcp4725.MCP4725(i2c_bus)

required_voltage = 1.97

# Set DAC output voltage
# The NPN BJT emitter follower causes a 0.66V drop from 3.3V
dac.normalized_value = required_voltage / (3.3 - 0.66)
