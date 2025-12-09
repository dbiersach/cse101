# test_blinka.py

import os

import board
import hid
import serial.tools.list_ports as lp

if os.environ.get("BLINKA_U2IF") == "1":
    print("✅ BLINKA_U2IF environment variable is set")
else:
    print("❌ BLINKA_U2IF environment variable is NOT set")

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

if hasattr(board, "I2C"):
    print("✅ I2C is available")

print(f"✅ Board pins:\n{dir(board)}")
