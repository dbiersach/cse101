# rc_circuit.py
# Voltage across charging and discharging resistor-capacitor circuit

# Uses (1) 10K ohm resistor (1/2 watt, 1% tolerance)
# Uses (1) 10uF 25V electrolytic capacitor (20% tolerance)

import time
from pathlib import Path

import analogio
import board
import digitalio
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.ticker import (
    AutoMinorLocator,
    FormatStrFormatter,
    MaxNLocator,
    MultipleLocator,
)
from tqdm import tqdm

# Configure pins
pin_adc = analogio.AnalogIn(board.ADC1)
pin_charge = digitalio.DigitalInOut(board.GP22)
pin_charge.direction = digitalio.Direction.OUTPUT
pin_charge.value = False

# Set number of samples
n = 1000
half_n = int(n / 2)
print(f"Reading {n} samples...")
times = np.zeros(n, dtype=float)
volts = np.zeros(n, dtype=float)

# Energize circuit (charge capacitor)
pin_charge.value = True
for i in tqdm(range(half_n)):
    times[i] = time.time_ns()
    volts[i] = pin_adc.value

# Drain circuit (discharge capacitor)
pin_charge.value = False
for i in tqdm(range(half_n, n)):
    times[i] = time.time_ns()
    volts[i] = pin_adc.value

# Convert to elapsed time in seconds
times = (times - times[0]) / 1e9
# Convert to volts
volts = volts * (3.3 / 65535)

# Find the middle time value
# mid_time = times[-1] / 2
mid_time = times[half_n]

# Calculate theoretical performance curve
V_s = 3.3  # Volts
R = 10_121  # Ohms
C = 0.00001069  # Farads
tau = R * C
t = np.linspace(0, mid_time, 100)
v1_c = V_s * (1 - np.exp(-t / tau))  # Charge
v2_c = V_s * np.exp(-t / tau)  # Decay

# Create a plot window
plt.figure(Path(__file__).name)
plt.gca().set_facecolor("black")

# Plot actual voltage
plt.plot(times, volts, color="magenta", linewidth=2, label="Actual")

# Plot theoretical voltage
plt.plot(t, v1_c, color="cyan", linewidth=2, label="Theory")
plt.plot(t + mid_time, v2_c, color="cyan", linewidth=2)

# Give the graph a title, axis labels, and display the legend
plt.title("Capacitor Voltage vs. Time")
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.legend()

# Set tick marks
plt.gca().xaxis.set_major_locator(MaxNLocator(11))
plt.gca().xaxis.set_major_formatter(FormatStrFormatter("%.2f"))
plt.gca().xaxis.set_minor_locator(AutoMinorLocator(2))
plt.gca().yaxis.set_major_locator(MultipleLocator(0.25))
plt.grid(which="both", color="gray", linestyle="dotted", alpha=0.5)

# Create straight lines to depict charging pin status over time
line_on = [(0, 0), (0, 3.3)]
line_charging = [(0, 3.3), (mid_time, 3.3)]
line_off = [(mid_time, 3.3), (mid_time, 0)]
line_discharging = [(mid_time, 0), (times[-1], 0)]
lc = LineCollection(
    [line_on, line_charging, line_off, line_discharging],
    color="yellow",
    linewidth=2,
    zorder=2.5,
)
plt.gca().add_collection(lc)

# Draw dashed lines starting at offset 0, with 5 units "on" and 6 units "off"
plt.axvline(0.1, color="yellow", linestyle=(0, (5, 6)), alpha=0.65)
plt.axvline(mid_time + 0.1, color="yellow", linestyle=(0, (5, 6)), alpha=0.65)

plt.show()
