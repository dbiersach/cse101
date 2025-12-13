# rlc_measure.py
# Measure frequency response of driven RLC circuit

# Uses AITRIP AD9833 Signal Generator
# Uses TLV2462 Omp Amp
# Uses (1) 10K Ohm and (1) 22K Ohm Resistor
# Uses (1) 10 Ohm & (1) 100 Ohm Resistor
# Uses 100 mH inductor (L)
# Uses 100nF capacitor (C)

from pathlib import Path

import analogio
import board
import busio
import digitalio
import numpy as np
from ad9833_blinka import AD9833
from tqdm import tqdm

# Set number of samples
n = 500
print(f"Reading {n} samples...")

# Allocate arrays
freq = np.zeros(n, float)  # frequency in Hz
volts_actual = np.zeros(n, float)  # volts

# Configure analog input pin (FROM the AD9833)
pin_adc = analogio.AnalogIn(board.ADC1)

# Configure chip select (FSYNC on AD9833) on GP22
pin_cs = digitalio.DigitalInOut(board.GP22)
pin_cs.switch_to_output(value=True)  # idle high (not selected)

# Create SPI (MISO not used by AD9833)
spi_bus = busio.SPI(clock=board.GP18, MOSI=board.GP19, MISO=None)

# Configure AD9833 Signal Generator
wave_gen = AD9833(spi_bus, pin_cs, baudrate=100_000)
wave_gen.reset(state=True)  # Hold in reset
wave_gen.waveform = "sine"
wave_gen.frequency = 30  # Load frequency (Hz) while in reset
wave_gen.phase = 0.0  # Load phase while in reset
wave_gen.reset(state=False)  # Power up and start outputting

# Read input voltage over increasing wave generator frequency
for i in tqdm(range(n)):
    # Set new sine wave frequency
    freq[i] = i * 10
    wave_gen.frequency = freq[i]
    v = (pin_adc.value or 0) / 65536 * 3.3
    if i > 0:
        # Stay within 92% volts of prior frequency to reduce jitter
        while v < volts_actual[i - 1] * 0.92:
            v = (pin_adc.value or 0) / 65536 * 3.3
    volts_actual[i] = v

# Convert frequencies to kHz
freq = freq / 1000

# Resonant frequency is at the peak voltage
max_volt_actual = np.max(volts_actual)
resonance_freq_actual = freq[np.argmax(volts_actual)]
print(f"Actual Resonance voltage = {max_volt_actual:0.4f} V")
print(f"Actual Resonance freq = {resonance_freq_actual:0.4f} kHz")

# Save samples to a CSV file
samples = np.column_stack((freq, volts_actual))
file_name = "rlc_resonance.csv"
file_path = Path(__file__).parent / file_name
np.savetxt(file_name, samples, fmt="%3.6f", delimiter=",")
print(f"Saved file {file_name}")
