# read_samples.py
# Lab: ohms_law

from pathlib import Path

import adafruit_board_toolkit.circuitpython_serial
import numpy as np
import serial

# Open the USB data port
cdc_data = adafruit_board_toolkit.circuitpython_serial.data_comports()[0]
ser = serial.Serial(None, 115200, 8, "N", 1, timeout=120)
ser.port = cdc_data.device
ser.open()
print("Lab: ohms_law")


def usb_readline():
    return ser.readline().decode("utf-8").strip()


def usb_writeline(x):
    ser.write(bytes(str(x) + "\n", "utf-8"))
    ser.flush()


# Query the user for the resistor number to be measured
while True:
    try:
        resistor_num = int(input("Resistor # (1, 2, or 3)? "))
        if 1 <= resistor_num <= 3:
            break
        else:
            print("Please enter an integer between 1 and 3 inclusive.")
    except ValueError:
        print("That is not a valid integer. Please try again.")

# Send MCU the command to (r)un the experiment
usb_writeline("r")
print("Reading samples")

# Read volts and amps samples from USB into arrays
n = int(usb_readline())
volts = np.zeros(n, float)
amps = np.zeros(n, float)
for i in range(n):
    volts[i] = float(usb_readline())
for i in range(n):
    amps[i] = float(usb_readline())
ser.close()
print(f"Received {n} volt and amp samples")

# Save samples to a CSV file
samples = np.column_stack((volts, amps))
file_name = f"resistor{resistor_num:n}.csv"
file_path = Path(__file__).parent / file_name
np.savetxt(file_path, samples, fmt="%3.6f", delimiter=",")
print(f'Saved file "{file_name}"')
