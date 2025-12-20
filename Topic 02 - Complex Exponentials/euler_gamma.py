"""euler_gamma.py"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import scipy.integrate


def factorial_recursive(n):
    # Base case
    if n == 0:
        return 1
    else:
        # Recursive case
        return int(n) * factorial_recursive(n - 1)


def f(x, s):
    """Integrand for the Gamma function: x^(s-1) * e^(-x)"""
    if x == 0 and s < 1:
        return 0
    return np.power(x, s - 1) * np.exp(-x)


def euler_gamma(s):
    """Compute Gamma(s) using numerical integration"""
    result, _ = scipy.integrate.quad(f, 0, np.inf, args=(s,))
    return result


def factorial_gamma(x):
    """Compute x! = Gamma(x+1)"""
    if np.isscalar(x):
        return np.round(euler_gamma(int(x) + 1), 5)
    return np.array([np.round(euler_gamma(xi + 1), 5) for xi in x])


def main(zoom=False):
    # Verify factorial calculation
    print(f"5! (recursive) = {factorial_recursive(5):,}")
    print(f"5! (gamma)     = {factorial_gamma(5):,}")

    # Plot Gamma function vs factorial
    xa = np.linspace(0, 5, 100)
    n = [factorial_recursive(i) for i in range(6)]

    plt.figure(Path(__file__).name)
    plt.plot(xa, factorial_gamma(xa), label=r"$\Gamma \left( x + 1 \right)$")
    plt.plot(range(len(n)), n, color="red", marker="o", linestyle="none", label="$n!$")
    plt.title(f"Factorial Via Euler's Gamma Function {'(zoomed)' if zoom else ''}")
    plt.xlabel("x")
    plt.ylabel("Factorial (x)")
    if not zoom:
        plt.xlim(0, 5.1)
    else:
        plt.xlim(0, 2.1)
        plt.ylim(0.5, 2.1)
    plt.legend(loc="upper left", framealpha=1.0, facecolor="white")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()
    main(zoom=True)
