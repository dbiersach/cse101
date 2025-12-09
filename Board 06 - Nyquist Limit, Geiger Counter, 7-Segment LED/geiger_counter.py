# geiger_counter.py
# Determine the capture limit of a hardware frequency counter

# Uses (1) LSI Computer Systems LS7366R Counter

import time

import board
import busio
import digitalio

from ls7366r_blinka import LS7366R

# Initialize the SPI bus
spi = busio.SPI(clock=board.GP18, MOSI=board.GP19, MISO=board.GP16)
while not spi.try_lock():
    pass
try:
    spi.configure(baudrate=1_000_000, polarity=0, phase=0)  # Mode 0
finally:
    spi.unlock()

# Configure chip-select (CS) pin for SPI bus
# This should be wired to "SS/" (pin 4) on the LS7366R
# NOTE: The trailing "/" means CS is active LOW
cs = digitalio.DigitalInOut(board.GP17)
cs.direction = digitalio.Direction.OUTPUT

# Configure the LS7366R quadrature encoder counter
enc = LS7366R(spi, cs)
enc.configure_non_quadrature_4byte(count_enable=True)
enc.clear_status()

while True:
    # Measure pulses using the LS7366R over exactly 1 second
    t0 = time.perf_counter_ns()
    enc.zero()  # Reset counter to 0
    while time.perf_counter_ns() - t0 < 1_000_000_000:
        pass
    actual_mhz = enc.read_counter(signed=False) / 1_000_000

    print(f"Measured {actual_mhz:>8.5f} MHz")
