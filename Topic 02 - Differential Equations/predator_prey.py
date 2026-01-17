#!/usr/bin/env uv run
"""predator_prey.py"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from scipy.integrate import solve_ivp


def model(time, state_vector, alpha, beta, delta, gamma):
    pred, prey = state_vector
    d_prey = alpha * prey - beta * prey * pred
    d_pred = delta * prey * pred - gamma * pred
    return d_pred, d_prey


def main():
    final_time = 20  # months

    alpha = 2.0  # Prey birth rate
    beta = 1.1  # Prey death rate
    delta = 1.0  # Pred birth rate
    gamma = 0.9  # Pred death rate

    # Initial percentage of each species' population
    pred_0 = 0.5  # Predator population starts at 50%
    prey_0 = 1.0  # Prey population starts at 100%

    sol = solve_ivp(
        model,
        (0, final_time),  # tuple of time span
        [pred_0, prey_0],  # initial state vector
        max_step=final_time / 1000,  # maximum time step
        args=(alpha, beta, delta, gamma),  # tuple of constants used in ODE
    )

    # Retrieve results of the solution
    t = sol.t
    pred, prey = sol.y * 100  # Convert to %

    plt.figure(Path(__file__).name)
    plt.plot(t, pred, label="predator", color="red", linewidth=2)
    plt.plot(t, prey, label="prey", color="blue", linewidth=2)
    plt.title("Predator-Prey Model (Lotka-Volterra)")
    plt.xlabel("Time (months)")
    plt.ylabel("Population Percentage")
    ax = plt.gca()
    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(50))
    ax.yaxis.set_minor_locator(MultipleLocator(10))
    ax.legend(loc="upper right", framealpha=1.0, facecolor="white")
    plt.show()


if __name__ == "__main__":
    main()
