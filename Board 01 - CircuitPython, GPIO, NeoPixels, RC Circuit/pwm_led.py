# pwm_led.py
# Fade external RED LED from off to on to off in

# Uses (1) 330 Ohm Resistor
# Uses (1) RED LED (660 nm Wavelength, 1.85V, 20mA)

import board
import pwmio

# Initialize GPIO pin for OUTPUT
pin_led = pwmio.PWMOut(board.GP22, frequency=5000, duty_cycle=0)

while True:
    # Fade from off to on
    for duty in range(0, 65536, 256):  # 0 to 65535 in steps of 256
        pin_led.duty_cycle = duty

    # Fade from on to off
    for duty in range(65535, -1, -256):
        pin_led.duty_cycle = duty
