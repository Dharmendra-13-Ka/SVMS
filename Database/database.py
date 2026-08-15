import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "svms.db")

connection = sqlite3.connect(DB_FILE)

cursor = connection.cursor()

# ============================
# ADMIN TABLE
# ============================

cursor.execute("""
CREATE TABLE IF NOT EXISTS admin(

id INTEGER PRIMARY KEY AUTOINCREMENT,

username TEXT UNIQUE,

password TEXT,

name TEXT,

mobile TEXT,

email TEXT,

created_on TEXT

)
""")

# ============================
# CUSTOMER TABLE
# ============================

cursor.execute("""
CREATE TABLE IF NOT EXISTS customer(

id INTEGER PRIMARY KEY AUTOINCREMENT,

customer_name TEXT,

mobile TEXT,

email TEXT,

address TEXT,

created_on TEXT

)
""")

print("Part 1 Completed")
# ============================
# DEVICE TABLE
# ============================

cursor.execute("""
CREATE TABLE IF NOT EXISTS device(

id INTEGER PRIMARY KEY AUTOINCREMENT,

device_id TEXT UNIQUE,

customer_id INTEGER,

device_name TEXT,

location TEXT,

firmware_version TEXT,

status TEXT,

created_on TEXT

)
""")

# ============================
# LIVE DATA TABLE
# ============================

cursor.execute("""
CREATE TABLE IF NOT EXISTS live_data(

id INTEGER PRIMARY KEY AUTOINCREMENT,

device_id TEXT,

date TEXT,

time TEXT,

voltage REAL,

current REAL,

power REAL,

relay TEXT,

charger TEXT,

alarm TEXT

)
""")

# ============================
# FAULT LOG TABLE
# ============================

cursor.execute("""
CREATE TABLE IF NOT EXISTS fault_log(

id INTEGER PRIMARY KEY AUTOINCREMENT,

device_id TEXT,

date TEXT,

time TEXT,

voltage REAL,

current REAL,

power REAL,

relay TEXT,

charger TEXT,

alarm TEXT,

fault_start TEXT,

fault_end TEXT,

duration TEXT

)
""")

print("Part 2 Completed")
# ============================
# RELAY LOG TABLE
# ============================

cursor.execute("""
CREATE TABLE IF NOT EXISTS relay_log(

id INTEGER PRIMARY KEY AUTOINCREMENT,

device_id TEXT,

date TEXT,

time TEXT,

command TEXT,

status TEXT,

user_name TEXT

)
""")

# ============================
# SETTINGS TABLE
# ============================

cursor.execute("""
CREATE TABLE IF NOT EXISTS settings(

id INTEGER PRIMARY KEY AUTOINCREMENT,

device_id TEXT,

low_voltage REAL,

high_voltage REAL,

max_current REAL,

auto_mode TEXT

)
""")

# ============================
# DEFAULT ADMIN
# ============================

cursor.execute("""
INSERT OR IGNORE INTO admin
(username,password,name,mobile,email,created_on)

VALUES
(
'admin',
'admin123',
'System Admin',
'9999999999',
'admin@svms.com',
datetime('now')
)
""")

connection.commit()

connection.close()

print("===================================")
print("SVMS DATABASE CREATED SUCCESSFULLY")
print("Version : 1.0")
print("===================================")