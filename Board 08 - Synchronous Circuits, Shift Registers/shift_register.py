# shift_register.py
# Control 8 LEDs using a 74HC595 Shift Register

# Uses (1) 74HC595 Shift Register
# Uses (1) LTA-1000G 10-LED strip
# Uses (8) 220 Ω resistors

import time

import board
import digitalio

# Define GPIO pins
data_pin = digitalio.DigitalInOut(board.GP20)  # SER/DS pin
latch_pin = digitalio.DigitalInOut(board.GP21)  # RCLK pin
clock_pin = digitalio.DigitalInOut(board.GP22)  # SRCLK pin

# Set pins as outputs
data_pin.direction = digitalio.Direction.OUTPUT
latch_pin.direction = digitalio.Direction.OUTPUT
clock_pin.direction = digitalio.Direction.OUTPUT

# Initialize pins low
data_pin.value = False
clock_pin.value = False
latch_pin.value = False


def shift_out(data_byte):
    """Shift out 8 bits to the 74HC595, MSB first"""
    for i in range(7, -1, -1):
        # Set data pin to current bit value
        data_pin.value = (data_byte >> i) & 1
        # Pulse clock to shift bit into register
        clock_pin.value = True
        clock_pin.value = False


def latch_data():
    """Transfer shift register contents to output latches"""
    latch_pin.value = True
    latch_pin.value = False


def main():
    print("Press Ctrl-C to exit...")
    try:
        while True:
            shift_out(0b10011001)  # 0x99 in hex, 153 in decimal
            latch_data()  # this updates the LEDs
            time.sleep(1)

            shift_out(0b01100110)  # 0x66 in hex, 102 in decimal
            latch_data()
            time.sleep(1)

    except KeyboardInterrupt:
        # Clean up: turn off all LEDs before exiting
        shift_out(0b00000000)
        latch_data()
        print("All LEDs now OFF, program exiting...")


if __name__ == "__main__":
    main()
