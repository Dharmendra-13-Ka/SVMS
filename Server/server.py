from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random
import sqlite3
from openpyxl import Workbook
import os

from datetime import datetime
from urllib.parse import urlparse, parse_qs
# ==========================================
# DEVICE DETAILS
# ==========================================

DEVICE_ID = "TVS001"

# ==========================================
# LIMITS
# ==========================================

LOW_VOLTAGE_LIMIT = 200
HIGH_VOLTAGE_LIMIT = 245

MAX_CURRENT_LIMIT = 16

# ==========================================
# DATABASE
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(BASE_DIR, "..", "Database", "svms.db")

# ==========================================
# LIVE VALUES
# ==========================================

LAST_FAULT = "NORMAL"

# ==========================================
# HISTORY (LAST 60 READINGS)
# ==========================================

VOLTAGE_HISTORY = []

CURRENT_HISTORY = []

POWER_HISTORY = []

HISTORY_LIMIT = 60
# ==========================================
# SAVE FAULT IN DATABASE
# ==========================================

def save_fault(
    voltage,
    current,
    power,
    relay,
    charger,
    alarm
):

    global LAST_FAULT

    if alarm == "NORMAL":
        LAST_FAULT = "NORMAL"
        return

    if alarm == LAST_FAULT:
        return

    LAST_FAULT = alarm

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    now = datetime.now()

    cursor.execute(
        """
        INSERT INTO fault_log
        (
            device_id,
            date,
            time,
            voltage,
            current,
            power,
            relay,
            charger,
            alarm,
            fault_start,
            fault_end,
            duration
        )

        VALUES
        (?,?,?,?,?,?,?,?,?,?,?,?)
        """,

        (
            DEVICE_ID,
            now.strftime("%d-%m-%Y"),
            now.strftime("%H:%M:%S"),
            voltage,
            current,
            power,
            relay,
            charger,
            alarm,
            now.strftime("%H:%M:%S"),
            "",
            ""
        )
    )

    connection.commit()
    connection.close()
    # ==========================================
# MAIN SERVER
# ==========================================
# ===========================
# LIVE DATA FROM ESP32
# ===========================

LIVE_VOLTAGE = 0.0
LIVE_CURRENT = 0.0
LIVE_POWER = 0.0

LIVE_RELAY = "OFF"
LIVE_CHARGER = "OFF"
LIVE_ALARM = "NORMAL"
class SVMSHandler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):

        self.send_response(200)

        self.send_header("Access-Control-Allow-Origin", "*")

        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

        self.send_header("Access-Control-Allow-Headers", "Content-Type")

        self.end_headers()

    def do_POST(self):

        if self.path == "/login":
       
        
            content_length = int(self.headers["Content-Length"])

            post_data = self.rfile.read(content_length).decode()

            data = json.loads(post_data)

            username = data["username"]

            password = data["password"]
            connection = sqlite3.connect(DATABASE)

            cursor = connection.cursor()

            cursor.execute(
                "SELECT * FROM admin WHERE username=? AND password=?",
                (username, password)
            )

            user = cursor.fetchone()

            connection.close()
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Content-Type", "application/json")



            self.end_headers()

            if user:

                self.wfile.write(
                    json.dumps({"status": "success"}).encode()
                )

            else:

                self.wfile.write(
                    json.dumps({"status": "failed"}).encode()
                )
    def do_GET(self):

        if self.path.startswith("/data"):
            parsed_url = urlparse(self.path)

            params = parse_qs(parsed_url.query)

            device_id = params.get("device", ["TVS001"])[0]
            voltage = random.randint(180, 250)

            current = round(random.uniform(2.0, 16.0), 2)

            power = round(voltage * current, 2)
                        # ==========================================
            # STORE LAST 60 READINGS
            # ==========================================

            VOLTAGE_HISTORY.append(voltage)
            CURRENT_HISTORY.append(current)
            POWER_HISTORY.append(power)

            if len(VOLTAGE_HISTORY) > HISTORY_LIMIT:
                VOLTAGE_HISTORY.pop(0)

            if len(CURRENT_HISTORY) > HISTORY_LIMIT:
                CURRENT_HISTORY.pop(0)

            if len(POWER_HISTORY) > HISTORY_LIMIT:
                POWER_HISTORY.pop(0)

            min_voltage = min(VOLTAGE_HISTORY)
            max_voltage = max(VOLTAGE_HISTORY)

            min_current = min(CURRENT_HISTORY)
            max_current = max(CURRENT_HISTORY)

            min_power = min(POWER_HISTORY)
            max_power = max(POWER_HISTORY)

            if voltage < LOW_VOLTAGE_LIMIT:

                relay = "OFF"
                charger = "OFF"
                alarm = "LOW VOLTAGE"

            elif voltage > HIGH_VOLTAGE_LIMIT:

                relay = "OFF"
                charger = "OFF"
                alarm = "HIGH VOLTAGE"

            elif current > MAX_CURRENT_LIMIT:

                relay = "OFF"
                charger = "OFF"
                alarm = "OVER CURRENT"
                  
            else:

                relay = "ON"
                charger = "ON"
                alarm = "NORMAL"

            save_fault(
                voltage,
                current,
                power,
                relay,
                charger,
                alarm
            )
            data = {

                "device_id": device_id,

                "voltage": voltage,
                "min_voltage": min_voltage,
                "max_voltage": max_voltage,

                "current": current,
                "min_current": min_current,
                "max_current": max_current,

                "power": power,
                "min_power": min_power,
                "max_power": max_power,

                "relay": relay,
                "charger": charger,
                "alarm": alarm,

                "date": datetime.now().strftime("%d-%m-%Y"),
                "time": datetime.now().strftime("%H:%M:%S")

            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            self.wfile.write(json.dumps(data).encode())
        elif self.path.startswith("/faultlog"):
            parsed_url = urlparse(self.path)

            params = parse_qs(parsed_url.query)

            device_id = params.get("device", ["TVS001"])[0]    
            connection = sqlite3.connect(DATABASE)

            cursor = connection.cursor()

            cursor.execute("""
    SELECT
        date,
        time,
        voltage,
        current,
        power,
        alarm,
        relay
    FROM fault_log
    WHERE device_id = ?
    ORDER BY id DESC
""", (device_id,))

            rows = cursor.fetchall()

            connection.close()

            fault_list = []

            for row in rows:

                fault_list.append({

                    "date": row[0],
                    "time": row[1],
                    "voltage": row[2],
                    "current": row[3],
                    "power": row[4],
                    "alarm": row[5],
                    "relay": row[6]

                })

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            self.wfile.write(json.dumps(fault_list).encode())
        elif self.path == "/exportexcel":

            connection = sqlite3.connect(DATABASE)

            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    date,
                    time,
                    voltage,
                    current,
                    power,
                    alarm,
                    relay
                FROM fault_log
                ORDER BY id DESC
            """)

            rows = cursor.fetchall()

            connection.close()

            workbook = Workbook()

            sheet = workbook.active

            sheet.title = "Fault Log"

            sheet.append([
                "Date",
                "Time",
                "Voltage",
                "Current",
                "Power",
                "Alarm",
                "Relay"
            ])

            for row in rows:
                sheet.append(row)

            file_name = "SVMS_Fault_Log.xlsx"
            print("Export Started")
            workbook.save(file_name)

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()

            self.wfile.write(f"Excel Saved: {file_name}".encode())
        elif self.path == "/":

            self.send_response(302)
            self.send_header("Location", "/login")
            self.end_headers()

        

            with open("../Dashboard/login.html", "rb") as file:
                self.wfile.write(file.read())
        else:

            self.send_response(404)
            self.end_headers()
            # ==========================================
# START SERVER
# ==========================================

server = HTTPServer(("localhost", 5000), SVMSHandler)

print("========================================")
print("      SVMS SERVER V3.1 STARTED")
print("========================================")
print("Device ID :", DEVICE_ID)
print("API       : http://localhost:5000/data")
print("Database  : Connected")
print("========================================")

try:

    server.serve_forever()

except KeyboardInterrupt:

    print("\nServer Stopped Successfully")

    server.server_close()