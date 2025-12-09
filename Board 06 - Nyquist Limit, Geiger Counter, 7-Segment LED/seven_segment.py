# seven_segment.py
# Blink external RED LED on and off

# Uses (1) 330 Ohm Resistor
# Uses (1) RED LED (660 nm Wavelength, 1.85V, 20mA)

import time

import board
import digitalio


segments = {
    "A": digitalio.DigitalInOut(board.GP20),  # Top
    "B": digitalio.DigitalInOut(board.GP19),  # Top Right
    "C": digitalio.DigitalInOut(board.GP16),  # Bottom Right
    "D": digitalio.DigitalInOut(board.GP17),  # Bottom
    "E": digitalio.DigitalInOut(board.GP18),  # Bottom Left
    "F": digitalio.DigitalInOut(board.GP21),  # Top Left
    "G": digitalio.DigitalInOut(board.GP22),  # Middle
}

for pin in segments.values():
    pin.direction = digitalio.Direction.OUTPUT

digits = {
    0: "ABCDEF",
    1: "BC",
    2: "ABGED",
    3: "ABGCD",
    4: "FGBC",
    5: "AFGCD",
    6: "AFGECD",
    7: "ABC",
    8: "AFBGECD",
    9: "AFBGC",
}

print("Displaying digits. Press Ctrl+C to stop.")
try:
    while True:
        for n in range(10):
            for pin in segments.values():
                pin.value = False

            print(f"Displaying digit: {n}")

            for c in digits[n]:
                pin = segments[c]
                pin.value = True

            time.sleep(3)

except KeyboardInterrupt:
    print("Display stopped.")
