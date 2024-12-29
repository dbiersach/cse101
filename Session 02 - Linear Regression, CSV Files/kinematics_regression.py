# kinematics_regression.py

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures


def fit_quadratic(x, y):
    # Reshape vector x to become matrix x
    x = x[:, np.newaxis]
    transformer = PolynomialFeatures(degree=2, include_bias=False)
    transformer.fit(x)
    # The matrix x2 will have two columns:
    # 1) the original x values and 2) the x**2 values
    x2 = np.array(transformer.transform(x))
    model = LinearRegression().fit(x2, y)
    a = model.coef_[1]
    b = model.coef_[0]
    c = model.intercept_
    return a, b, c


def main():
    file_name = "kinematics_regression.csv"
    file_path = Path(__file__).parent / file_name    
    vec_x, vec_y = np.genfromtxt(file_path, delimiter=",", unpack=True)

    a, b, c = fit_quadratic(vec_x, vec_y)

    print(f"Constant acceleration = {a * 2:.4f} m/s^2")
    print(f"Initial velocity = {b:.4f} m/s")

    x = np.linspace(np.min(vec_x), np.max(vec_x))

    plt.figure(Path(__file__).name)
    plt.plot(x, a * x**2 + b * x + c)
    plt.scatter(vec_x, vec_y, color="red")

    plt.title("Newtonian Kinematics")
    plt.xlabel("Time (sec)")
    plt.ylabel("Distance (m)")
    plt.show(block=True)
    sys.exit()


main()
