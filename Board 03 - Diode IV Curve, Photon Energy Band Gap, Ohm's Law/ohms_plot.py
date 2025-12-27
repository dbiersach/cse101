# ohms_plot.py


from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator


def fit_linear(x, y):
    m = len(x) * np.sum(x * y) - np.sum(x) * np.sum(y)
    m = m / (len(x) * np.sum(x**2) - np.sum(x) ** 2)
    b = (np.sum(y) - m * np.sum(x)) / len(x)
    return m, b


def read_samples(file_name):
    file_path = Path(__file__).parent / file_name
    col1, col2 = np.genfromtxt(file_path, delimiter=",", unpack=True)
    return col1, col2


def main():
    # Read in the sample data files
    volts1, amps1 = read_samples("resistor1.csv")
    volts2, amps2 = read_samples("resistor2.csv")
    volts3, amps3 = read_samples("resistor3.csv")

    # Find the line of best fit y = mx + b
    # where m = slope and b = y-intercept
    m1, b1 = fit_linear(volts1, amps1)
    m2, b2 = fit_linear(volts2, amps2)
    m3, b3 = fit_linear(volts3, amps3)

    # Calculate resistance at 2.0V using Ohms Law: R = V / I
    v = 2.0
    ohm1 = v / (m1 * v + b1) * 1000
    ohm2 = v / (m2 * v + b2) * 1000
    ohm3 = v / (m3 * v + b3) * 1000

    # Plot the graph on the main axes
    plt.figure(Path(__file__).name)
    plt.gca().set_facecolor("black")
    plt.scatter(volts1, amps1)
    plt.scatter(volts2, amps2)
    plt.scatter(volts3, amps3)
    x = np.linspace(volts1[0], volts1[-1], 100)
    plt.plot(x, m1 * x + b1, label=f"Resistor 1 - {ohm1:.0f} Ohm")
    plt.plot(x, m2 * x + b2, label=f"Resistor 2 - {ohm2:.0f} Ohm")
    plt.plot(x, m3 * x + b3, label=f"Resistor 3 - {ohm3:.0f} Ohm")
    plt.title("Ohm's Law")
    plt.xlabel("Voltage (V)")
    plt.ylabel("Current (mA)")
    plt.axvline(x=v, color="white")
    plt.gca().yaxis.set_major_locator(MultipleLocator(5.0))
    plt.grid(which="both", color="lightgray", linestyle="dotted", alpha=0.5)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
