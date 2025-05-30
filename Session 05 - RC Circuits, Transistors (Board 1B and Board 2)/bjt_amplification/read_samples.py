# read_samples.py
# Lab: bjt_amplification

import adafruit_board_toolkit.circuitpython_serial
import numpy as np
import serial

# Open the USB data port
cdc_data = adafruit_board_toolkit.circuitpython_serial.data_comports()[0]
ser = serial.Serial(None, 115200, 8, "N", 1, timeout=120)
ser.port = cdc_data.device
ser.open()
print("Lab: bjt_amplification")


def usb_readline():
    return ser.readline().decode("utf-8").strip()


def usb_writeline(x):
    ser.write(bytes(str(x) + "\n", "utf-8"))
    ser.flush()


# Send MCU the command to (r)un the experiment
usb_writeline("r")
print("Reading samples")

# Read samples from USB into arrays
n = int(usb_readline())
volts_be = np.zeros(n, float)
volts_ce = np.zeros(n, float)
for i in range(n):
    volts_be[i] = float(usb_readline())
for i in range(n):
    volts_ce[i] = float(usb_readline())
ser.close()
print(f"Received {n} BE volt and CE volt samples")

# Save samples to a CSV file
samples = np.column_stack((volts_be, volts_ce))
np.savetxt("samples.csv", samples, fmt="%3.6f", delimiter=",")
print('Saved file "samples.csv"')
