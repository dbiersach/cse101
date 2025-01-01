# code.py for Raspberry Pi Pico 2
# Lab: rc_circuit
# Voltage across charging and discharging resistor-capacitor circuit

# Uses (1) 10K ohm resistor (1/2 watt, 1% tolerance)
# Uses (1) 10uF 25V electrolytic capacitor (20% tolerance)

import analogio
import board
import digitalio
import time
import supervisor
import usb_cdc

# Wait until USB console port is ready
while not supervisor.runtime.usb_connected:
    pass
print("Lab: rc_circuit")

# Create USB data port
ser = usb_cdc.data

# Configure pins
pin_adc = analogio.AnalogIn(board.A1)
pin_charge = digitalio.DigitalInOut(board.GP22)
pin_charge.direction = digitalio.Direction.OUTPUT


def usb_readline():
    return ser.readline().decode("utf-8").strip()


def usb_writeline(x):
    ser.write(bytes(str(x) + "\n", "utf-8"))
    ser.flush()


def read_samples():
    # Set number of samples (NOT number of seconds!)
    n1 = 1000
    n2 = n1 * 2
    volts = [int] * n2
    times = [int] * n2
    
    print("Reading samples")

    # Drain circuit (discharge capacitor)
    pin_charge.value = False
    time.sleep(5)

    # Energize circuit (charge capacitor)    
    pin_charge.value = True
    for i in range(n1):
        volts[i] = pin_adc.value
        times[i] = time.monotonic_ns()
        time.sleep(0.001)

    # Drain circuit (discharge capacitor)
    pin_charge.value = False
    for i in range(n1, n2):
        volts[i] = pin_adc.value
        times[i] = time.monotonic_ns()
        time.sleep(0.001)

    # Send number of samples
    print("Sending samples")
    usb_writeline(n2)  # number of samples
    for val in times:
        usb_writeline(val)  # times array
    for val in volts:
        usb_writeline(val)  # volts array


while True:
    print("Waiting")
    cmd = usb_readline()
    if cmd == "r":
        read_samples()
