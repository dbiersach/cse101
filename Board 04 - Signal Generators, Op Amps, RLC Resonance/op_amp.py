# op_amp.py
# Measure sine wave frequency and amplitude

# Uses (1) AITRIP AD9833 Signal Generator
# Uses (1) Adafruit TLV2462 Op Amp
# Uses (1) 10K Ohm and (1) 22K Ohm Resistor

import time
from pathlib import Path

import analogio
import board
import busio
import digitalio
import matplotlib.pyplot as plt
import numpy as np
from ad9833_blinka import AD9833
from matplotlib.ticker import (
    AutoMinorLocator,
    FormatStrFormatter,
    MaxNLocator,
    MultipleLocator,
)

# Set number of samples
n = 1000
print(f"Reading {n} samples...")

# Allocate arrays
times_ns = np.empty(n, dtype=np.int64)  # nanoseconds since t0
adc_raw = np.empty(n, dtype=np.uint16)  # AnalogIn.value is 0..65535

# Configure analog input pin (FROM the AD9833)
pin_adc = analogio.AnalogIn(board.ADC1)

# Create SPI (MISO not used by AD9833)
spi_bus = busio.SPI(clock=board.GP18, MOSI=board.GP19, MISO=None)

# Configure chip select (FSYNC on AD9833) on GP22
pin_cs = digitalio.DigitalInOut(board.GP22)
pin_cs.switch_to_output(value=True)  # idle high (not selected)

# Configure AD9833 Signal Generator
wave_gen = AD9833(spi_bus, pin_cs, baudrate=100_000)
wave_gen.reset(state=True)  # Hold in reset
wave_gen.waveform = "sine"
wave_gen.frequency = 30  # Load frequency (Hz) while in reset
wave_gen.phase = 0.0  # Load phase while in reset
wave_gen.reset(state=False)  # Power up and start outputting

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

# Read in the volts from the raw AD9833 (before amplification)
file_name = "samples_ad9833.csv"
file_path = Path(__file__).parent / file_name
file_times, file_volts = np.genfromtxt(file_path, delimiter=",", unpack=True)

# Create a plot window
plt.figure(Path(__file__).name)
plt.gca().set_facecolor("black")
plt.plot(file_times, file_volts, color="magenta", linewidth=2, label="AD9833")
plt.plot(times, volts, color="lime", linewidth=2, label="AD9833+TLV2462")
plt.legend()
plt.title("TLV2462 Operational Amplifier")
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.gca().xaxis.set_major_locator(MaxNLocator(11))
plt.gca().xaxis.set_major_formatter(FormatStrFormatter("%.3f"))
plt.gca().xaxis.set_minor_locator(AutoMinorLocator(2))
plt.gca().yaxis.set_minor_locator(AutoMinorLocator(2))
plt.gca().yaxis.set_major_locator(MultipleLocator(0.25))
plt.grid(which="both", color="gray", linestyle="dotted", alpha=0.5)
plt.axhline(0, color="gray", linestyle="--", alpha=0.65)
plt.axhline(3.3, color="red")
plt.axhline(np.mean(volts), color="yellow", linestyle="--", alpha=0.65)
plt.axvline(0.0, color="yellow", linestyle="--", alpha=0.65)
plt.axvline(1.0, color="yellow", linestyle="--", alpha=0.65)
plt.show()
