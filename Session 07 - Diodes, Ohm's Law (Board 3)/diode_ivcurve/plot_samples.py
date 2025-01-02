# plot_samples.py
# Lab: diode_ivcurve

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FormatStrFormatter, MultipleLocator

# Read samples
file_name = "samples.csv"
file_path = Path(__file__).parent / file_name
volts, amps = np.genfromtxt(file_path, delimiter=",", unpack=True)

# Find index of sample with maximum amps, then use
# that index to find the corresponding max voltage
max_volts = volts[np.argmax(amps)]

# Plot the graph on the main axes
plt.figure(Path(__file__).name)
plt.gca().set_facecolor("black")
plt.plot(volts, amps, color="yellow", linewidth=2)
plt.title("1N4001 Diode I-V Characteristic Curve")
plt.xlabel("Voltage (V)")
plt.ylabel("Current (mA)")
plt.gca().xaxis.set_major_locator(MultipleLocator(0.1))
plt.gca().xaxis.set_major_formatter(FormatStrFormatter("%.2f"))
plt.gca().yaxis.set_major_locator(MultipleLocator(1.0))
plt.gca().yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
plt.axvline(max_volts, color="green", linestyle="--")
plt.grid(which="both", color="lightgray", linestyle="dotted", alpha=0.5)
plt.show(block=True)
sys.exit()
