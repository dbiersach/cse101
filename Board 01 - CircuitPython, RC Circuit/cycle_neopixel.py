# cycle_neopixel.py
# Cycle NeoPixel through colors

# Uses (1) Adafruit NeoPixel
# https://www.adafruit.com/product/1558

import time

import board
import neopixel

# Initialize Adafruit NeoPixel object
pixel = neopixel.NeoPixel(board.GP22, 1, brightness=0.25)

# Turn off the NeoPixel off (set its color to BLACK)
pixel[0] = (0, 0, 0)

# Set display time (in seconds) for each color
time_delay = 2  # Seconds

while True:
    pixel[0] = (255, 0, 0)  # RGB triplet for pure RED
    time.sleep(time_delay)
    pixel[0] = (0, 255, 0)  # RGB triplet for pure GREEN
    time.sleep(time_delay)
    pixel[0] = (0, 0, 255)  # RGB triplet for pure BLUE
    time.sleep(time_delay)
