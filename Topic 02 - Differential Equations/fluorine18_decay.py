#!/usr/bin/env uv run
"""fluorine18_decay.py"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

tf = 12  # final time (hours)
ts = 100  # time steps
dt = tf / ts  # delta time (so updates every 7.2 minutes)

# Initialize time and concentration arrays
t = np.zeros(ts)
n = np.zeros(ts)

tau = 1.833  # half-life of F-18 (hours)
n[0] = 100.0  # initial amount of F-18 (% concentration)

# Euler's method to solve the decay ODE
for i in range(ts - 1):
    t[i + 1] = t[i] + dt
    n[i + 1] = n[i] - n[i] / tau * dt

plt.figure(Path(__file__).name)
plt.plot(t, n)
plt.title("Fluorine-18 Decay")
plt.xlabel("Time (hours)")
plt.ylabel("% Concentration")
plt.show()
