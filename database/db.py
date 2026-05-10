import mysql.connector
import json
import os
import sys

# Load DB credentials from keys.json (user-supplied, never committed to git)
_keys_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "keys.json")

if not os.path.exists(_keys_path):
    print("\n" + "="*60)
    print("  ERROR: keys.json not found!")
    print("  Copy keys.example.json to keys.json and fill in your")
    print("  MySQL database details before starting the app.")
    print("="*60 + "\n")
    sys.exit(1)

with open(_keys_path, "r") as f:
    _keys = json.load(f)

_db_cfg = _keys.get("db", {})

try:
    db = mysql.connector.connect(
        host=_db_cfg.get("host", "localhost"),
        user=_db_cfg.get("user", "root"),
        password=_db_cfg.get("password", ""),
        database=_db_cfg.get("database", "tallyopen")
    )
    cursor = db.cursor()
except mysql.connector.Error as e:
    print("\n" + "="*60)
    print(f"  ERROR: Could not connect to MySQL database!")
    print(f"  Details: {e}")
    print("  Check your keys.json and make sure MySQL is running.")
    print("="*60 + "\n")
    sys.exit(1)