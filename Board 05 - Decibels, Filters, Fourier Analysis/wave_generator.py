# wave_generator.py
# Generate 800 Hz sine and square waves

# Uses (1) AITRIP AD9833 Signal Generator
# Uses (1) Adafruit TLV2462 Op Amp
# Uses (1) 10K Ohm and (1) 22K Ohm Resistor

import time

import analogio
import board
import busio
import digitalio
from ad9833_blinka import AD9833

# Configure analog input pin (FROM the AD9833)
pin_adc = analogio.AnalogIn(board.ADC1)

# Create SPI (MISO not used by AD9833)
spi_bus = busio.SPI(clock=board.GP18, MOSI=board.GP19, MISO=None)

# Configure chip select (FSYNC on AD9833) on GP22
pin_cs = digitalio.DigitalInOut(board.GP22)
pin_cs.switch_to_output(value=True)  # idle high (not selected)

# Configure AD9833 Signal Generator
wave_gen = AD9833(spi_bus, pin_cs, baudrate=100_000)

print("Generating 750 Hz tone")
for _ in range(3):
    print("Square wave...")
    wave_gen.reset(state=True)  # Hold in reset
    wave_gen.waveform = "square"  # Load waveform type while in reset
    wave_gen.frequency = 750  # Load frequency (Hz) while in reset
    wave_gen.phase = 0.0  # Load phase while in reset
    wave_gen.reset(state=False)  # Power up and start outputting
    time.sleep(3.0)

    print("Sine wave...")
    wave_gen.reset(state=True)  # Hold in reset
    wave_gen.waveform = "sine"  # Load waveform type while in reset
    wave_gen.frequency = 750  # Load frequency (Hz) while in reset
    wave_gen.phase = 0.0  # Load phase while in reset
    wave_gen.reset(state=False)  # Power up and start outputting
    time.sleep(3.0)

wave_gen.reset(state=True)  # Hold in reset
