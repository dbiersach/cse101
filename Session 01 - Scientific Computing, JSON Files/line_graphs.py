# line_graphs.py

import sys

import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(-10, 10)
y1 = 2 * x - 5
y2 = -0.3 * x**2 + 15

plt.plot(x, y1)
plt.plot(x, y2)
plt.show(block=True)
sys.exit()
