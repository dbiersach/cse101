# rc_filter.py
# Simulation of passive RC filter from 10 Hz to 1 MHz
# Demonstrates low-pass and high-pass frequency response

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

# Circuit parameters
V_s = 3.0  # Source voltage amplitude (V)
R = 10_000  # Resistance (Ohms) - 10kΩ
C = 10e-9  # Capacitance (Farads) - 10nF
tau = R * C  # Time constant
f_c = 1 / (2 * np.pi * tau)  # Cutoff frequency (Hz)

print(f"R = {R:,} Ω")
print(f"C = {C * 1e9:.1f} nF")
print(f"τ = RC = {tau * 1e6:.2f} µs")
print(f"Cutoff frequency f_c = {f_c:.1f} Hz")

# Frequency sweep parameters (log scale from 10 Hz to 1 MHz)
frequencies = np.logspace(1, 6, 100)  # 10 Hz to 1 MHz, 100 points

# Calculate theoretical response (magnitude) - a ratio of voltages (V_out / V_in)
lp_theory = 1 / np.sqrt(1 + (frequencies / f_c) ** 2)
hp_theory = (frequencies / f_c) / np.sqrt(1 + (frequencies / f_c) ** 2)

# Convert voltage ratios to dB
lp_db = 20 * np.log10(lp_theory)
hp_db = 20 * np.log10(hp_theory)

# Plot 1: Bode plot (frequency response in dB)
fig1, ax1 = plt.subplots(figsize=(10, 6), num="RC Filter Frequency Response (Bode)")
ax1.set_facecolor("black")
fig1.patch.set_facecolor("#1a1a1a")  # dark gray background
ax1.semilogx(frequencies, lp_db, color="magenta", linewidth=2.5, label="Low-pass")
ax1.semilogx(frequencies, hp_db, color="lime", linewidth=2.5, label="High-pass")
# Mark cutoff frequency (-3 dB point)
ax1.axvline(f_c, color="white", linestyle=":", alpha=0.7, linewidth=1.5)
ax1.axhline(-3, color="white", linestyle=":", alpha=0.5, linewidth=1)
ax1.annotate(
    f"f_c = {f_c:.0f} Hz\n(-3 dB)",
    xy=(f_c, -3),
    xytext=(f_c * 3, -8),
    color="white",
    fontsize=10,
    arrowprops={"arrowstyle": "->", "color": "white", "alpha": 0.7},
)
ax1.set_xlabel("Frequency (Hz)", color="white", fontsize=12)
ax1.set_ylabel("Gain (dB)", color="white", fontsize=12)
ax1.set_title("RC Filter Frequency Response", color="white", fontsize=14)
ax1.legend(loc="lower left", facecolor="#333333", edgecolor="white", labelcolor="white")
ax1.set_xlim(10, 1e6)
ax1.set_ylim(-40, 5)
ax1.tick_params(colors="white")
ax1.grid(True, which="both", color="gray", linestyle="dotted", alpha=0.4)
for spine in ax1.spines.values():
    spine.set_color("white")

# Plot 2: Time-domain waveforms at three frequencies (using Runge-Kutta integration)
fig2, axes = plt.subplots(3, 1, figsize=(10, 9), num="RC Filter Time-Domain Response")
fig2.patch.set_facecolor("#1a1a1a")

# Frequencies to test
test_freqs = [100, f_c, 100_000]  # Below, at, and above cutoff in Hz
freq_labels = ["100 Hz (below f_c)", f"{f_c:.0f} Hz (at f_c)", "100 kHz (above f_c)"]

for idx, (freq, label) in enumerate(zip(test_freqs, freq_labels)):
    # Simulation parameters
    n_cycles = 100  # Number of cycles to simulate to ensure steady-state
    n_timesteps = 500  # Number of time steps per cycle

    period = 1 / freq  # At 100 Hz, period = 1/100 = 0.01 seconds (10 ms per cycle)
    dt = period / n_timesteps  # dt = 0.01/500 = 0.00002 seconds (20 µs per sample)

    # Total samples = 100 * 500 = 50,000 samples
    n_samples = int(n_cycles * period / dt)

    # Arrays for storing results
    t = np.zeros(n_samples)
    v_in = np.zeros(n_samples)
    v_lp = np.zeros(n_samples)
    v_hp = np.zeros(n_samples)

    # Initial condition: capacitor starts discharged
    v_cap = 0.0

    # Define the derivative function for RK4: dV_cap/dt = (V_in - V_cap) / (R * C)
    def dv_cap_dt(v_cap_val, v_in_val):
        return (v_in_val - v_cap_val) / (R * C)

    # 4th-order Runge-Kutta integration
    for i in range(n_samples):
        t[i] = i * dt
        # Input: DC signal swinging 0 to V_s (not true AC)
        # Sine wave normal range is -1 to 1, so scale and shift it
        v_in[i] = (V_s / 2) * (1 + np.sin(2 * np.pi * freq * t[i]))

        # Store current capacitor voltage
        v_lp[i] = v_cap
        # High-pass = voltage across resistor (Kirchhoff's voltage law)
        v_hp[i] = v_in[i] - v_cap

        # RK4 integration for next step
        if i < n_samples - 1:
            t_next = (i + 1) * dt
            v_in_next = (V_s / 2) * (1 + np.sin(2 * np.pi * freq * t_next))
            v_in_mid = (V_s / 2) * (1 + np.sin(2 * np.pi * freq * (t[i] + dt / 2)))

            k1 = dv_cap_dt(v_cap, v_in[i])
            k2 = dv_cap_dt(v_cap + k1 * dt / 2, v_in_mid)
            k3 = dv_cap_dt(v_cap + k2 * dt / 2, v_in_mid)
            k4 = dv_cap_dt(v_cap + k3 * dt, v_in_next)

            v_cap += (dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)

    # Only plot the last 4 cycles (steady state)
    samples_per_cycle = int(period / dt)
    plot_start = n_samples - 4 * samples_per_cycle
    t_plot = t[plot_start:] - t[plot_start]
    v_in_plot = v_in[plot_start:]
    v_lp_plot = v_lp[plot_start:]
    v_hp_plot = v_hp[plot_start:]

    # Plot waveforms
    ax = axes[idx]
    ax.set_facecolor("black")

    times = t_plot * 1000  # Convert to ms
    ax.plot(times, v_in_plot, color="yellow", linewidth=2, label="Input")
    ax.plot(times, v_lp_plot, color="white", linewidth=2, label="Low-pass (V_cap)")
    ax.plot(times, v_hp_plot, color="fuchsia", linewidth=2, label="High-pass (V_R)")
    ax.set_ylabel("Voltage (V)", color="white", fontsize=10)
    ax.set_title(f"f = {label}", color="white", fontsize=11)
    ax.legend(
        loc="upper right",
        facecolor="#333333",
        edgecolor="white",
        labelcolor="white",
        fontsize=9,
    )
    ax.set_ylim(-2, 3.5)
    ax.tick_params(colors="white")
    ax.grid(True, color="gray", linestyle="dotted", alpha=0.4)
    ax.yaxis.set_major_locator(MultipleLocator(0.5))
    for spine in ax.spines.values():
        spine.set_color("white")

axes[-1].set_xlabel("Time (ms)", color="white", fontsize=12)
fig2.tight_layout()

# Print gain values at cutoff frequency
print(f"At f_c = {f_c:.0f} Hz:")
print(f"  Low-pass gain:  {lp_db[np.argmin(np.abs(frequencies - f_c))]:.2f} dB")
print(f"  High-pass gain: {hp_db[np.argmin(np.abs(frequencies - f_c))]:.2f} dB")

plt.show()
