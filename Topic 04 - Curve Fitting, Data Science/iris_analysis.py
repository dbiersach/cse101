#!/usr/bin/env -S uv run
"""iris_analysis.py"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

file_name = "iris.csv"
petal_data = np.genfromtxt(
    file_name, delimiter=",", skip_header=1, usecols=(2, 3), dtype=float
)

species_data = np.genfromtxt(
    file_name, delimiter=",", skip_header=1, usecols=(4), dtype=str
)

plt.figure(Path(__file__).name, figsize=(8, 6))
for species in np.unique(species_data):
    mask = species_data == species  # Broadcasting and element-wise comparison
    plt.scatter(petal_data[mask, 0], petal_data[mask, 1], label=species.strip('"'))
plt.title("Iris Petal Length vs Petal Width By Species")
plt.xlabel("Petal Length (cm)")
plt.ylabel("Petal Width (cm)")
plt.legend(loc="upper left")
plt.show()
