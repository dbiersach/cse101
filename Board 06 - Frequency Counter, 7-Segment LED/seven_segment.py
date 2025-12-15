# seven_segment.py
# Display digits 0-9 on a 7-segment LED display

# Uses (1) 330 Ohm Resistor
# Uses (1) Seven-Segment LED Display (Common Cathode)

import time

import board
import digitalio

# Define GPIO pins for each segment of the 7-segment display
segments = {
    "A": digitalio.DigitalInOut(board.GP20),  # Top
    "B": digitalio.DigitalInOut(board.GP19),  # Top Right
    "C": digitalio.DigitalInOut(board.GP16),  # Bottom Right
    "D": digitalio.DigitalInOut(board.GP17),  # Bottom
    "E": digitalio.DigitalInOut(board.GP18),  # Bottom Left
    "F": digitalio.DigitalInOut(board.GP21),  # Top Left
    "G": digitalio.DigitalInOut(board.GP22),  # Middle
}

# Set all GPIO pins as outputs
for pin in segments.values():
    pin.direction = digitalio.Direction.OUTPUT

# Define which segments to light up for each digit
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
        # Loop through digits 0-9
        for n in range(10):
            # Turn off all segments
            for pin in segments.values():
                pin.value = False

            print(f"Displaying digit: {n}")

            # Turn on the required segments for the current digit
            for c in digits[n]:
                pin = segments[c]
                pin.value = True

            time.sleep(3)

except KeyboardInterrupt:
    # Turn off all segments before exiting
    for pin in segments.values():
        pin.value = False
    print("Display stopped.")
