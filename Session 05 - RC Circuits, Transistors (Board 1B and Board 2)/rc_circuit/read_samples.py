# read_samples.py
# Lab: rc_circuit

import numpy as np
import serial
import adafruit_board_toolkit.circuitpython_serial

# Open the USB data port
cdc_data = adafruit_board_toolkit.circuitpython_serial.data_comports()[0]
ser = serial.Serial(None, 115200, 8, "N", 1, timeout=120)
ser.port = cdc_data.device
ser.open()
print("Lab: rc_circuit")


def usb_readline():
    return ser.readline().decode("utf-8").strip()


def usb_writeline(x):
    ser.write(bytes(str(x) + "\n", "utf-8"))
    ser.flush()


# Send MCU the command to (r)un the experiment
usb_writeline("r")
print("Reading samples")

# Read from MCU the number of samples
n = int(usb_readline())

# Declare numpy arrays to store the samples
times = np.zeros(n, float)
volts = np.zeros(n, float)

# Read from MCU the times and volts samples into arrays
for i in range(n):
    times[i] = int(usb_readline())
for i in range(n):
    volts[i] = int(usb_readline())
ser.close()
print(f"Received {n} time and volt samples...")

# Save samples to a CSV file
samples = np.column_stack((times, volts))
np.savetxt("samples.csv", samples, fmt="%3.6f", delimiter=",")
print('Saved file "samples.csv"')
