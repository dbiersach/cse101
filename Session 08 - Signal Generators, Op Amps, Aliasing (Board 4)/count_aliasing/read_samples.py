# read_samples.py
# Lab: count_aliasing

from pathlib import Path

import adafruit_board_toolkit.circuitpython_serial
import numpy as np
import serial

# Open the USB data port
cdc_data = adafruit_board_toolkit.circuitpython_serial.data_comports()[0]
ser = serial.Serial(None, 115200, 8, "N", 1, timeout=120)
ser.port = cdc_data.device
ser.open()

# Read clock settings
file_name = "clock_settings.csv"
file_path = Path(__file__).parent / file_name
clock_settings = np.genfromtxt(file_name, delimiter=",")
num_samples = len(clock_settings)

print("Lab: count_aliasing")


def usb_readline():
    return ser.readline().decode("utf-8").strip()


def usb_writeline(x):
    ser.write(bytes(str(x) + "\n", "utf-8"))
    ser.flush()


# Create arrays to hold expected and measured frequencies
expected_mhz = np.zeros(num_samples, float)
measured_mhz = np.zeros(num_samples, float)

for n in range(num_samples):
    pll_multiplier = int(clock_settings[n, 0])
    clock_divider = int(clock_settings[n, 1])
    freq_mhz = pll_multiplier * 25 / clock_divider
    print(f"Counting pulses at {freq_mhz:3.2f} MHz")
    # Send this run's parameters to the MCU
    params = f"{pll_multiplier},{clock_divider}"
    usb_writeline(params)
    # Wait for the MCU to respond with the measured counts
    counts = int(usb_readline())
    # Calculate the measured clock frequency
    expected_mhz[n] = freq_mhz
    measured_mhz[n] = counts / 1e6  # Convert to MHz

# Save samples to a CSV file
samples = np.column_stack((expected_mhz, measured_mhz))
file_name = "samples.csv"
file_path = Path(__file__).parent / file_name
np.savetxt(file_path, samples, fmt="%3.2f", delimiter=",")
print('Saved file "samples.csv"')
