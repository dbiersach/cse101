#!/usr/bin/env -S uv run
"""pendulum_phase_space.py

Plots the phase space (theta vs omega) for an ideal pendulum,
comparing three numerical integrators against the exact energy
contour.

  Black dashed: Exact energy contour E(theta, omega) = E0
  Red:          Forward Euler    — spirals outward (energy gain)
  Orange:       Euler-Cromer     — wobbles around the contour
  Green:        Velocity Verlet  — hugs the contour tightly

The exact contour is computed from energy conservation:
  E = (1/2)omega^2 - (g/L)cos(theta)
so for a given E0, omega = +/- sqrt(2(E0 + (g/L)cos(theta)))
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# --- Physical constants ---
LENGTH = 1.0  # pendulum length (m)
G = 9.81  # gravity (m/s^2)


def angular_acceleration(theta):
    """alpha = -(g/L) sin(theta)"""
    return -G / LENGTH * np.sin(theta)


def total_energy(theta, omega):
    """Total mechanical energy: E = (1/2)w^2 - (g/L)cos(theta)."""
    return 0.5 * omega**2 - G / LENGTH * np.cos(theta)


# ========================================================================
# Integrators (all return t, theta, omega arrays)
# ========================================================================


def solve_forward_euler(theta0, omega0, t_final, dt):
    n_steps = int(t_final / dt)
    t = np.arange(n_steps) * dt
    theta = np.zeros(n_steps)
    omega = np.zeros(n_steps)
    theta[0], omega[0] = theta0, omega0
    for i in range(n_steps - 1):
        alpha = angular_acceleration(theta[i])
        omega[i + 1] = omega[i] + alpha * dt
        theta[i + 1] = theta[i] + omega[i] * dt
    return t, theta, omega


def solve_euler_cromer(theta0, omega0, t_final, dt):
    n_steps = int(t_final / dt)
    t = np.arange(n_steps) * dt
    theta = np.zeros(n_steps)
    omega = np.zeros(n_steps)
    theta[0], omega[0] = theta0, omega0
    for i in range(n_steps - 1):
        alpha = angular_acceleration(theta[i])
        omega[i + 1] = omega[i] + alpha * dt
        theta[i + 1] = theta[i] + omega[i + 1] * dt
    return t, theta, omega


def solve_velocity_verlet(theta0, omega0, t_final, dt):
    n_steps = int(t_final / dt)
    t = np.arange(n_steps) * dt
    theta = np.zeros(n_steps)
    omega = np.zeros(n_steps)
    theta[0], omega[0] = theta0, omega0
    for i in range(n_steps - 1):
        alpha = angular_acceleration(theta[i])
        theta[i + 1] = theta[i] + omega[i] * dt + 0.5 * alpha * dt**2
        alpha_new = angular_acceleration(theta[i + 1])
        omega[i + 1] = omega[i] + 0.5 * (alpha + alpha_new) * dt
    return t, theta, omega


# ========================================================================
# Exact energy contour
# ========================================================================


def exact_contour(E0, n_points=1000):
    """Compute the exact phase-space contour for energy E0.

    Returns arrays (theta_upper, omega_upper, theta_lower, omega_lower)
    for the top and bottom halves of the closed curve.
    """
    # theta range where omega^2 >= 0:  E0 + (g/L)cos(theta) >= 0
    theta = np.linspace(-np.pi, np.pi, n_points)
    omega_sq = 2.0 * (E0 + (G / LENGTH) * np.cos(theta))

    # Mask to valid region
    valid = omega_sq >= 0
    theta_valid = theta[valid]
    omega_upper = np.sqrt(omega_sq[valid])
    omega_lower = -omega_upper

    return theta_valid, omega_upper, omega_lower


def main():
    # --- Simulation parameters ---
    theta_initial = np.deg2rad(45)
    omega_initial = 0.0
    dt = 0.05
    t_symplectic = 500  # seconds for symplectic methods
    t_euler = 20        # shorter for Forward Euler (it blows up fast)

    E0 = total_energy(theta_initial, omega_initial)

    # --- Run integrators ---
    methods = {
        "Forward Euler": (solve_forward_euler, "red", 0.7, 0.8, t_euler),
        "Euler-Cromer": (solve_euler_cromer, "orange", 0.7, 0.8, t_symplectic),
        "Velocity Verlet": (solve_velocity_verlet, "green", 0.9, 1.0, t_symplectic),
    }

    results = {}
    for name, (solver, color, alpha, lw, t_run) in methods.items():
        print(f"Running {name} for {t_run}s...")
        t, theta, omega = solver(theta_initial, omega_initial, t_run, dt)
        results[name] = (t, theta, omega, color, alpha, lw)

    # --- Exact contour ---
    theta_exact, omega_upper, omega_lower = exact_contour(E0)

    # --- Plot ---
    fig, ax = plt.subplots(1, 1, figsize=(8, 7))
    fig_name = f"{Path(__file__).name} - Phase Space"
    fig.canvas.manager.set_window_title(fig_name)

    # Exact contour first (underneath everything)
    ax.plot(theta_exact, omega_upper, "k--", linewidth=2.0, label="Exact contour")
    ax.plot(theta_exact, omega_lower, "k--", linewidth=2.0)

    # Numerical trajectories — plot in order so Verlet is on top
    for name in methods:
        t, theta, omega, color, alpha, lw = results[name]
        ax.plot(theta, omega, color=color, linewidth=lw, alpha=alpha, label=name)

    # Clip axes to focus on the contour region
    pad = 0.3
    ax.set_xlim(theta_exact.min() - pad, theta_exact.max() + pad)
    ax.set_ylim(omega_lower.min() - 1.5, omega_upper.max() + 1.5)

    ax.set_title(
        f"Phase Space — dt={dt}s, "
        rf"$\theta_0$={np.rad2deg(theta_initial):.0f}°"
        f"   (Euler: {t_euler}s, others: {t_symplectic}s)",
        fontsize=13,
        fontweight="bold",
    )
    ax.set_xlabel(r"$\theta$ (rad)")
    ax.set_ylabel(r"$\omega$ (rad/s)")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)

    fig.tight_layout()

    # --- Print energy drift summary ---
    print(f"\nE0 = {E0:.6f}")
    print(f"{'Method':<22} {'t_run (s)':>10} {'Final E':>12} {'Drift':>12} {'Drift %':>10}")
    print("-" * 70)
    for name in methods:
        t, theta, omega, color, alpha, lw = results[name]
        E_final = total_energy(theta[-1], omega[-1])
        drift = E_final - E0
        drift_pct = 100 * drift / abs(E0)
        print(f"{name:<22} {t[-1]:>10.0f} {E_final:>12.6f} {drift:>+12.6f} {drift_pct:>+10.2f}%")

    plt.show()


if __name__ == "__main__":
    main()
