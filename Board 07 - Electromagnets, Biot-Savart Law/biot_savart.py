# biot_savart.py
# Measure the strength of an electromagnet

# Uses (1) Adafruit MMC5603 Triple-axis Magnetometer
# Uses (1) Adafruit INA260 Current Sensor
# Uses (1) Adafruit DRV8833 DC/Stepper Motor Driver
# Uses (1) Adafruit 5V Electromagnet

from pathlib import Path

import adafruit_ina260
import adafruit_mmc56x3
import board
import busio
import digitalio
import matplotlib.pyplot as plt
import numpy as np
import pwmio
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
    # Use slower I2C speed for reliability
    i2c_bus0 = busio.I2C(scl=board.SCL0, sda=board.SDA0)  # Qwiic Connector
    magnetometer = adafruit_mmc56x3.MMC5603(i2c_bus0)

    # Configure the Adafruit INA260 Current Sensor
    i2c_bus1 = busio.I2C(scl=board.GP15, sda=board.GP14)
    ina260 = adafruit_ina260.INA260(i2c_bus1)

    # Configure DRV8833 DC/Stepper Motor Driver
    motor_pwm_1 = pwmio.PWMOut(board.GP16, frequency=333)
    motor_pwm_2 = pwmio.PWMOut(board.GP17, frequency=333)
    motor_pwm_2.duty_cycle = 0  # Hold BOUT2 low

    motor_sleep_pin = digitalio.DigitalInOut(board.GP18)
    motor_sleep_pin.direction = digitalio.Direction.OUTPUT
    motor_sleep_pin.value = True  # Wake from sleep mode

    # Set number of samples
    n = 15
    print(f"Reading {n} samples...")

    # Allocate arrays
    current = np.zeros(n, float)  # mA
    field_strength = np.zeros(n, float)  # uT

    # Read field strength at each current step
    for i in tqdm(range(n)):
        # Set voltage (% of 5V from VBUS) flowing into electromagnet
        throttle = i / (n - 1) if n > 1 else 0  # 0 to 100% range
        motor_pwm_1.duty_cycle = int(throttle * 65535)  # 0-65535 range

        # Find mean current and field over multiple samples
        num_samples = 50
        for _ in range(num_samples):
            current[i] += ina260.current
            try:
                mag_x, mag_y, mag_z = magnetometer.magnetic
                field_strength[i] += np.sqrt(mag_x**2 + mag_y**2 + mag_z**2)
            except (RuntimeError, OSError):
                # Reinitialize I2C bus and magnetometer
                try:
                    while not i2c_bus0.try_lock():
                        pass
                    i2c_bus0.unlock()
                    i2c_bus0.deinit()
                    i2c_bus0 = busio.I2C(board.SCL0, board.SDA0)
                    magnetometer = adafruit_mmc56x3.MMC5603(i2c_bus0)
                except (RuntimeError, OSError):
                    pass
        current[i] /= num_samples
        field_strength[i] /= num_samples

    # Turn off motor driver and clean up
    motor_pwm_1.duty_cycle = 0
    motor_pwm_1.deinit()
    motor_pwm_2.deinit()
    motor_sleep_pin.value = False  # Enter sleep state
    motor_sleep_pin.deinit()

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
