import csv
import os
import json
from datetime import datetime

from flask import Flask, request, jsonify, send_file, send_from_directory, session
from flask_cors import CORS


app = Flask(__name__)
app.secret_key = "SVMS_SECRET_KEY_2026_CHANGE_LATER"
DASHBOARD_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "Dashboard"
    )
)
CORS(app)


live_data = {
    "voltage": 0,
    "min_voltage": 999,
    "max_voltage": 0,

    "current": 0,
    "min_current": 999,
    "max_current": 0,

    "power": 0,
    "relay": "OFF",
    "charger": "OFF",
    "alarm": "NORMAL"
}


DEVICE_ID = "TVS001"

# ==================================================
# FAULT HISTORY STORAGE
# ==================================================

FAULT_HISTORY_FILE = "fault_history.json"
FAULT_CLEAR_FILE = "fault_clear.json"

fault_log = []
live_history = []
last_alarm = "NORMAL"
active_fault = None

# ==================================================
# POWER HISTORY STORAGE
# ==================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

POWER_HISTORY_FILE = os.path.join(
    BASE_DIR,
    "power_history.json"
)

POWER_ACTIVE_FILE = os.path.join(
    BASE_DIR,
    "power_active.json"
)

power_history = []
active_power_sessions = {}


# Load completed power history
if os.path.exists(POWER_HISTORY_FILE):
    try:
        with open(
            POWER_HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            power_history = json.load(file)
    except Exception:
        power_history = []


# Load active power session
if os.path.exists(POWER_ACTIVE_FILE):
    try:
        with open(
            POWER_ACTIVE_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            active_power_sessions = json.load(file)
    except Exception:
        active_power_sessions = {}


def save_power_history():

    with open(
        POWER_HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            power_history,
            file,
            indent=4
        )


def save_active_power_sessions():

    with open(
        POWER_ACTIVE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            active_power_sessions,
            file,
            indent=4
        )

# Device-wise clear marker
fault_clear_marker = {}


# ==================================================
# LOAD FAULT HISTORY
# ==================================================

if os.path.exists(FAULT_HISTORY_FILE):

    try:

        with open(
            FAULT_HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            fault_log = json.load(file)

    except Exception:

        fault_log = []


# ==================================================
# LOAD CLEAR MARKER
# ==================================================

if os.path.exists(FAULT_CLEAR_FILE):

    try:

        with open(
            FAULT_CLEAR_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            fault_clear_marker = json.load(file)

    except Exception:

        fault_clear_marker = {}


# ==================================================
# SAVE FAULT HISTORY
# ==================================================

def save_fault_history():

    with open(
        FAULT_HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            fault_log,
            file,
            indent=4
        )


# ==================================================
# SAVE CLEAR MARKER
# ==================================================

def save_clear_marker():

    with open(
        FAULT_CLEAR_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            fault_clear_marker,
            file,
            indent=4
        )


# ==================================================
# UPDATE DATA
# ==================================================

@app.route("/update", methods=["POST"])
def update():

    global live_data
    global fault_log
    global last_alarm
    global active_fault

    data = request.get_json(force=True)

    live_data["device_id"] = data.get(
        "device_id",
        DEVICE_ID
    )

    voltage = data.get("voltage", 0)
    current = data.get("current", 0)

    # ----------------------------------------------
    # Min / Max Voltage
    # ----------------------------------------------

    if voltage < live_data["min_voltage"]:
        live_data["min_voltage"] = voltage

    if voltage > live_data["max_voltage"]:
        live_data["max_voltage"] = voltage

    # ----------------------------------------------
    # Min / Max Current
    # ----------------------------------------------

    if current < live_data["min_current"]:
        live_data["min_current"] = current

    if current > live_data["max_current"]:
        live_data["max_current"] = current

    # ----------------------------------------------
    # Live Data
    # ----------------------------------------------

    live_data["voltage"] = voltage
    live_data["current"] = current
    live_data["power"] = data.get("power", 0)
    live_data["relay"] = data.get("relay", "OFF")
    live_data["charger"] = data.get("charger", "OFF")

    # ==================================================
    # POWER SESSION START
    # ==================================================

    device_id = data.get(
        "device_id",
        DEVICE_ID
    )

    relay_status = str(
        data.get(
            "relay",
            "OFF"
        )
    ).upper()

    previous_relay = live_data.get(
        "_previous_relay",
        "OFF"
    )

    # POWER ON DETECTED
    if (
        relay_status == "ON"
        and previous_relay != "ON"
    ):

        now = datetime.now()

        voltage_now = float(
            data.get("voltage", 0) or 0
        )

        current_now = float(
            data.get("current", 0) or 0
        )

        power_now = float(
            data.get("power", 0) or 0
        )

        energy_now = data.get(
            "energy",
            0
        )

        active_power_sessions[device_id] = {

            "session_id": (
                len(power_history) + 1
            ),

            "device_id": device_id,

            "date": now.strftime(
                "%d-%m-%Y"
            ),

            "on_time": now.strftime(
                "%H:%M:%S"
            ),

            "off_time": "",

            "duration": "Running",

            "start_energy": energy_now,

            "end_energy": "",

            "units_used": 0,

            "min_voltage": voltage_now,

            "max_voltage": voltage_now,

            "avg_voltage": voltage_now,

            "min_current": current_now,

            "max_current": current_now,

            "avg_current": current_now,

            "max_load": power_now,

            "avg_load": power_now,

            "status": "RUNNING",

            "_start_timestamp": now.timestamp(),

            "_voltage_sum": voltage_now,

            "_current_sum": current_now,

            "_power_sum": power_now,

            "_reading_count": 1
        }

        save_active_power_sessions()

        print(
            "POWER SESSION STARTED:",
            device_id
        )
    # ==================================================
    # POWER SESSION LIVE UPDATE
    # ==================================================

    elif relay_status == "ON":

        if device_id in active_power_sessions:

            session_data = active_power_sessions[device_id]

            voltage_now = float(
                data.get("voltage", 0) or 0
            )

            current_now = float(
                data.get("current", 0) or 0
            )

            power_now = float(
                data.get("power", 0) or 0
            )

            # ------------------------------------------
            # MIN / MAX VOLTAGE
            # ------------------------------------------

            session_data["min_voltage"] = min(
                session_data["min_voltage"],
                voltage_now
            )

            session_data["max_voltage"] = max(
                session_data["max_voltage"],
                voltage_now
            )

            # ------------------------------------------
            # MIN / MAX CURRENT
            # ------------------------------------------

            session_data["min_current"] = min(
                session_data["min_current"],
                current_now
            )

            session_data["max_current"] = max(
                session_data["max_current"],
                current_now
            )

            # ------------------------------------------
            # MAX LOAD
            # ------------------------------------------

            session_data["max_load"] = max(
                session_data["max_load"],
                power_now
            )

            # ------------------------------------------
            # AVERAGE CALCULATION
            # ------------------------------------------

            session_data["_voltage_sum"] += voltage_now

            session_data["_current_sum"] += current_now

            session_data["_power_sum"] += power_now

            session_data["_reading_count"] += 1

            count = session_data["_reading_count"]

            session_data["avg_voltage"] = round(
                session_data["_voltage_sum"] / count,
                2
            )

            session_data["avg_current"] = round(
                session_data["_current_sum"] / count,
                2
            )

            session_data["avg_load"] = round(
                session_data["_power_sum"] / count,
                2
            )

            # ------------------------------------------
            # DURATION
            # ------------------------------------------

            now = datetime.now()

            total_seconds = int(
                now.timestamp()
                - session_data["_start_timestamp"]
            )

            hours = total_seconds // 3600

            minutes = (
                total_seconds % 3600
            ) // 60

            seconds = (
                total_seconds % 60
            )

            session_data["duration"] = (
                f"{hours}h "
                f"{minutes}m "
                f"{seconds}s"
            )

            # ------------------------------------------
            # PZEM ENERGY
            # ------------------------------------------

            energy_now = data.get(
                "energy",
                None
            )

            if energy_now is not None:

                try:

                    energy_now = float(
                        energy_now
                    )

                    session_data["end_energy"] = (
                        energy_now
                    )

                    start_energy = float(
                        session_data[
                            "start_energy"
                        ]
                    )

                    session_data["units_used"] = round(
                        max(
                            0,
                            energy_now - start_energy
                        ),
                        3
                    )

                except Exception:
                    pass

            # ------------------------------------------
            # SAVE UPDATED SESSION
            # ------------------------------------------

            save_active_power_sessions()
    # ==================================================
    # POWER SESSION CLOSE
    # ==================================================

    elif (
        relay_status == "OFF"
        and previous_relay == "ON"
    ):

        if device_id in active_power_sessions:

            session_data = active_power_sessions[
                device_id
            ]

            now = datetime.now()

            voltage_now = float(
                data.get("voltage", 0) or 0
            )

            current_now = float(
                data.get("current", 0) or 0
            )

            power_now = float(
                data.get("power", 0) or 0
            )

            # ------------------------------------------
            # FINAL MIN / MAX VALUES
            # ------------------------------------------

            session_data["min_voltage"] = min(
                session_data["min_voltage"],
                voltage_now
            )

            session_data["max_voltage"] = max(
                session_data["max_voltage"],
                voltage_now
            )

            session_data["min_current"] = min(
                session_data["min_current"],
                current_now
            )

            session_data["max_current"] = max(
                session_data["max_current"],
                current_now
            )

            session_data["max_load"] = max(
                session_data["max_load"],
                power_now
            )

            # ------------------------------------------
            # FINAL DURATION
            # ------------------------------------------

            total_seconds = int(
                now.timestamp()
                - session_data["_start_timestamp"]
            )

            hours = total_seconds // 3600

            minutes = (
                total_seconds % 3600
            ) // 60

            seconds = (
                total_seconds % 60
            )

            session_data["duration"] = (
                f"{hours}h "
                f"{minutes}m "
                f"{seconds}s"
            )

            session_data["off_time"] = (
                now.strftime("%H:%M:%S")
            )

            # ------------------------------------------
            # FINAL ENERGY
            # ------------------------------------------

            energy_now = data.get(
                "energy",
                None
            )

            if energy_now is not None:

                try:

                    energy_now = float(
                        energy_now
                    )

                    session_data["end_energy"] = (
                        energy_now
                    )

                    start_energy = float(
                        session_data[
                            "start_energy"
                        ]
                    )

                    session_data["units_used"] = round(
                        max(
                            0,
                            energy_now - start_energy
                        ),
                        3
                    )

                except Exception:
                    pass

            # ------------------------------------------
            # SESSION COMPLETED
            # ------------------------------------------

            session_data["status"] = "COMPLETED"

            # Remove internal calculation values
            completed_session = {
                key: value
                for key, value
                in session_data.items()
                if not key.startswith("_")
            }

            power_history.append(
                completed_session
            )

            save_power_history()

            del active_power_sessions[
                device_id
            ]

            save_active_power_sessions()

            print(
                "POWER SESSION CLOSED:",
                device_id
            )

    print("DATA :", data)


    # ==================================================
    # VOLTAGE ALARM
    # ==================================================

    if voltage < 180:

        current_alarm = "LOW VOLTAGE"

    elif voltage > 250:

        current_alarm = "HIGH VOLTAGE"

    else:

        current_alarm = "NORMAL"

    live_data["alarm"] = current_alarm

    # AUTOMATIC RELAY OFF ON VOLTAGE FAULT
    if current_alarm != "NORMAL":
        live_data["relay"] = "OFF"

    # ==================================================
    # FAULT START
    # ==================================================

    if current_alarm != "NORMAL" and last_alarm == "NORMAL":

        start_time = datetime.now()

        active_fault = {
            "device_id": DEVICE_ID,
            "date": start_time.strftime("%d-%m-%Y"),
            "fault_start": start_time.strftime("%H:%M:%S"),
            "start_voltage": voltage,
            "fault": current_alarm,
            "relay": "OFF",
            "fault_resolve": "",
            "resolve_voltage": "",
            "fault_duration": "",
            "status": "ACTIVE"
        }

        fault_log.append(active_fault)

        save_fault_history()

    # ==================================================
    # FAULT RESOLVED
    # ==================================================

    elif current_alarm == "NORMAL" and last_alarm != "NORMAL":

        resolve_time = datetime.now()

        if active_fault is not None:

            start_time = datetime.strptime(
                active_fault["date"] + " " +
                active_fault["fault_start"],
                "%d-%m-%Y %H:%M:%S"
            )

            duration = resolve_time - start_time

            total_seconds = int(
                duration.total_seconds()
            )

            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            if hours > 0:

                duration_text = (
                    f"{hours} hr "
                    f"{minutes} min "
                    f"{seconds} sec"
                )

            else:

                duration_text = (
                    f"{minutes} min "
                    f"{seconds} sec"
                )

            active_fault["fault_resolve"] = (
                resolve_time.strftime("%H:%M:%S")
            )

            active_fault["resolve_voltage"] = voltage
            active_fault["fault_duration"] = duration_text
            active_fault["relay"] = "ON"
            active_fault["status"] = "RESOLVED"

            save_fault_history()

            active_fault = None

    # ==================================================
    # UPDATE PREVIOUS ALARM
    # ==================================================

    last_alarm = current_alarm

    return jsonify({"status": "OK"})


# ==================================================
# LIVE DATA
# ==================================================

# ==================================================
# MANUAL RELAY CONTROL
# ==================================================

@app.route("/relay", methods=["POST"])
def relay_control():

    global live_data
    global active_power_sessions
    global power_history

    data = request.get_json(force=True)

    device_id = data.get(
        "device_id",
        DEVICE_ID
    )

    relay = str(
        data.get(
            "relay",
            "OFF"
        )
    ).upper()

    if relay not in ["ON", "OFF"]:
        return jsonify({
            "status": "ERROR",
            "message": "Invalid relay status"
        }), 400

    # Current live values
    voltage_now = float(
        live_data.get("voltage", 0) or 0
    )

    current_now = float(
        live_data.get("current", 0) or 0
    )

    power_now = float(
        live_data.get("power", 0) or 0
    )

    energy_now = float(
        live_data.get("energy", 0) or 0
    )

    now = datetime.now()

    # ==================================================
    # MANUAL POWER ON
    # ==================================================

    if relay == "ON":

        live_data["relay"] = "ON"

        if device_id not in active_power_sessions:

            active_power_sessions[device_id] = {

                "session_id": len(power_history) + 1,

                "device_id": device_id,

                "date": now.strftime("%d-%m-%Y"),

                "on_time": now.strftime("%H:%M:%S"),

                "off_time": "",

                "duration": "Running",

                "start_energy": energy_now,

                "end_energy": "",

                "units_used": 0,

                "min_voltage": voltage_now,

                "max_voltage": voltage_now,

                "avg_voltage": voltage_now,

                "min_current": current_now,

                "max_current": current_now,

                "avg_current": current_now,

                "max_load": power_now,

                "avg_load": power_now,

                "status": "RUNNING",

                "_start_timestamp": now.timestamp(),

                "_voltage_sum": voltage_now,

                "_current_sum": current_now,

                "_power_sum": power_now,

                "_reading_count": 1
            }

            save_active_power_sessions()

            print(
                "MANUAL POWER SESSION STARTED:",
                device_id
            )

    # ==================================================
    # MANUAL POWER OFF
    # ==================================================

    elif relay == "OFF":

        live_data["relay"] = "OFF"

        if device_id in active_power_sessions:

            session_data = active_power_sessions[device_id]

            total_seconds = int(
                now.timestamp()
                - session_data["_start_timestamp"]
            )

            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            session_data["duration"] = (
                f"{hours}h "
                f"{minutes}m "
                f"{seconds}s"
            )

            session_data["off_time"] = (
                now.strftime("%H:%M:%S")
            )

            # Final readings
            session_data["min_voltage"] = min(
                session_data["min_voltage"],
                voltage_now
            )

            session_data["max_voltage"] = max(
                session_data["max_voltage"],
                voltage_now
            )

            session_data["min_current"] = min(
                session_data["min_current"],
                current_now
            )

            session_data["max_current"] = max(
                session_data["max_current"],
                current_now
            )

            session_data["max_load"] = max(
                session_data["max_load"],
                power_now
            )

            # Final energy
            session_data["end_energy"] = energy_now

            session_data["units_used"] = round(
                max(
                    0,
                    energy_now -
                    float(session_data["start_energy"])
                ),
                3
            )

            session_data["status"] = "COMPLETED"

            completed_session = {
                key: value
                for key, value in session_data.items()
                if not key.startswith("_")
            }

            power_history.append(
                completed_session
            )

            save_power_history()

            del active_power_sessions[device_id]

            save_active_power_sessions()

            print(
                "MANUAL POWER SESSION CLOSED:",
                device_id
            )

    live_data["_previous_relay"] = relay

    return jsonify({
        "status": "OK",
        "device_id": device_id,
        "relay": relay
    })


@app.route("/data", methods=["GET"])
def data():

    device = request.args.get("device", "").strip()

    if not device:
        return jsonify([])

    if live_data.get("device_id") != device:
        return jsonify([])

    return jsonify(live_data)


# ==================================================
# FAULT LOG
# ==================================================

@app.route("/faultlog", methods=["GET"])
def faultlog():

    device = request.args.get("device", "").strip()

    if not device:
        return jsonify([])

    clear_position = int(
        fault_clear_marker.get(device, 0)
    )

    filtered_faults = []

    device_count = 0

    for item in fault_log:

        if item.get("device_id") != device:
            continue

        device_count += 1

        if device_count > clear_position:
            filtered_faults.append(item)

    return jsonify(filtered_faults)

# ==================================================
# POWER HISTORY API
# ==================================================

@app.route("/powerhistory", methods=["GET"])
def powerhistory():

    device_id = request.args.get(
        "device",
        ""
    ).strip()

    if device_id == "":
        return jsonify([])

    result = []

    # ------------------------------------------
    # COMPLETED POWER SESSIONS
    # ------------------------------------------

    for session in power_history:

        if session.get(
            "device_id"
        ) == device_id:

            result.append(session)

    # ------------------------------------------
    # CURRENTLY RUNNING SESSION
    # ------------------------------------------

    if device_id in active_power_sessions:

        running_session = (
            active_power_sessions[
                device_id
            ]
        )

        clean_session = {
            key: value
            for key, value
            in running_session.items()
            if not key.startswith("_")
        }

        result.insert(
            0,
            clean_session
        )

    return jsonify(result)

# ==================================================
# POWER HISTORY EXCEL EXPORT
# ==================================================

@app.route("/exportpower")
def exportpower():

    device_id = request.args.get(
        "device",
        ""
    ).strip()

    if device_id == "":
        return "Device ID is required", 400

    selected_sessions = []

    # ------------------------------------------
    # FIND DEVICE POWER HISTORY
    # ------------------------------------------

    for session in power_history:

        if session.get(
            "device_id"
        ) == device_id:

            selected_sessions.append(
                session
            )

    # ------------------------------------------
    # CREATE CSV FILE
    # ------------------------------------------

    filename = (
        "Power_History_"
        + device_id
        + "_"
        + datetime.now().strftime(
            "%d-%m-%Y_%H-%M-%S"
        )
        + ".csv"
    )

    filepath = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        filename
    )

    with open(
        filepath,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(file)

        # Header
        writer.writerow([
            "Device ID",
            "Date",
            "ON Time",
            "OFF Time",
            "Duration",
            "Start Energy (kWh)",
            "End Energy (kWh)",
            "Units Used (kWh)",
            "Min Voltage (V)",
            "Max Voltage (V)",
            "Avg Voltage (V)",
            "Min Current (A)",
            "Max Current (A)",
            "Avg Current (A)",
            "Max Load (W)",
            "Avg Load (W)",
            "Status"
        ])

        # Data
        for session in selected_sessions:

            writer.writerow([
                session.get(
                    "device_id",
                    ""
                ),

                session.get(
                    "date",
                    ""
                ),

                session.get(
                    "on_time",
                    ""
                ),

                session.get(
                    "off_time",
                    ""
                ),

                session.get(
                    "duration",
                    ""
                ),

                session.get(
                    "start_energy",
                    ""
                ),

                session.get(
                    "end_energy",
                    ""
                ),

                session.get(
                    "units_used",
                    ""
                ),

                session.get(
                    "min_voltage",
                    ""
                ),

                session.get(
                    "max_voltage",
                    ""
                ),

                session.get(
                    "avg_voltage",
                    ""
                ),

                session.get(
                    "min_current",
                    ""
                ),

                session.get(
                    "max_current",
                    ""
                ),

                session.get(
                    "avg_current",
                    ""
                ),

                session.get(
                    "max_load",
                    ""
                ),

                session.get(
                    "avg_load",
                    ""
                ),

                session.get(
                    "status",
                    ""
                )
            ])

    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename
    )

    # ------------------------------------------
    # COMPLETED POWER SESSIONS
    # ------------------------------------------

    for session in power_history:

        if session.get(
            "device_id"
        ) == device_id:

            result.append(session)

    # ------------------------------------------
    # CURRENTLY RUNNING SESSION
    # ------------------------------------------

    if device_id in active_power_sessions:

        running_session = (
            active_power_sessions[
                device_id
            ]
        )

        clean_session = {
            key: value
            for key, value
            in running_session.items()
            if not key.startswith("_")
        }

        result.insert(
            0,
            clean_session
        )

    return jsonify(result)

# ==================================================
# CLEAR FAULT LOG
# ==================================================

@app.route("/clearfaultlog", methods=["POST"])
def clearfaultlog():

    device = request.args.get("device", "").strip()

    if not device:
        return jsonify({
            "status": "ERROR",
            "message": "Device ID is required"
        }), 400

    device_count = 0

    for item in fault_log:

        if item.get("device_id") == device:
            device_count += 1

    fault_clear_marker[device] = device_count

    save_clear_marker()

    return jsonify({
        "status": "OK",
        "message": "Fault Log cleared"
    })


# ==================================================
# EXPORT FAULT LOG
# ==================================================

@app.route("/exportexcel")
def exportexcel():

    filename = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "Fault_Log_" + datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".csv"
)

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Device ID",
            "Date",
            "Fault Start",
            "Start Voltage",
            "Fault",
            "Relay",
            "Fault Resolve",
            "Resolve Voltage",
            "Fault Duration",
            "Status"
        ])

        for item in fault_log:

            writer.writerow([
                item.get("device_id", ""),
                item.get("date", ""),
                item.get("fault_start", ""),
                item.get("start_voltage", ""),
                item.get("fault", ""),
                item.get("relay", ""),
                item.get("fault_resolve", ""),
                item.get("resolve_voltage", ""),
                item.get("fault_duration", ""),
                item.get("status", "")
            ])

    return send_file(
        filename,
        as_attachment=True,
        download_name="Fault_Log.csv"
    )


# ==================================================
# EXPORT LIVE DATA
# ==================================================

@app.route("/exportlivedata")
def exportlivedata():

    filename = os.path.join(
        os.getcwd(),
        "LiveData.csv"
    )

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Date",
            "Time",
            "Voltage",
            "Min Voltage",
            "Max Voltage",
            "Current",
            "Min Current",
            "Max Current",
            "Power",
            "Relay",
            "Charger",
            "Alarm"
        ])

        writer.writerow([
            datetime.now().strftime("%d-%m-%Y"),
            datetime.now().strftime("%H:%M:%S"),
            live_data["voltage"],
            live_data["min_voltage"],
            live_data["max_voltage"],
            live_data["current"],
            live_data["min_current"],
            live_data["max_current"],
            live_data["power"],
            live_data["relay"],
            live_data["charger"],
            live_data["alarm"]
        ])

    return send_file(
        filename,
        as_attachment=True,
        download_name="Live_Data.csv"
    )
# ==================================================
# EXPORT FULL REPORT
# ==================================================

@app.route("/exportfullreport")
def exportfullreport():

    device = request.args.get("device", "").strip()

    if not device:
        return "Device ID is required", 400

    filename = "Full_Report.csv"

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(file)

        # ------------------------------------------
        # CSV HEADER
        # ------------------------------------------

        writer.writerow([
            "Device ID",
            "Date",
            "Time",
            "Voltage",
            "Min Voltage",
            "Max Voltage",
            "Current",
            "Min Current",
            "Max Current",
            "Power",
            "Relay",
            "Charger",
            "Alarm",
            "Fault Start",
            "Start Voltage",
            "Fault",
            "Fault Resolve",
            "Resolve Voltage",
            "Fault Duration",
            "Status"
        ])

        # ------------------------------------------
        # LIVE DATA
        # ------------------------------------------

        if live_data.get("device_id") == device:

            writer.writerow([
                device,
                datetime.now().strftime("%d-%m-%Y"),
                datetime.now().strftime("%H:%M:%S"),
                live_data.get("voltage", ""),
                live_data.get("min_voltage", ""),
                live_data.get("max_voltage", ""),
                live_data.get("current", ""),
                live_data.get("min_current", ""),
                live_data.get("max_current", ""),
                live_data.get("power", ""),
                live_data.get("relay", ""),
                live_data.get("charger", ""),
                live_data.get("alarm", ""),
                "",
                "",
                "",
                "",
                "",
                "",
                ""
            ])

        # ------------------------------------------
        # FAULT LOG
        # ------------------------------------------

        for item in fault_log:

            if item.get("device_id") != device:
                continue

            writer.writerow([
                device,
                item.get("date", ""),
                item.get("fault_start", ""),
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                item.get("relay", ""),
                "",
                item.get("fault", ""),
                item.get("fault_start", ""),
                item.get("start_voltage", ""),
                item.get("fault", ""),
                item.get("fault_resolve", ""),
                item.get("resolve_voltage", ""),
                item.get("fault_duration", ""),
                item.get("status", "")
            ])

    return send_file(
        filename,
        as_attachment=True,
        download_name="Full_Report_" + device + ".csv"
    )
# ==================================================
# LOGIN
# ==================================================

USERNAME = "admin"
PASSWORD = "1234"

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json(force=True)

    username = data.get("username", "")
    password = data.get("password", "")

    if username == USERNAME and password == PASSWORD:

        session["logged_in"] = True
        session["username"] = username

        return jsonify({
            "status": "success"
        })

    return jsonify({
        "status": "error",
        "message": "Invalid Username or Password"
    }), 401

# ==================================================
# START SERVER
# ==================================================
# ==================================================
# WEBSITE
# ==================================================

@app.route("/")
def website_home():
    return send_from_directory(DASHBOARD_DIR, "login.html")


@app.route("/<path:filename>")
def website_files(filename):
    return send_from_directory(DASHBOARD_DIR, filename)

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=False
    )