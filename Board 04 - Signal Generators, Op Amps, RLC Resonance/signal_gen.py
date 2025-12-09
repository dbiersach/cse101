# signal_gen.py
# Measure sine wave frequency and amplitude

# Uses (1) AITRIP AD9833 Signal Generator

import time
from pathlib import Path

import analogio
import board
import busio
import digitalio
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import (
    AutoMinorLocator,
    FormatStrFormatter,
    MaxNLocator,
    MultipleLocator,
)
from scipy.signal import find_peaks

from ad9833_blinka import AD9833

# Configure analog input pin (FROM the AD9833)
pin_adc = analogio.AnalogIn(board.ADC1)

# Configure chip select (FSYNC on AD9833) on GP22
pin_cs = digitalio.DigitalInOut(board.GP22)
pin_cs.switch_to_output(value=True)  # idle high (not selected)

# Create SPI (MISO not used by AD9833)
spi_bus = busio.SPI(board.GP18, MOSI=board.GP19, MISO=None)

# Configure AD9833 Signal Generator
wave_gen = AD9833(spi_bus, pin_cs)
wave_gen.waveform = "sine"
wave_gen.frequency = 30.0

# Set number of samples
n = 1000
print(f"Reading {n} samples...")

# Allocate arrays
times_ns = np.empty(n, dtype=np.int64)  # nanoseconds since t0
adc_raw = np.empty(n, dtype=np.uint16)  # AnalogIn.value is 0..65535

# Measure the ADC as quickly as possible
for i in range(n):
    adc_raw[i] = pin_adc.value
    times_ns[i] = time.perf_counter_ns()

# Convert to volts and times
vol_ref = 3.3  # Maximum RP2040 ADC input is 3.3V
volts = adc_raw.astype(np.float32) * (vol_ref / 65535.0)
times_ns -= times_ns[0]
times = times_ns.astype(np.float64) * 1e-9

# Only keep the first second of samples
keep = times <= 1.0
times = times[keep]
volts = volts[keep]

# Trim samples to start from the first minimum
keep = np.argmin(volts[:15])
times = times[keep:]
volts = volts[keep:]
times = times - times[0]

# Save samples to a CSV file
samples = np.column_stack((times, volts))
file_name = "samples_ad9833.csv"
file_path = Path(__file__).parent / file_name
np.savetxt(file_name, samples, fmt="%3.6f", delimiter=",")
print(f"Saved file {file_name}")

# Find the number of peaks in sampled waveform
volt_threshold = 0.34  # Maximum output of AD9833 sine wave is 0.68V
peaks, _ = find_peaks(volts, height=volt_threshold, distance=5)
peak_intervals = np.diff(times[peaks])
avg_period = np.mean(peak_intervals)
avg_freq = times[-1] / avg_period

# Create a plot window
plt.figure("signal_gen.py")
plt.gca().set_facecolor("black")
plt.plot(times, volts, color="magenta")
plt.scatter(times[peaks], volts[peaks], color="yellow")
plt.title(f"AD9833 Signal Generator: {avg_freq:.2f} Hz")
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.ylim(0, vol_ref)
plt.gca().xaxis.set_major_locator(MaxNLocator(11))
plt.gca().xaxis.set_major_formatter(FormatStrFormatter("%.2f"))
plt.gca().xaxis.set_minor_locator(AutoMinorLocator(2))
plt.gca().yaxis.set_major_locator(MultipleLocator(0.25))
plt.gca().yaxis.set_minor_locator(AutoMinorLocator(2))
plt.grid(which="both", color="gray", linestyle="dotted", alpha=0.5)
plt.axhline(volt_threshold, color="yellow", linestyle="dotted", linewidth=2)
plt.show()
