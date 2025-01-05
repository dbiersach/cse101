# read_samples.py
# Lab: count_by_countio

import adafruit_board_toolkit.circuitpython_serial
import serial

# Open the USB data port
cdc_data = adafruit_board_toolkit.circuitpython_serial.data_comports()[0]
ser = serial.Serial(None, 115200, 8, "N", 1, timeout=120)
ser.port = cdc_data.device
ser.open()
print("Lab: count_by_countio")


def usb_readline():
    return ser.readline().decode("utf-8").strip()


def usb_writeline(x):
    ser.write(bytes(str(x) + "\n", "utf-8"))
    ser.flush()


print("Reading samples for 10 seconds")
usb_writeline("r")
# Divide by 10 because we counted for 10 seconds
# Divide by 1,000,000 to convert to megahertz
count = float(usb_readline()) / 10 / 1e6
print(f"{count:.6f} Mhz")
