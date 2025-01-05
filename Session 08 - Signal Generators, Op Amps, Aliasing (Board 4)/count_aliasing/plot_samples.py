# plot_samples.py
# Lab: count_aliasing

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

# Read samples
file_name = "samples.csv"
file_path = Path(__file__).parent / file_name
expected_mhz, measured_mhz = np.genfromtxt(file_path, delimiter=",", unpack=True)

# Plot samples
plt.figure("plot_samples.py", figsize=(12, 8), tight_layout=True)
plt.gca().set_facecolor("black")
plt.plot(expected_mhz, expected_mhz, color="lightgreen", linewidth=2, label="Expected")
plt.plot(expected_mhz, measured_mhz, color="blue", linewidth=2, label="Measured")
plt.title("Adafruit Si5351 Clock Generator as measured by the Pi Pico 2")
plt.xlabel("Expected Frequency (MHz)")
plt.ylabel("Measured Frequency (MHz)")
plt.legend(loc="upper right")
plt.gca().xaxis.set_major_locator(MultipleLocator(5))
plt.gca().yaxis.set_major_locator(MultipleLocator(5))
plt.xticks(rotation=90)
plt.xlim(10)
plt.ylim(10)
plt.axvline(x=70, color="yellow", linestyle="--")
plt.axvline(x=115, color="red", linestyle="--")
plt.grid(which="both", color="gray", linestyle="dotted", alpha=0.5)
plt.show(block=True)
sys.exit()
