# random_walk.py

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

np.random.seed(2017)
n = 10_000
x = np.zeros(n)
y = np.zeros(n)

for i in range(1, n):
    t = 2 * np.pi * np.random.rand()
    x[i] = x[i - 1] + np.cos(t)
    y[i] = y[i - 1] + np.sin(t)

plt.figure(Path(__file__).name, constrained_layout=True)
plt.get_current_fig_manager().full_screen_toggle()
plt.plot(x, y)
plt.plot(x[0], y[0], color="green", marker="o")
plt.plot(x[-1], y[-1], color="red", marker="o")
# fmt: off
plt.arrow(x[0], y[0], x[-1] - x[0], y[-1] - y[0],
        color="black", linestyle="--",  width=0.3,
        head_width=1,  length_includes_head=True, zorder=3)
# fmt: on
plt.gca().set_aspect("equal")
plt.show(block=True)
sys.exit()
