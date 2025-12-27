# blink_led.py
# Blink external RED LED on and off

# Uses (1) 330 Ohm Resistor
# Uses (1) RED LED (660 nm Wavelength, 1.85V, 20mA)

import time

import board
import digitalio

# Initialize GPIO pin for OUTPUT
pin_led = digitalio.DigitalInOut(board.GP22)
pin_led.direction = digitalio.Direction.OUTPUT

while True:
    pin_led.value = True
    time.sleep(0.5)
    pin_led.value = False
    time.sleep(0.5)
