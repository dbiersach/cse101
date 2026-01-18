#!/usr/bin/env -S uv run
"""complex_algebra.py"""

import numpy as np

z1 = complex(-5.9, -7.5)
z2 = complex(np.sqrt(2), np.pi)
z3 = 7 - 2j

print(f"z1 = {z1}")
print(f"z2 = {z2}")
print(f"z3 = {z3}")
print()

print(f"{z1 + z2 = :.4f}")
print(f"{z1 - z2 = :.4f}")
print(f"{z1 * z2 = :.4f}")
print(f"{z1 / z2 = :.4f}")
print()

print(f"z1* = {np.conjugate(z1):.4f}")
print(f"|z2| = {np.absolute(z2):.4f}")
print(f"arg(z3) = {np.angle(z3):.4f}")
print(f"z3^3 = {np.power(z3, 3):.4f}")
