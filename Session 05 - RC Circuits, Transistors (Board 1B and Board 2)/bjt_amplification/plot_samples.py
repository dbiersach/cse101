# plot_samples.py
# Lab: bjt_amplification.py

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# Read samples
file_name = "samples.csv"
file_path = Path(__file__).parent / file_name
volts_be, volts_ce = np.genfromtxt(file_path, delimiter=",", unpack=True)

# Find points of within the active region of the BJT
i1 = np.where(volts_be > 0.6)[0][0]
i2 = np.where(volts_be > 0.7)[0][0]
vb0 = volts_be[0]
vb1, vc1 = volts_be[i1], volts_ce[i1]
vb2, vc2 = volts_be[i2], volts_ce[i2]

# Plot samples
plt.figure(Path(__file__).name)
plt.gca().set_facecolor("black")
plt.plot(volts_be, volts_ce, color="yellow", linewidth=2)
plt.title("PN2222A (NPN) BJT Amplification")
plt.xlabel("Base-Emitter Voltage (V)")
plt.ylabel("Collector-Emitter Voltage (V)")
plt.grid(which="both", color="grey", linestyle="dotted", alpha=0.5)
plt.vlines(vb1, 0, vc1, color="g", linestyle="--")
plt.hlines(vc1, vb0, vb1, color="g", ls="--")
plt.vlines(vb2, 0, vc2, color="r", linestyle="--")
plt.hlines(vc2, vb0, vb2, color="r", ls="--")
plt.show(block=True)
sys.exit()
