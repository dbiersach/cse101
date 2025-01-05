# code.py for Raspberry Pi Pico 2
# Lab: omp_amp
# Measure sine wave frequency and amplitude

# Uses (1) AITRIP AD9833 Signal Generator
# Uses (1) Adafruit TLV2462 Op Amp
# Uses (1) 10K Ohm and (1) 22K Ohm Resistor

import time

import ad9833
import analogio
import board
import supervisor
import usb_cdc

# Wait until USB console port is ready
while not supervisor.runtime.usb_connected:
    pass
print("Lab: omp_amp")

# Create USB data port
ser = usb_cdc.data

# Configure analog input pin (from AD9833)
pin_adc = analogio.AnalogIn(board.A1)

# Configure AITRIP AD9833 Signal Generator
wave_gen = ad9833.AD9833(select="GP22")  # CS/FSYNC
wave_gen.reset()
wave_gen.update_freq(10)  # Hz
wave_gen.start()


def usb_writeline(usb_data_port, x):
    usb_data_port.write(bytes(str(x) + "\n", "utf-8"))
    usb_data_port.flush()


def read_samples():
    # Set number of samples (NOT number of seconds!)
    n = 2000
    volts = [int] * n
    times = [int] * n

    # Read voltage samples
    print("Reading samples")
    wave_gen.reset()
    wave_gen.update_freq(10)  # Hz
    wave_gen.start()
    for i in range(n):
        times[i] = time.monotonic_ns()
        volts[i] = pin_adc.value
        time.sleep(0.001)

    # Transfer data over USB data port
    print("Sending samples")
    usb_writeline(ser, n)  # number of samples
    for val in times:
        usb_writeline(ser, val)  # times array
    for val in volts:
        usb_writeline(ser, val)  # volts array


while True:
    print("Waiting")
    cmd = ser.readline().strip().decode("utf-8")
    if cmd == "r":
        read_samples()
