# notch_filter.py
# Test a Twin-T Notch Filter (750 Hz center frequency)

# Uses (1) AITRIP AD9833 Signal Generator
# Uses (1) Microchip MCP6002 Op-Amp
# Uses (1) 10K Ohm and (5) 22K Ohm Resistors
# Uses (4) 10nf Capacitors
# Uses (1) Adafruit 8 Ohm Speaker

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

for _ in range(4):
    print("Sine wave at 750 Hz...")
    wave_gen.reset(state=True)  # Hold in reset
    wave_gen.waveform = "sine"  # Load waveform type while in reset
    wave_gen.frequency = 750  # Load frequency (Hz) while in reset
    wave_gen.phase = 0.0  # Load phase while in reset
    wave_gen.reset(state=False)  # Power up and start outputting
    time.sleep(4.0)

    print("Square wave at 750 Hz...")
    wave_gen.reset(state=True)  # Hold in reset
    wave_gen.waveform = "square"  # Load waveform type while in reset
    wave_gen.frequency = 725  # Load frequency (Hz) while in reset
    wave_gen.phase = 0.0  # Load phase while in reset
    wave_gen.reset(state=False)  # Power up and start outputting
    time.sleep(4.0)

wave_gen.reset(state=True)  # Hold in reset
