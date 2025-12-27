# button_debounce.py
# Cycle NeoPixel through colors on button press

# Uses (1) Adafruit NeoPixel
# Uses (1) Adafruit Colorful Tactile Button Switch
# https://www.adafruit.com/product/1010

import board
import digitalio
import neopixel
from adafruit_debouncer import Debouncer

# Initialize Adafruit NeoPixel object
pixel = neopixel.NeoPixel(board.GP22, 1, brightness=0.25)

# Turn off the NeoPixel off (set its color to BLACK/OFF)
pixel[0] = (0, 0, 0)

# Initialize GPIO pin for INPUT
pin_button = digitalio.DigitalInOut(board.GP20)
pin_button.pull = digitalio.Pull.UP

# Initialize Adafruit Debouncer object
switch = Debouncer(pin_button, interval=0.05)

# Define the color tuples for RED, GREEN, BLUE, and BLACK/OFF
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 0, 0)]

push_count = 0

while True:
    switch.update()
    if switch.fell:
        # Set the neopixel color using push_count as an index into colors list
        pixel[0] = colors[push_count]
        # Increment the push_count but remain within interval [0, 3]
        push_count = (push_count + 1) % 4
