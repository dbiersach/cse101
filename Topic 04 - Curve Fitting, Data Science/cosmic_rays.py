#!/usr/bin/env -S uv run
"""identify_element.py"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def fit_linear(x, y):
    m = len(x) * np.sum(x * y) - np.sum(x) * np.sum(y)
    m = m / (len(x) * np.sum(x**2) - np.sum(x) ** 2)
    b = (np.sum(y) - m * np.sum(x)) / len(x)
    return m, b


def main():
    # Load data
    file_name = "ray.csv"
    time, height = np.genfromtxt(file_name, delimiter=",", unpack=True)

    # Calculate line of best fit
    slope, yint = fit_linear(time, height)

    # Calculate origination height and velocity
    oh = (slope * 1e9 / 100) * (0.1743 / 1e3) / 1000
    v = slope / 29.98

    # Plot data and line of best fit
    plt.figure(Path(__file__).name, figsize=(12, 8))
    plt.scatter(time, height)
    plt.plot(time, slope * time + yint, color="red", linewidth=2)
    plt.title(
        "Secondary Cosmic Ray Trajectory\n"
        f"Velocity = {v:.2f}c "
        f"Origination Height = {oh:,.2f}km",
    )
    plt.xlabel("Time (ns)")
    plt.ylabel("Detector Height (cm)")
    plt.grid("on")
    plt.show()


if __name__ == "__main__":
    main()
