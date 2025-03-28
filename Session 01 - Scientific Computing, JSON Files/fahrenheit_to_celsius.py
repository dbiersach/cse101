# fahrenheit_to_celsius.py

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

k = np.linspace(0, 400)
f = 9 / 5 * (k - 273.15) + 32
c = 5 / 9 * (f - 32)

plt.figure(Path(__file__).name)
plt.plot(k, f, label="Fahrenheit")
plt.plot(k, c, label="Celsius")
plt.title("Temperature Scale Comparison")
plt.xlabel("Kelvin")
plt.ylabel("Temperature")
plt.legend(loc="upper left")
plt.grid(True)
plt.show(block=True)
sys.exit()
