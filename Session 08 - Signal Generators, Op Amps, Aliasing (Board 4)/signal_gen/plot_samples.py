# plot_samples.py
# Lab: signal_gen

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import (
    AutoMinorLocator,
    FormatStrFormatter,
    MaxNLocator,
    MultipleLocator,
)

# Read samples
file_name = "samples.csv"
file_path = Path(__file__).parent / file_name
times, volts = np.genfromtxt(file_path, delimiter=",", unpack=True)

# Set times to be elapsed time & scale to seconds
times -= times[0]
times *= 1e-9
# Scale volts to fall between 0 and 3.3V
volts /= 65535
volts *= 3.3

# Save these samples for comparison with the omp_amp lab
file_name = "ad9833_volts.txt"
file_path = Path(__file__).parent / file_name
np.savetxt(file_path, volts)

# Create a plot window with a black background
plt.figure("sig_gen.py")
plt.gca().set_facecolor("black")
plt.plot(times, volts, color="magenta", linewidth=2)
plt.title("AD9833 Signal Generator")
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.gca().xaxis.set_major_locator(MaxNLocator(11))
plt.gca().xaxis.set_major_formatter(FormatStrFormatter("%.3f"))
plt.gca().xaxis.set_minor_locator(AutoMinorLocator(2))
plt.gca().yaxis.set_major_locator(MultipleLocator(0.25))
plt.gca().yaxis.set_minor_locator(AutoMinorLocator(2))
plt.grid(which="both", color="gray", linestyle="dotted", alpha=0.5)
plt.axhline(0, color="gray", linestyle="--", alpha=0.65)
plt.axhline(3.3, color="red")
plt.axhline(np.mean(volts), color="yellow", linestyle="--", alpha=0.65)
plt.axvline(0.0, color="yellow", linestyle="--", alpha=0.65)
plt.axvline(1.0, color="yellow", linestyle="--", alpha=0.65)
plt.show(block=True)
sys.exit()
