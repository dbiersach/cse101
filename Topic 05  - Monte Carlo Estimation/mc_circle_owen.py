#!/usr/bin/env python3
"""mc_circle_owen.py"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import qmc


def main():
    dots = 25_600

    sampler = qmc.Halton(d=2, scramble=True, seed=2026)
    sample = sampler.random(n=dots, workers=-1)
    sample = qmc.scale(sample, -1, 1)

    x = sample[:, 0]
    y = sample[:, 1]

    d = x**2 + y**2

    x_in = x[d <= 1.0]
    y_in = y[d <= 1.0]
    x_out = x[d > 1.0]
    y_out = y[d > 1.0]

    act_area = np.pi
    est_area = np.count_nonzero(d <= 1.0) / dots * 4
    err = np.abs((est_area - act_area) / act_area)

    print(f"dots = {dots:,}")
    print(f"act = {act_area:.6f}")
    print(f"est = {est_area:.6f}")
    print(f"err = {err:.5%}")

    plt.figure(Path(__file__).name)
    plt.scatter(x_in, y_in, color="red", marker=".", s=0.5)
    plt.scatter(x_out, y_out, color="blue", marker=".", s=0.5)
    plt.axis("equal")
    plt.show()


if __name__ == "__main__":
    main()
