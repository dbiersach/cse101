# biot_savart.py
# Measure the strength of an electromagnet

# Uses (1) Adafruit DRV8833 Motor Driver
# Uses (1) Adafruit INA260 Current Sensor
# Uses (1) Adafruit MMC5603 Triple-axis Magnetometer
# Uses (1) Adafruit 5V Electromagnet - 5 Kg Holding Force [P25/20]

from pathlib import Path

import adafruit_ina260
import adafruit_mmc56x3
import board
import busio
import digitalio
import matplotlib.pyplot as plt
import numpy as np
import pwmio
from adafruit_motor import motor
from matplotlib.ticker import AutoMinorLocator
from tqdm import tqdm


def fit_linear(x, y):
    # Use Gauss's Method of Least Squares
    n = len(x)
    sum_x = np.sum(x)
    sum_y = np.sum(y)
    sum_xy = np.sum(x * y)
    sum_x2 = np.sum(x**2)
    sum_y2 = np.sum(y**2)

    # Calculate slope and intercept
    numerator = n * sum_xy - sum_x * sum_y
    m = numerator / (n * sum_x2 - sum_x**2)
    b = (sum_y - m * sum_x) / n

    # Calculate Pearson's correlation coefficient "r"
    denominator = np.sqrt((n * sum_x2 - sum_x**2) * (n * sum_y2 - sum_y**2))
    r = numerator / denominator

    return m, b, r


def main():
    # Configure the Adafruit MMC5603 Triple-axis Magnetometer
    i2c_bus0 = busio.I2C(board.SCL0, board.SDA0)
    magnetometer = adafruit_mmc56x3.MMC5603(i2c_bus0)

    # Configure the Adafruit INA260 Current Sensor
    i2c_bus1 = busio.I2C(board.SCL1, board.SDA1)
    ina260 = adafruit_ina260.INA260(i2c_bus1)

    # Configure DRV8833 DC/Stepper Motor Driver
    motor_pwm_1 = pwmio.PWMOut(board.GP16, frequency=333)
    motor_pwm_2 = pwmio.PWMOut(board.GP17, frequency=333)
    motor_driver = motor.DCMotor(motor_pwm_1, motor_pwm_2)
    motor_driver.decay_mode = motor.SLOW_DECAY
    motor_driver.throttle = 0.1  # 10% of Vcc
    motor_sleep_pin = digitalio.DigitalInOut(board.GP18)
    motor_sleep_pin.direction = digitalio.Direction.OUTPUT
    motor_sleep_pin.value = True  # Now out of sleep mode

    # Set number of samples
    n = 15
    print(f"Reading {n} samples...")

    # Allocate arrays
    current = np.zeros(n, float)  # mA
    field_strength = np.zeros(n, float)  # uT

    # Read field strength at each current step
    for i in tqdm(range(n)):
        # Set voltage (% of 5V) flowing into electromagnet
        motor_driver.throttle = i / 100

        # Find mean current over 100 subsamples
        for _ in range(100):
            current[i] += ina260.current
        current[i] /= 100

        # Measure combined magnetic field strength
        mag_x, mag_y, mag_z = magnetometer.magnetic
        field_strength[i] = np.sqrt(mag_x**2 + mag_y**2 + mag_z**2)

    # Turn off motor driver (enter sleep state)
    motor_sleep_pin.value = False

    # Plot samples
    plt.figure(Path(__file__).name)
    plt.gca().set_facecolor("black")
    plt.scatter(
        current, field_strength, marker=".", color="yellow", label="Sensor Data"
    )
    # Plot line of best fit using linear regression
    x = np.linspace(np.min(current), np.max(current), 1000)
    m, b, r = fit_linear(current, field_strength)
    plt.plot(x, m * x + b, label="Linear")

    plt.title(f"Biot-Savart Law (r={r:0.3f})")
    plt.xlabel("Current (mA)")
    plt.ylabel("Magnetic Field Strength (uT)")
    plt.legend()
    plt.gca().xaxis.set_minor_locator(AutoMinorLocator(5))
    plt.gca().yaxis.set_minor_locator(AutoMinorLocator(5))
    plt.show()


if __name__ == "__main__":
    main()
