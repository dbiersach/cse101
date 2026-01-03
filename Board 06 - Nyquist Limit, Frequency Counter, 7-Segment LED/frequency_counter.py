# frequency_counter.py
# Determine the capture limit of a hardware frequency counter

# Uses (1) LSI Computer Systems LS7366R Counter
# Uses (1) Adafruit Si5351A Clock Generator

import time
from pathlib import Path

import adafruit_si5351
import board
import busio
import digitalio
import matplotlib.pyplot as plt
import numpy as np
from ls7366r_blinka import LS7366R
from matplotlib.ticker import MultipleLocator
from tqdm import tqdm

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
counter = LS7366R(spi, cs)
counter.configure_non_quadrature_4byte(count_enable=True)
counter.clear_status()

# Initialize the Si5351 clock generator
i2c_bus = busio.I2C(board.SCL0, board.SDA0)
si5351 = adafruit_si5351.SI5351(i2c_bus)

# Read in the clock settings data file
file_name = "clock_settings.csv"
file_path = Path(__file__).parent / file_name
frequency_mhz, pll_multiplier, clock_divider = np.genfromtxt(
    file_path, unpack=True, skip_header=1, delimiter=","
)
n = len(frequency_mhz)
print(f"Reading {n} samples...")

# Create the array to store sampling errors
err = np.zeros(n, float)  # Absolute percent relative error (APRE)

# Read pulses from the clock generator at each frequency
for i in tqdm(range(n)):
    # Set the Si5351 Clock Generator frequency
    si5351.pll_a.configure_integer(pll_multiplier[i])
    si5351.clock_2.configure_integer(si5351.pll_a, clock_divider[i])
    si5351.outputs_enabled = True

    # Measure pulses using the LS7366R over exactly 1 second
    t0 = time.perf_counter_ns()
    counter.zero()  # Reset counter to 0
    while time.perf_counter_ns() - t0 < 1_000_000_000:
        pass
    actual_mhz = counter.read_counter(signed=False) / 1_000_000

    # Calculate percent relative error
    predicted_mhz = frequency_mhz[i]
    err[i] = np.abs((actual_mhz - predicted_mhz) / predicted_mhz) * 100


# Plot samples
plt.figure(Path(__file__).name)
plt.gca().set_facecolor("black")
plt.plot(frequency_mhz, err, color="magenta")
plt.title("LS7366R Counter Error vs. Frequency")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Percent Error")
plt.gca().xaxis.set_major_locator(MultipleLocator(2))
plt.gca().yaxis.set_major_locator(MultipleLocator(10))
plt.show()
