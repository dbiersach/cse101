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

while True:
    pixel[0] = (255, 0, 0)  # RGB triplet for pure RED
    time.sleep(1)
    pixel[0] = (0, 255, 0)  # RGB triplet for pure GREEN
    time.sleep(1)
    pixel[0] = (0, 0, 255)  # RGB triplet for pure BLUE
    time.sleep(1)
