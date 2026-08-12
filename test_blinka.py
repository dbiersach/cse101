#!/usr/bin/env -S uv run
"""test_blinka.py"""

import os

os.environ.setdefault("BLINKA_U2IF", "1")

import hid
import serial.tools.list_ports as lp

ports = list(lp.comports())
u2if_port = None
for p in ports:
    if p.vid == 0xCAFE and p.pid == 0x4005:
        u2if_port = p
        break

if u2if_port:
    print("✅ U2IF Serial Port Found:")
    print(f"  Device: {u2if_port.device}")
    print(f"  Description: {u2if_port.description}")
else:
    print("❌ U2IF serial port NOT found")

devices = hid.enumerate()
for d in devices:
    if d["vendor_id"] == 0xCAFE and d["product_id"] == 0x4005:
        print("✅ U2IF HID Device Found")

# Importing board is the step that opens the Blinka connection, so it is the
# first thing to fail when no board is attached. The serial and HID checks
# above need no board and are what explain such a failure, so they run first
# and this import is guarded rather than allowed to stop the script.
try:
    import board
except (ImportError, OSError, RuntimeError) as exc:
    print(f"❌ Could not import board: {exc}")
else:
    if hasattr(board, "I2C"):
        print("✅ I2C is available")
    print(f"✅ Board pins:\n{dir(board)}")
