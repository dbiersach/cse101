# AD9833.py - CircuitPython driver for AD9833 DDS (u2if/Blinka friendly)
# Dave Biersach - derived from https://github.com/owainm713/AD9833-MicroPython-Module
# Key fixes implemented:
# - Writes full 28-bit frequency in ONE SPI transaction with CS (FSYNC) held low
#   (LSW first, then MSW) per datasheet B28=1 mode.
# - Uses correct address fields for FREQ0/FREQ1 and PHASE0/PHASE1.
# - Control register bits follow datasheet (B28, HLB, FSELECT, PSELECT, RESET, etc.).
# - Correct waveform selection per Table 15 (sine/triangle/square MSB or MSB/2).
# - Defaults to SPI mode CPOL=1, CPHA=0 (a.k.a. mode 2) which matches ADI guidance.
# - Clean, minimal API with properties: waveform, frequency, phase; methods for reset
#   and selecting registers.
#
# Datasheet references (AD9833 Rev. G):
# - B28/HLB and 28-bit write order (LSW then MSW): pages 14–15.
# - Frequency register addressing (FREQ0=01, FREQ1=10): Table 8.
# - Phase register addressing (D15..D14=11; D13 selects PHASE0/1): Table 12.
# - VOUT waveform selection with OPBITEN/MODE/DIV2: Table 15.
# - RESET behavior: Table 13.
#
# Typical modules ship with a 25 MHz MCLK; adjust mclk if yours differs.
# This driver requires: adafruit_blinka, adafruit_bus_device
#
# Example wiring (RP2040 via Adafruit u2if):
#   SCK  -> board.GP18
#   MOSI -> board.GP19
#   CS   -> board.GP22  (FSYNC, active low)
#   MISO not used
#
# Example:
#   import board, busio, digitalio
#   from AD9833 import AD9833
#   spi = busio.SPI(board.GP18, MOSI=board.GP19, MISO=None)
#   cs  = digitalio.DigitalInOut(board.GP22); cs.switch_to_output(value=True)
#   dds = AD9833(spi, cs)  # defaults: 1 MHz, mode=2 (polarity=1, phase=0), mclk=25e6
#   dds.reset()
#   dds.waveform = "sine"
#   dds.frequency = 100.0
#
from __future__ import annotations

import time

try:
    import busio
    import digitalio
except ImportError:  # pragma: no cover - helpful message if Blinka not present
    raise ImportError("This driver requires CircuitPython/Blinka (busio, digitalio).")

try:
    from adafruit_bus_device.spi_device import SPIDevice
except ImportError as e:
    raise ImportError("Please install adafruit_bus_device: pip install adafruit-circuitpython-busdevice") from e


# -----------------------------
# Bitfield & address constants
# -----------------------------

# Control register bit positions (D15..D0) — D15..D14 must be 0 for control writes.
_B28 = 1 << 13  # two consecutive writes load full 28-bit frequency
_HLB = 1 << 12  # ignored when B28=1
_FSELECT = 1 << 11  # 0: FREQ0, 1: FREQ1 used by phase accumulator
_PSELECT = 1 << 10  # 0: PHASE0, 1: PHASE1 used
_RESET = 1 << 8
_SLEEP1 = 1 << 7   # disable internal MCLK to NCO
_SLEEP12 = 1 << 6   # power down DAC
_OPBITEN = 1 << 5   # route MSB(/2) to VOUT instead of DAC output
_DIV2 = 1 << 3   # with OPBITEN=1: 1 = MSB, 0 = MSB/2
_MODE = 1 << 1   # with OPBITEN=0: 1 = triangle, 0 = sine

# Frequency register write prefixes (top two bits select destination per Table 8).
_FREQ0_PREFIX = 0x4000  # 0b01 << 14
_FREQ1_PREFIX = 0x8000  # 0b10 << 14

# Phase register write prefixes (D15..D14=11, D13 selects PHASE0/1 per Table 12).
_PHASE0_PREFIX = 0xC000  # 0b110 << 13
_PHASE1_PREFIX = 0xE000  # 0b111 << 13


class AD9833:
    """
    CircuitPython driver for the AD9833 DDS.
    Ensures frequency writes are performed with LSW then MSW in one SPI transaction
    while CS (FSYNC) remains low.
    """

    def __init__(
        self,
        spi: "busio.SPI",
        cs: "digitalio.DigitalInOut",
        *,
        mclk: float = 25_000_000.0,
        baudrate: int = 1_000_000,
        polarity: int = 1,
        phase: int = 0,
    ) -> None:
        """
        :param spi: A configured busio.SPI instance (MISO may be None)
        :param cs:  digitalio.DigitalInOut for chip select (FSYNC), set to output before passing
        :param mclk: Master clock frequency of your AD9833 module (Hz). Common: 25e6.
        :param baudrate: SPI bitrate for transactions. 1 MHz is conservative/safe for u2if.
        :param polarity: SPI clock polarity. ADI guidance prefers CPOL=1.
        :param phase: SPI clock phase. ADI guidance prefers CPHA=0 (mode 2).
        """
        if not isinstance(cs, digitalio.DigitalInOut):
            raise TypeError("cs must be a digitalio.DigitalInOut")
        self.mclk = float(mclk)
        self._control = 0  # top two bits must be 0 for control writes
        # Default: enable full 28-bit frequency writes
        self._control |= _B28

        # track selected registers
        self._freq_sel = 0  # 0 => FREQ0, 1 => FREQ1
        self._phase_sel = 0  # 0 => PHASE0, 1 => PHASE1

        # SPI device wrapper will manage locks and keep CS low for contiguous writes
        self._device = SPIDevice(
            spi, cs,
            baudrate=baudrate,
            polarity=polarity,
            phase=phase,
        )

        # sensible default waveform: sine, DAC enabled
        self._control &= ~_OPBITEN  # ensure DAC connected
        self._control &= ~_MODE     # sine
        self._control &= ~_SLEEP12  # DAC enabled
        self._write_control()

    # -----------------------------
    # Low-level write helpers
    # -----------------------------

    def _write_control(self) -> None:
        """Push current control register (D15..D14=0)."""
        word = self._control & 0x3FFF  # ensure D15..D14=0, reserved bits remain 0
        self._write_words([word])

    def _write_words(self, words) -> None:
        """
        Write a sequence of 16-bit words in ONE SPI transaction.
        This ensures CS (FSYNC) stays low across the full 28-bit frequency write.
        """
        # big-endian bytes for each 16-bit word
        out = bytearray(2 * len(words))
        i = 0
        for w in words:
            w &= 0xFFFF
            out[i] = (w >> 8) & 0xFF
            out[i + 1] = w & 0xFF
            i += 2
        with self._device as spi:
            spi.write(out)

    # -----------------------------
    # Public API
    # -----------------------------

    def reset(self, *, state: bool | None = None, pulse_ms: float = 1.0) -> None:
        """
        Set or pulse the RESET bit.
        :param state: If True/False, sets RESET to that state. If None (default),
                      pulses RESET high then low with a small delay.
        :param pulse_ms: delay (milliseconds) while RESET is asserted when pulsing.
        """
        if state is None:
            self._control |= _RESET
            self._write_control()
            time.sleep(pulse_ms / 1000.0)
            self._control &= ~_RESET
            self._write_control()
        elif state:
            self._control |= _RESET
            self._write_control()
        else:
            self._control &= ~_RESET
            self._write_control()

    def select_frequency_register(self, reg: int) -> None:
        """Select FREQ0 (0) or FREQ1 (1) for output via FSELECT bit."""
        reg = 1 if reg else 0
        self._freq_sel = reg
        if reg:
            self._control |= _FSELECT
        else:
            self._control &= ~_FSELECT
        self._write_control()

    def select_phase_register(self, reg: int) -> None:
        """Select PHASE0 (0) or PHASE1 (1) for output via PSELECT bit."""
        reg = 1 if reg else 0
        self._phase_sel = reg
        if reg:
            self._control |= _PSELECT
        else:
            self._control &= ~_PSELECT
        self._write_control()

    def set_frequency(self, hz: float, *, reg: int | None = None) -> None:
        """
        Set frequency in Hz into FREQ0 or FREQ1.
        Writes both 14-bit halves with LSW first, then MSW, in one transaction.

        :param hz: desired output frequency in Hz
        :param reg: 0 for FREQ0, 1 for FREQ1, or None to use currently selected register
        """
        if hz < 0:
            raise ValueError("frequency must be non-negative")
        if reg is None:
            reg = self._freq_sel
        reg = 1 if reg else 0
        prefix = _FREQ1_PREFIX if reg else _FREQ0_PREFIX

        # Convert to 28-bit tuning word: f_out = (MCLK / 2^28) * word
        word28 = int(round(hz * (1 << 28) / self.mclk)) & 0x0FFFFFFF
        lsw = prefix | (word28 & 0x3FFF)           # lower 14 bits
        msw = prefix | ((word28 >> 14) & 0x3FFF)   # upper 14 bits

        # With B28=1, device latches the full 28-bit word after the second write.
        # Keep FSYNC low for both 16-bit writes.
        self._write_words([lsw, msw])

    def set_phase(self, radians: float, *, reg: int | None = None) -> None:
        """
        Set phase offset (radians) into PHASE0 or PHASE1.
        :param radians: phase in radians (wrapped into [0, 2π))
        :param reg: 0 for PHASE0, 1 for PHASE1, or None to use currently selected register
        """
        import math
        if reg is None:
            reg = self._phase_sel
        reg = 1 if reg else 0
        prefix = _PHASE1_PREFIX if reg else _PHASE0_PREFIX
        # 12-bit phase word maps 0..2π to 0..4095
        phase_word = int(round((radians % (2 * math.pi)) * (4096.0 / (2 * math.pi)))) & 0x0FFF
        self._write_words([prefix | phase_word])

    # -------- Properties --------

    @property
    def waveform(self) -> str:
        """Return 'sine', 'triangle', or 'square'."""
        if self._control & _OPBITEN:
            return "square"
        return "triangle" if (self._control & _MODE) else "sine"

    @waveform.setter
    def waveform(self, kind: str) -> None:
        kind_l = str(kind).strip().lower()
        if kind_l not in ("sine", "triangle", "square"):
            raise ValueError("waveform must be 'sine', 'triangle', or 'square'")
        # Clear OPBITEN/MODE/DIV2 bits; set as needed
        self._control &= ~(_OPBITEN | _MODE | _DIV2)
        if kind_l == "sine":
            # OPBITEN=0, MODE=0, DAC enabled
            self._control &= ~_SLEEP12
        elif kind_l == "triangle":
            # OPBITEN=0, MODE=1, DAC enabled
            self._control |= _MODE
            self._control &= ~_SLEEP12
        else:  # square: route MSB (/2) to output, DAC can be powered down
            self._control |= _OPBITEN
            # Choose full-amplitude MSB (DIV2=1). Set DIV2=0 if you want MSB/2.
            self._control |= _DIV2
            # MODE should be 0 when OPBITEN=1
            self._control &= ~_MODE
            # Optionally power down DAC to save power when using MSB output:
            self._control |= _SLEEP12
        self._write_control()

    @property
    def frequency(self) -> float:
        """Return the last frequency written to the currently selected register (best-effort).
        Note: The AD9833 does not provide readback; this returns a cached value if set via this API.
        """
        return getattr(self, "_freq_cache_" + str(self._freq_sel), 0.0)

    @frequency.setter
    def frequency(self, hz: float) -> None:
        self.set_frequency(hz, reg=self._freq_sel)
        setattr(self, "_freq_cache_" + str(self._freq_sel), float(hz))

    @property
    def phase(self) -> float:
        """Return the last phase (radians) written to the currently selected phase reg (best-effort)."""
        return getattr(self, "_phase_cache_" + str(self._phase_sel), 0.0)

    @phase.setter
    def phase(self, radians: float) -> None:
        self.set_phase(radians, reg=self._phase_sel)
        setattr(self, "_phase_cache_" + str(self._phase_sel), float(radians))

    # Utilities
    def sleep(self, *, dac: bool | None = None, clock: bool | None = None) -> None:
        """Control SLEEP12 (DAC) and SLEEP1 (clock) bits. Pass True to enable sleep (power-down)."""
        if dac is not None:
            if dac:
                self._control |= _SLEEP12
            else:
                self._control &= ~_SLEEP12
        if clock is not None:
            if clock:
                self._control |= _SLEEP1
            else:
                self._control &= ~_SLEEP1
        self._write_control()


if __name__ == "__main__":
    # Minimal example: set up a 100 Hz sine wave on AD9833
    import board

    # Create SPI (MISO not used by AD9833)
    spi_test = busio.SPI(board.GP18, MOSI=board.GP19, MISO=None)

    # Chip select (FSYNC) on GP22
    cs_test = digitalio.DigitalInOut(board.GP22)
    cs_test.switch_to_output(value=True)  # idle high (not selected)

    # Instantiate driver (1 MHz, SPI mode 2 by default)
    dds = AD9833(spi_test, cs_test, mclk=25_000_000.0, baudrate=1_000_000, polarity=1, phase=0)

    # Reset the device, select sine, set 100 Hz on the currently selected register (FREQ0 by default)
    dds.reset()
    dds.waveform = "sine"
    dds.frequency = 100.0

    print("AD9833 configured: 100 Hz sine on VOUT using FREQ0.")
