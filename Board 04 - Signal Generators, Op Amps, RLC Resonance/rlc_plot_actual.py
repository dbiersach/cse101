# rlc_plot_actual.py
# Plot actual frequency response of driven RLC circuit

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import (
    AutoMinorLocator,
    FormatStrFormatter,
)

# Load measured (actual) volts from the RLC circuit
file_name = file_name = "rlc_resonance.csv"
file_path = Path(__file__).parent / file_name
freq, volts_actual = np.genfromtxt(file_path, delimiter=",", unpack=True)

# Resonant frequency is at the peak voltage
max_volt_actual = np.max(volts_actual)
resonance_freq_actual = freq[np.argmax(volts_actual)]
print(f"Actual Resonance voltage = {max_volt_actual:0.4f} V")
print(f"Actual Resonance freq = {resonance_freq_actual:0.4f} kHz")

# Create a plot window
plt.figure(Path(__file__).name)
plt.gca().set_facecolor("black")
plt.scatter(freq, volts_actual, color="magenta", s=1)
plt.vlines(resonance_freq_actual, 0, max_volt_actual, color="yellow", linewidth=2)
plt.title(f"RLC Circuit Resonance (Actual) - {resonance_freq_actual} kHz")
plt.xlabel("Frequency (kHz)")
plt.ylabel("Voltage (V)")
plt.gca().xaxis.set_minor_locator(AutoMinorLocator())
plt.gca().xaxis.set_major_formatter(FormatStrFormatter("%0.3f"))
plt.xlim(0, 5)  # 0 to 5 kHz
plt.ylim(0, 0.3)  # 0 to 0.3 Volts
plt.show()
