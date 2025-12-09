# wave_generator.py
# Measure sine wave frequency and amplitude

# Uses (1) AITRIP AD9833 Signal Generator
# Uses (1) Adafruit TLV2462 Op Amp
# Uses (1) 10K Ohm and (1) 22K Ohm Resistor

import analogio
import board
import busio
import digitalio
import time

from ad9833_blinka import AD9833

# Configure analog input pin (FROM the AD9833)
pin_adc = analogio.AnalogIn(board.ADC1)

# Configure chip select (FSYNC on AD9833) on GP22
pin_cs = digitalio.DigitalInOut(board.GP22)
pin_cs.switch_to_output(value=True)  # idle high (not selected)

# Create SPI (MISO not used by AD9833)
spi_bus = busio.SPI(board.GP18, MOSI=board.GP19, MISO=None)

# Create AD9833 Signal Generator
wave_gen = AD9833(spi_bus, pin_cs)
wave_gen.reset()

print("Generating 800 Hz tone")
wave_gen.frequency = 800

for _ in range(3):
    print("Square wave...")
    wave_gen.waveform = "square"
    time.sleep(3.0)

    print("Sine wave...")
    wave_gen.waveform = "sine"
    time.sleep(3.0)

# Disable tone
wave_gen.frequency = 0
