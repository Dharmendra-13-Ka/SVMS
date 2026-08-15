import random
import time

min_voltage = 400
max_voltage = 0

while True:

    voltage = random.randint(180,250)

    if voltage < min_voltage:
        min_voltage = voltage

    if voltage > max_voltage:
        max_voltage = voltage

    print("------------------------")
    print("Current Voltage :", voltage,"V")
    print("Minimum Voltage :", min_voltage,"V")
    print("Maximum Voltage :", max_voltage,"V")

    time.sleep(2)