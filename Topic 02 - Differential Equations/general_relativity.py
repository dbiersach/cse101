#!/usr/bin/env python3
"""general_relativity.py"""

from math import ceil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
from tqdm import tqdm


def estimate_precession_slope(alpha):
    """
    Simulate Mercury's orbit with a given general relativity correction alpha
    and return the slope of perihelion angle vs time (degrees per year).

    Parameters
    ----------
    alpha : float
        Modified gravity force correction to induce precession (AU²)

    Returns
    -------
    float
        Slope of perihelion angle vs time (degrees per year)
    """
    tf = 5  # final time in Julian years
    n = ceil(tf * 365.25 * 24)  # Sample every hour
    dt = tf / n  # time step in Julian years

    # Physical constants (SI → AU/yr)
    m_sun = 1.98847e30
    G = 6.67430e-11
    year_s = 3.15576e7
    AU = 1.495978707e11
    GM = G * m_sun * year_s**2 / AU**3  # AU^3 / yr^2
    a = 0.47  # # Mercury semi-major axis (AU)

    # Time, radius(distance), and velocity arrays
    t = np.arange(n) * dt
    r = np.empty(n)
    x = np.empty(n)
    y = np.empty(n)
    vx = np.empty(n)
    vy = np.empty(n)

    # Mercury's orbital initial conditions
    x[0] = a  # AU
    y[0] = 0.0
    vx[0] = 0.0
    vy[0] = 8.2  # AU/yr
    r[0] = np.hypot(x[0], y[0])

    # Time integration (Euler–Cromer)
    for i in range(1, n):
        # Calculate distance from Sun
        r_prev = np.hypot(x[i - 1], y[i - 1])
        # Calculate acceleration with modified gravity
        corr = 1.0 + alpha / (r_prev**2)  # Correction factor
        ax = -GM * x[i - 1] / (r_prev**3) * corr
        ay = -GM * y[i - 1] / (r_prev**3) * corr
        # Calculate new velocity and position using Euler-Cromer method
        vx[i] = vx[i - 1] + ax * dt
        vy[i] = vy[i - 1] + ay * dt
        x[i] = x[i - 1] + vx[i] * dt
        y[i] = y[i - 1] + vy[i] * dt
        # Update radius
        r[i] = np.hypot(x[i], y[i])

    # Calculate the perihelion points and angles
    peri_idx, _ = find_peaks(-r)
    peri_angles = np.degrees(np.unwrap((np.arctan2(y[peri_idx], x[peri_idx]))))

    # Fit line to perihelion angle vs time to get slope
    m, b = np.polyfit(t[peri_idx], peri_angles, 1)  # degree=1 → line

    return m


def main():
    """Main function to run the simulation and plot results."""

    # Sweep over alpha values to determine slope of perihelion angle vs time
    alpha_span = np.linspace(0.0001, 0.001, 11)
    slopes = np.array([estimate_precession_slope(a) for a in tqdm(alpha_span)])

    # Fit line to slope vs alpha data
    m, b = np.polyfit(alpha_span, slopes, 1)  # degree=1 → line
    y_fit = m * alpha_span + b  # y = mx + b where b = 0

    # Calculate and print precession rate for Mercury
    precession = m * 1.1e-8 * 3_600 * 100  # arcseconds per century

    # Plot slope of perihelion angle vs time as a function of alpha
    fig, ax = plt.subplots(num=Path(__file__).name)
    ax.set_title(
        "Estimated Precession of Mercury = "
        rf"$\mathbf{{{precession:.0f}}}\ \mathrm{{arcsec/century}}$"
    )
    ax.scatter(alpha_span, slopes, marker="o", c="r", label="Simulation Data")
    ax.plot(alpha_span, y_fit, lw=2, label="Linear Fit")
    ax.set_xlabel(r"$\alpha$ (AU$^2$)")
    ax.set_ylabel(r"$\dfrac{d\theta}{dt}$ (degrees/yr)")
    ax.legend(loc="center right", framealpha=1.0, facecolor="white")
    ax.grid(True)
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
