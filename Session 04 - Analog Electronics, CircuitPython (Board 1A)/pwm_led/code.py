# code.py for Raspberry Pi Pico 2
# Lab: pwm_led
# Fade external RED LED from off to on to off in

# Uses (1) 330 Ohm Resistor
# Uses (1) RED LED (660 nm Wavelength, 1.85V, 20mA)

import board
import pwmio
import time

# Initialize GPIO pin for OUTPUT
pin_led = pwmio.PWMOut(board.GP22, frequency=5000, duty_cycle=0)


while True:
    # Fade from off to on
    for duty in range(65536):  # 0 to 65535
        pin_led.duty_cycle = duty

    # Fade from on to off
    for duty in range(65535, -1, -1):
        pin_led.duty_cycle = duty
