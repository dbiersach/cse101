# ls7366r_blinka.py
# Blinka-compatible driver for the LS7366R 32-bit quadrature / pulse counter over SPI.
# Works on CircuitPython and on Linux/SBCs via Blinka. Uses adafruit_bus_device for SPI.
#
# Wiring (typical, adjust pins for your board):
#   - SPI SCK  -> LS7366R SCK
#   - SPI MOSI -> LS7366R MOSI (RXD)
#   - SPI MISO -> LS7366R MISO (TXD)
#   - Chip Select (any GPIO) -> LS7366R SS/
#   - VDD -> 3V3 (or 5V if your board is 5V-tolerant on SPI)
#   - VSS -> GND
#   - To count simple pulses feed your pulses to A, tie B HIGH (count up)
#     or LOW (count down). Leave INDEX unconnected unless you use it.
#
# Notes:
#  - SPI mode 0 (CPOL=0, CPHA=0)
#  - The counter width is selectable (1..4 bytes). This driver defaults to 4 bytes.
#  - Read CNTR automatically latches CNTR to OTR, then returns OTR (per datasheet).
#

import digitalio
from adafruit_bus_device.spi_device import SPIDevice


class LS7366R:
    # ---- Instruction opcodes (from datasheet) ----
    _CLR_MDR0 = 0x08
    _CLR_MDR1 = 0x10
    _CLR_CNTR = 0x20
    _CLR_STR = 0x30

    _RD_MDR0 = 0x48
    _RD_MDR1 = 0x50
    _RD_CNTR = 0x60  # Transfers CNTR->OTR then reads OTR
    _RD_OTR = 0x68
    _RD_STR = 0x70

    _WR_MDR0 = 0x88
    _WR_MDR1 = 0x90
    _WR_DTR = 0x98

    _LOAD_CNTR = 0xE0  # DTR -> CNTR
    _LOAD_OTR = 0xE4  # CNTR -> OTR

    # ---- MDR0 bit fields ----
    # Quadrature / non-quadrature
    QUAD_NON = 0x00  # A=clock, B=direction
    QUAD_X1 = 0x01
    QUAD_X2 = 0x02
    QUAD_X4 = 0x03

    # Count modes
    COUNT_FREE = 0x00
    COUNT_SINGLE = 0x04
    COUNT_RANGE_LIM = 0x08
    COUNT_MOD_N = 0x0C

    # Index behavior
    INDEX_DISABLE = 0x00
    INDEX_LOADC = 0x10  # DTR -> CNTR
    INDEX_RESETC = 0x20  # CNTR -> 0
    INDEX_LOADO = 0x30  # CNTR -> OTR

    # Index sync / async
    INDEX_ASYNC = 0x00
    INDEX_SYNC = 0x40

    # Input filter (applies in quadrature modes)
    FILTER_1 = 0x00  # fF = fCKi
    FILTER_2 = 0x80  # fF = fCKi/2

    # ---- MDR1 bit fields ----
    BYTE_4 = 0x00
    BYTE_3 = 0x01
    BYTE_2 = 0x02
    BYTE_1 = 0x03

    COUNT_ENABLE = 0x00  # B2=0
    COUNT_DISABLE = 0x04  # B2=1

    FLAG_IDX = 0x10
    FLAG_CMP = 0x20
    FLAG_BW = 0x40
    FLAG_CY = 0x80

    def __init__(
        self,
        spi,
        cs_pin,
        *,
        baudrate=1_000_000,
        polarity=0,
        phase=0,
        mdr0=None,
        mdr1=None,
    ):
        """
        spi    : an initialized busio.SPI (or Blinka-compatible) object
        cs_pin : a digitalio.DigitalInOut for chip select (active low)
        baudrate/polarity/phase: SPI parameters (mode 0 by default)

        mdr0   : optional initial MDR0 value
        mdr1   : optional initial MDR1 value
        """
        if isinstance(cs_pin, digitalio.DigitalInOut):
            self._cs = cs_pin
        else:
            self._cs = digitalio.DigitalInOut(cs_pin)
        self._cs.direction = digitalio.Direction.OUTPUT
        self._device = SPIDevice(
            spi, self._cs, baudrate=baudrate, polarity=polarity, phase=phase
        )

        # Default: 4-byte counter, counting enabled; non-quadrature, free-run
        if mdr0 is None:
            mdr0 = (
                self.QUAD_NON
                | self.COUNT_FREE
                | self.INDEX_DISABLE
                | self.INDEX_ASYNC
                | self.FILTER_1
            )
        if mdr1 is None:
            mdr1 = self.BYTE_4 | self.COUNT_ENABLE  # 4-byte counter, enable counting

        self.write_mdr0(mdr0)
        self.write_mdr1(mdr1)

        # Track the active counter width from MDR1
        self._nbytes = 4 - (mdr1 & 0x03)  # 0->4B,1->3B,2->2B,3->1B

    # ---------- Low-level SPI helpers ----------
    def _write(self, opcode, data=None):
        """Write an opcode, optionally followed by data bytes."""
        with self._device as spi:
            spi.write(bytes((opcode,)))
            if data is not None:
                spi.write(data)

    def _read(self, opcode, nbytes):
        """Write an opcode, then read nbytes into a new bytearray and return it."""
        buf = bytearray(nbytes)
        with self._device as spi:
            spi.write(bytes((opcode,)))
            spi.readinto(buf)
        return buf

    # ---------- Register access ----------
    def write_mdr0(self, value: int):
        self._write(self._WR_MDR0, bytes((value & 0xFF,)))

    def write_mdr1(self, value: int):
        self._write(self._WR_MDR1, bytes((value & 0xFF,)))
        self._nbytes = 4 - (value & 0x03)

    def read_mdr0(self) -> int:
        return self._read(self._RD_MDR0, 1)[0]

    def read_mdr1(self) -> int:
        return self._read(self._RD_MDR1, 1)[0]

    def clear_counter(self):
        self._write(self._CLR_CNTR)

    def clear_status(self):
        self._write(self._CLR_STR)

    def read_status(self) -> int:
        """Return STR (status) byte."""
        return self._read(self._RD_STR, 1)[0]

    def enable_counting(self, enable: bool = True):
        """Set/clear MDR1.B2 to enable/disable counting."""
        m1 = self.read_mdr1()
        if enable:
            m1 &= ~0x04
        else:
            m1 |= 0x04
        self.write_mdr1(m1)

    def set_counter_bytes(self, nbytes: int):
        """Set counter width to 1..4 bytes (affects CNTR/OTR/DTR)."""
        if nbytes not in (1, 2, 3, 4):
            raise ValueError("nbytes must be 1..4")
        m1 = self.read_mdr1()
        m1 = (m1 & ~0x03) | {4: 0x00, 3: 0x01, 2: 0x02, 1: 0x03}[nbytes]
        self.write_mdr1(m1)

    def write_dtr(self, value: int):
        """Write DTR with current counter byte-width; value truncated accordingly."""
        n = self._nbytes
        maxv = (1 << (8 * n)) - 1
        value &= maxv
        data = value.to_bytes(n, "big", signed=False)
        self._write(self._WR_DTR, data)

    def load_cntr_from_dtr(self):
        """DTR -> CNTR (parallel transfer)."""
        self._write(self._LOAD_CNTR)

    def latch_cntr_to_otr(self):
        """CNTR -> OTR (parallel transfer)."""
        self._write(self._LOAD_OTR)

    def read_counter(self, *, signed: bool = True) -> int:
        """
        Read the counter using RD_CNTR (which latches CNTR to OTR and then reads OTR).
        If signed=True, return a 2's-complement signed integer for the configured width.
        """
        n = self._nbytes
        raw = self._read(self._RD_CNTR, n)
        val = int.from_bytes(raw, "big", signed=False)
        if not signed:
            return val
        # 2's complement sign-extend to Python int
        sign_bit = 1 << (8 * n - 1)
        if val & sign_bit:
            val -= 1 << (8 * n)
        return val

    # Convenience helpers
    def zero(self):
        """Clear CNTR to 0."""
        self.clear_counter()

    def configure_non_quadrature_4byte(self, count_enable=True):
        """Simple preset: non-quadrature, free-run, 4-byte counter."""
        self.write_mdr0(
            self.QUAD_NON
            | self.COUNT_FREE
            | self.INDEX_DISABLE
            | self.INDEX_ASYNC
            | self.FILTER_1
        )
        self.write_mdr1(
            self.BYTE_4 | (self.COUNT_ENABLE if count_enable else self.COUNT_DISABLE)
        )
