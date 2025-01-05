# code.py for Raspberry Pi Pico 2
# Lab: count_aliasing
# Measure square waves

# Uses (1) Adafruit Si5351 Clock Generator

import time

import adafruit_si5351
import board
import countio
import supervisor
import usb_cdc

# Wait until USB console port is ready
while not supervisor.runtime.usb_connected:
    pass

# Create USB data port
ser = usb_cdc.data

# Initialize I2C bus and Si5351 Clock Generator
i2c = board.STEMMA_I2C()
si5351 = adafruit_si5351.SI5351(i2c)

print("Lab: count_aliasing")


def usb_readline():
    return ser.readline().decode("utf-8").strip()


def usb_writeline(x):
    ser.write(bytes(str(x) + "\n", "utf-8"))
    ser.flush()


def read_samples(params):
    pll_multiplier = int(params[0])
    clock_divider = int(params[1])
    freq_mhz = pll_multiplier * 25 / clock_divider
    # Start clock generator
    si5351.pll_a.configure_integer(pll_multiplier)
    si5351.clock_0.configure_integer(si5351.pll_a, clock_divider)
    si5351.outputs_enabled = True
    print(f"Counting pulses at {freq_mhz:n} MHz")
    # Configure *digital* input pin (from Si5351)
    counter = countio.Counter(board.A1, edge=countio.Edge.RISE)
    time_start = time.monotonic_ns()
    while True:
        if time.monotonic_ns() - time_start > 1e9:  # One second
            break
    counts = counter.count
    usb_writeline(counts)
    counter.deinit()


while True:
    print("Waiting")
    params = usb_readline().split(",")
    read_samples(params)
