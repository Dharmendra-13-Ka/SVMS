import random
import time
from datetime import datetime

# ==========================================
# SMART VOLTAGE MONITORING SYSTEM (SVMS)
# Version 1.0
# ==========================================

DEVICE_ID = "TVS001"

MIN_VOLTAGE = 400
MAX_VOLTAGE = 0

MIN_CURRENT = 100
MAX_CURRENT = 0

LOW_VOLTAGE_LIMIT = 200
HIGH_VOLTAGE_LIMIT = 245
MAX_CURRENT_LIMIT = 16

print("==========================================")
print(" SMART VOLTAGE MONITORING SYSTEM ")
print("==========================================")
print("Device ID :", DEVICE_ID)
print("System Started Successfully")
print("==========================================")

while True:

    # Live Dummy Data (बाद में ESP32 से आएगा)
    CURRENT_VOLTAGE = random.randint(180, 250)
    CURRENT = round(random.uniform(2.0, 16.0), 2)
    POWER = round(CURRENT_VOLTAGE * CURRENT, 2)

    # Minimum Voltage
    if CURRENT_VOLTAGE < MIN_VOLTAGE:
        MIN_VOLTAGE = CURRENT_VOLTAGE

    # Maximum Voltage
    if CURRENT_VOLTAGE > MAX_VOLTAGE:
        MAX_VOLTAGE = CURRENT_VOLTAGE

    # Minimum Current
    if CURRENT < MIN_CURRENT:
        MIN_CURRENT = CURRENT

    # Maximum Current
    if CURRENT > MAX_CURRENT:
        MAX_CURRENT = CURRENT

    # Relay Logic
    if CURRENT_VOLTAGE < LOW_VOLTAGE_LIMIT:
        RELAY_STATUS = "OFF"
        CHARGER_STATUS = "OFF"
        ALARM = "LOW VOLTAGE"

    elif CURRENT_VOLTAGE > HIGH_VOLTAGE_LIMIT:
        RELAY_STATUS = "OFF"
        CHARGER_STATUS = "OFF"
        ALARM = "HIGH VOLTAGE"

    elif CURRENT > MAX_CURRENT_LIMIT:
        RELAY_STATUS = "OFF"
        CHARGER_STATUS = "OFF"
        ALARM = "OVER CURRENT"

    else:
        RELAY_STATUS = "ON"
        CHARGER_STATUS = "ON"
        ALARM = "NORMAL"

    print("\n==========================================")
    print(" SMART VOLTAGE MONITORING SYSTEM ")
    print("==========================================")

    print("Device ID        :", DEVICE_ID)
    print("Date & Time      :", datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

    print("------------------------------------------")

    print("Current Voltage  :", CURRENT_VOLTAGE, "V")
    print("Minimum Voltage  :", MIN_VOLTAGE, "V")
    print("Maximum Voltage  :", MAX_VOLTAGE, "V")

    print("------------------------------------------")

    print("Current          :", CURRENT, "A")
    print("Minimum Current  :", MIN_CURRENT, "A")
    print("Maximum Current  :", MAX_CURRENT, "A")

    print("------------------------------------------")

    print("Power            :", POWER, "W")
    print("Relay Status     :", RELAY_STATUS)
    print("Charger Status   :", CHARGER_STATUS)
    print("Alarm            :", ALARM)

    print("==========================================")

    time.sleep(2)