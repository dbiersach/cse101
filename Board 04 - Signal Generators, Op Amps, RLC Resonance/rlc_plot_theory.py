# rlc_plot_theory.py
# Plot theoretical frequency response of driven RLC circuit

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import AutoMinorLocator, FormatStrFormatter


def calc_rms(w):
    Emf = 1.1  # Potential in Volts (mean in op_amp.py plot)
    R1, R2 = 10.2, 99.5  # Resistance in Ohms
    R = R1 + R2  # Total Resistance in Ohms

    L = 101.6e-3  # Inductance in Henries (mH to H)
    C = 93.7e-9  # Capacitance in Farads (nF to F)

    Q = C * Emf  # Initial capacitor charge
    I = 0.0  # Initial capacitor current is zero
    V = 0.0  # Initial capacitor voltage is zero

    t = 0.0
    tf = 1.0  # End time in seconds
    dt = 0.00001
    n = (tf - t) / dt  # Number of intervals

    while t < tf:  # Simulate circuit
        alpha = (Emf * np.sin(w * t) - I * R - Q / C) / L
        I = I + alpha * dt
        Q = Q + I * dt
        V = V + (I * R1) ** 2  # Voltage through R1
        t = t + dt

    return np.sqrt(V / n)  # RMS value


def main():
    # Load measured (actual) volts from the RLC circuit
    file_name = file_name = "rlc_resonance.csv"
    file_path = Path(__file__).parent / file_name
    freq, volts_actual = np.genfromtxt(file_path, delimiter=",", unpack=True)

    # Calculate theoretical voltage at the measured (actual) frequencies
    omega = freq * (2 * np.pi * 1000)  # Covert kHz to rad/s
    volts_theory = calc_rms(omega) * 3.18  # Due to TLV2462 Op Amp gain

    # Resonant frequency is at the peak voltage
    max_volt_actual = np.max(volts_actual)
    resonance_freq_actual = freq[np.argmax(volts_actual)]
    print(f"Actual Resonance voltage = {max_volt_actual:0.4f} V")
    print(f"Actual Resonance freq = {resonance_freq_actual:0.4f} kHz")
    print()
    max_volt_theory = np.max(volts_theory)
    resonance_freq_theory = freq[np.argmax(volts_theory)]
    print(f"Theoretical Resonance voltage = {max_volt_theory:0.4f} V")
    print(f"Theoretical Resonance freq = {resonance_freq_theory:0.4f} kHz")

    # Create a plot window
    plt.figure(Path(__file__).name)
    plt.gca().set_facecolor("black")
    plt.scatter(freq, volts_actual, color="magenta", s=1, label="Actual")
    plt.plot(freq, volts_theory, color="green", lw=2, label="Theory")
    plt.vlines(resonance_freq_theory, 0, max_volt_theory, color="yellow", lw=2)
    plt.title("RLC Circuit Resonance (Theory vs. Actual)")
    plt.xlabel("Frequency (kHz)")
    plt.ylabel("Voltage (V)")
    plt.xlim(0, 5)  # 0 to 5 kHz
    plt.ylim(0, 0.3)  # 0 to 0.3 Volts
    plt.gca().xaxis.set_minor_locator(AutoMinorLocator())
    plt.gca().xaxis.set_major_formatter(FormatStrFormatter("%0.3f"))
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
