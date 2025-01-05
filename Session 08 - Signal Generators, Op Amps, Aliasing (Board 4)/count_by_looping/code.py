# code.py for Raspberry Pi Pico 2
# Lab: count_by_looping
# Measure square waves

# Uses Adafruit Si5351 Clock Generator

import time

import adafruit_si5351
import board
import digitalio
import supervisor
import usb_cdc

# Wait until USB console port is ready
while not supervisor.runtime.usb_connected:
    pass
print("Lab: count_by_looping")

# Create USB data port
ser = usb_cdc.data

# Configure pulse sensing pin (ADC#1 is GPIO#27)
pin_pulse = digitalio.DigitalInOut(board.GP27)
pin_pulse.direction = digitalio.Direction.INPUT
pin_pulse.pull = digitalio.Pull.UP

# Initialize I2C bus and Si5351 Clock Generator
i2c = board.STEMMA_I2C()
si5351 = adafruit_si5351.SI5351(i2c)

# Start clock generator @ 10 MHz
si5351.pll_a.configure_integer(30)  # Base 25 MHz * 30 = 750 MHz
si5351.clock_0.configure_integer(si5351.pll_a, 75)  # 750 / 75 = 10 MHz
si5351.outputs_enabled = True


def usb_readline():
    return ser.readline().decode("utf-8").strip()


def usb_writeline(x):
    ser.write(bytes(str(x) + "\n", "utf-8"))
    ser.flush()


def read_samples():
    print("Counting pulses for 10 seconds")
    counts = 0
    time_start = time.monotonic_ns()
    while True:
        while pin_pulse.value is True:  # Wait for FALLING edge
            pass
        while pin_pulse.value is False:  # Wait for RISING edge
            pass
        counts += 1
        if time.monotonic_ns() - time_start > 10_000_000_000:  # 10 secs
            break
    print(f"{counts:,} total pulses")
    usb_writeline(counts)


while True:
    print("Waiting")
    cmd = usb_readline()
    if cmd == "r":
        read_samples()
