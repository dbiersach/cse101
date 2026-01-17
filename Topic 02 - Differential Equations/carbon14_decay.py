#!/usr/bin/env uv run
"""carbon14_decay.py"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

tf = 40_000  # final time (years)
ts = 100  # time steps
dt = tf / ts  # delta time (so updates every 400 years)

# Initialize time and concentration arrays
t = np.zeros(ts)
n = np.zeros(ts)

tau = 5730  # half-life of C-14 (years)
n[0] = 100.0  # initial amount of C-14 (% concentration)

# Euler's method to solve the decay ODE
for i in range(ts - 1):
    t[i + 1] = t[i] + dt
    n[i + 1] = n[i] - n[i] / tau * dt

plt.figure(Path(__file__).name)
plt.plot(t, n)
plt.title("Carbon-14 Decay")
plt.xlabel("Time (years)")
plt.ylabel("% Concentration")
plt.show()
