# plot_parabola.py

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(-4, 5)
y = np.power(x, 2) + 1.0

plt.figure(Path(__file__).name)
plt.plot(x, y)
plt.title("$y = x^2+1$")
plt.xlabel("x")
plt.ylabel("y")
plt.xlim(-6, 6)
plt.ylim(-3, 30)
plt.grid(True)
plt.plot(0, 1, color="red", marker="o")
plt.axhline(1, color="gray", linestyle="--")
plt.show(block=True)
sys.exit()
