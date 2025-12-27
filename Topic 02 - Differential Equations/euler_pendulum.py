#!/usr/bin/env python3
"""euler_pendulum.py"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

tf = 10  # final time (seconds)
ts = 500  # time steps
dt = tf / ts  # delta time (so updates every 20 ms)

# Initialize arrays
t = np.zeros(ts)
omega = np.zeros(ts)
theta = np.zeros(ts)

length = 1.0  # pendulum length (m)
theta[0] = np.deg2rad(45)  # initial angle (radians)
g = 9.81  # gravity (m/s^2)

# Euler method loop
for i in range(ts - 1):
    t[i + 1] = t[i] + dt
    omega[i + 1] = omega[i] - g / length * np.sin(theta[i]) * dt
    theta[i + 1] = theta[i] + omega[i] * dt

plt.figure(Path(__file__).name)
(plot1,) = plt.plot(t, theta, lw=2)
(plot2,) = plt.plot(t, omega, lw=2)
plt.title("Simple Pendulum (Euler's Method)")
plt.xlabel("Time (sec)")
plt.ylabel(r"Angular Displacement $\theta$ (rad)")
plt.twinx()
plt.ylabel(r"Angular Velocity $\omega$ (rad/s)")
legend_lines = [plot1, plot2]
legend_labels = [r"$\theta$", r"$\omega$"]
plt.legend(
    [plot1, plot2], [r"$\theta$", r"$\omega$"], framealpha=1.0, facecolor="white"
)
plt.grid("on")
plt.show()
