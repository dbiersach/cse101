# frequency_counter.py
# Determine the capture limit of a hardware frequency counter

# Uses (1) LSI Computer Systems LS7366R Counter
# Uses (1) Adafruit Si5351A Clock Generator

# The LS7366R must be powered from the 3V3 pin on the Pico, not VBUS.
# Its logic levels follow whatever VDD it is given, so a 5V part would drive
# 5V on MISO into a Pico SPI pin that is only rated for 3.3V.
#
# Running at 3.3V costs us speed. From the LS7366R datasheet, non-quadrature
# mode requires Clock A to hold each level for at least 24 ns when VDD = 3.3V,
# so the fastest pulse train it can count is
#     fA = 1 / (24 ns + 24 ns) = 20 MHz
# At VDD = 5.0V that minimum drops to 12 ns and fA rises to 40 MHz.
#
# So we sweep the Si5351A from 1 MHz to 30 MHz. Below 20 MHz the counter
# should track the clock generator almost perfectly. Above 20 MHz it starts
# missing pulses, and the measured frequency falls behind the true frequency.

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

# The datasheet count limit for the LS7366R when powered at 3.3V
COUNT_LIMIT_MHZ = 20

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
# At 3.3V the LS7366R needs SCK pulses of at least 120 ns, which caps the SPI
# bus at about 4 MHz. The 1 MHz baudrate set above stays well inside that.
counter = LS7366R(spi, cs)
counter.configure_non_quadrature_4byte(count_enable=True)
counter.clear_status()

# Initialize the Si5351 clock generator
i2c_bus = busio.I2C(board.SCL0, board.SDA0)
si5351 = adafruit_si5351.SI5351(i2c_bus)

# Read in the clock settings data file
# Lines beginning with "#" are header comments and are ignored
file_name = "clock_settings.csv"
file_path = Path(__file__).parent / file_name
frequency_mhz, pll_multiplier, clock_divider = np.genfromtxt(
    file_path, unpack=True, delimiter=",", comments="#"
)
n = len(frequency_mhz)
lo, hi = frequency_mhz[0], frequency_mhz[-1]
print(f"Sweeping {n} frequencies from {lo:.0f} MHz to {hi:.0f} MHz...")

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

# Report where the counter first loses more than 1% of the pulses
over_limit = np.flatnonzero(err > 1.0)
if over_limit.size > 0:
    print(f"Counting breaks down at {frequency_mhz[over_limit[0]]:.0f} MHz")
else:
    print("The counter tracked every frequency in the sweep")

# Plot samples
plt.figure(Path(__file__).name)
plt.gca().set_facecolor("black")
plt.plot(frequency_mhz, err, color="magenta")

# Mark the datasheet limit so students can compare it to the measured curve
plt.axvline(COUNT_LIMIT_MHZ, color="cyan", linestyle="--")
plt.text(
    COUNT_LIMIT_MHZ - 0.5,
    plt.ylim()[1] * 0.9,
    f"{COUNT_LIMIT_MHZ} MHz datasheet limit at 3.3V",
    color="cyan",
    horizontalalignment="right",
)

plt.title("LS7366R Counter Error vs. Frequency (VDD = 3.3V)")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Percent Error")
plt.gca().xaxis.set_major_locator(MultipleLocator(2))
plt.gca().yaxis.set_major_locator(MultipleLocator(10))
plt.show()
