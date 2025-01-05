# read_samples.py
# Lab: signal_gen.py

from pathlib import Path

import adafruit_board_toolkit.circuitpython_serial
import numpy as np
import serial

# Open the USB data port
cdc_data = adafruit_board_toolkit.circuitpython_serial.data_comports()[0]
ser = serial.Serial(None, 115200, 8, "N", 1, timeout=120)
ser.port = cdc_data.device
ser.open()
print("Lab: signal_gen")


def usb_readline():
    return ser.readline().decode("utf-8").strip()


def usb_writeline(x):
    ser.write(bytes(str(x) + "\n", "utf-8"))
    ser.flush()


# Send to MCU the command to (r)un the experiment
usb_writeline("r")
print("Reading samples")

# Read times and volts samples from MCU into arrays
n = int(usb_readline())
times = np.zeros(n, float)
volts = np.zeros(n, float)
for i in range(n):
    times[i] = float(usb_readline())
for i in range(n):
    volts[i] = float(usb_readline())
ser.close()
print(f"Received {n} time and volt samples...")

# Save samples to a CSV file
samples = np.column_stack((times, volts))
file_name = "samples.csv"
file_path = Path(__file__).parent / file_name
np.savetxt("samples.csv", samples, fmt="%3.6f", delimiter=",")
print('Saved file "samples.csv"')
