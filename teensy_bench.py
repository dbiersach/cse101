#!/usr/bin/env -S uv run

import time

import matplotlib.pyplot as plt
import numpy as np
import serial
import serial.tools.list_ports
from matplotlib.ticker import AutoMinorLocator


def send_cmd(ser, cmd):
    """Send a command, then give Teensy time to process."""
    ser.write(f"{cmd}\n".encode())
    ser.flush()
    time.sleep(0.5)


def read_exact(ser, n):
    """Read exactly n bytes from serial, raising on timeout."""
    data = bytearray()
    while len(data) < n:
        chunk = ser.read(n - len(data))
        if not chunk:
            raise TimeoutError(f"Expected {n:,} bytes but only received {len(data):,}")
        data.extend(chunk)
    return data


def capture_adc(ser):
    # Drain any leftover bytes from previous commands
    ser.reset_input_buffer()

    # Send command to Teensy
    ser.write(b"adc\n")
    ser.flush()

    # Read the raw binary data (131070 bytes = 65535 × 2)
    raw = read_exact(ser, 131_070)
    samples = np.frombuffer(raw, dtype=np.uint16)

    # Convert to volts (12-bit ADC, 3.3 V reference)
    volts = samples.astype(np.float32) * (3.3 / 4095.0)

    # Uniform time axis from known sample rate (800 kSPS)
    dt_us = 1e6 / 800_000
    time_ms = np.arange(65535) * (dt_us / 1000.0)

    return volts, time_ms


def plot_capture(volts, time_ms):
    """Plot ~10 cycles in time domain (based on dominant FFT tone) + full FFT."""
    SPS = 800_000  # Hz (Teensy ADC sample rate)
    N = len(volts)

    v = volts.astype(np.float64)

    # FFT on full capture
    fft_mag = np.abs(np.fft.rfft(v)) * 2.0 / N
    freqs = np.fft.rfftfreq(N, d=1.0 / SPS)

    # Dominant tone bin (ignore DC)
    k = int(np.argmax(fft_mag[1:])) + 1

    # Refine peak via parabolic interpolation on *log* magnitude
    # delta is fractional-bin offset in [-0.5, 0.5] for well-behaved peaks
    y1 = np.log(fft_mag[k - 1] + 1e-30)
    y2 = np.log(fft_mag[k] + 1e-30)
    y3 = np.log(fft_mag[k + 1] + 1e-30)
    delta = 0.5 * (y1 - y3) / (y1 - 2.0 * y2 + y3)

    # Refined frequency estimate
    k_refined = k + float(delta)
    dominant_freq = k_refined * (SPS / N)  # Hz

    # Time-domain window: at least 10 cycles of the dominant tone
    samples_needed = int(np.ceil(10.0 * SPS / dominant_freq))
    end_idx = min(N, samples_needed)

    volts_win = volts[:end_idx]
    time_win = time_ms[:end_idx]

    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # Time domain (top)
    ax1.plot(time_win, volts_win, linewidth=0.6)
    ax1.set_xlabel("Time (ms)")
    ax1.set_ylabel("Voltage (V)")
    ax1.set_title(
        f"ADC Capture (800 kSPS) - Dominant Tone: {dominant_freq / 1000:.3f} kHz"
    )
    ax1.set_ylim(0.0, 3.3)
    ax1.grid(True, alpha=0.3)

    # Frequency domain (bottom)
    ax2.plot(freqs / 1000.0, 20 * np.log10(fft_mag + 1e-12), linewidth=0.6)
    ax2.set_xlabel("Frequency (kHz)")
    ax2.set_ylabel("Magnitude (dB)")
    ax2.set_title("Frequency Spectrum")
    ax2.grid(True, alpha=0.3)

    # Zoom logic (start checking at <= 50 kHz)
    if dominant_freq <= 50_000:
        fmax = 50_000
    elif dominant_freq <= 100_000:
        fmax = 100_000
    else:
        fmax = 200_000
    ax2.set_xlim(0, fmax / 1000.0)

    # Minor ticks: 3 minor ticks per major interval on the frequency axis
    ax2.xaxis.set_minor_locator(AutoMinorLocator(4))
    ax2.grid(True, which="minor", alpha=0.15)

    plt.tight_layout()
    plt.show()


def oscilloscope(ser):
    send_cmd(ser, "neo 255 0 0 ")
    # 800_000 / 65535 ≈ 12.207 kHz (FFT bin center frequency)
    # send_cmd(ser, "sig sine 12207")
    # send_cmd(ser, "sig sine 35246")
    send_cmd(ser, "sig sine 10000")
    volts, time_ms = capture_adc(ser)
    plot_capture(volts, time_ms)
    send_cmd(ser, "neo 0 0 0")


def main():
    """Find the serial port for a connected Teensy."""
    port = None
    for p in serial.tools.list_ports.comports():
        if p.vid == 0x16C0:
            port = p
            break
    if port is None:
        print("No Teensy found. Please connect one and try again.")
        return

    ser = serial.Serial(port.device, timeout=5)
    oscilloscope(ser)


if __name__ == "__main__":
    main()
