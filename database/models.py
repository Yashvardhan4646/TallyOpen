from database.db import cursor, db

# Companies
cursor.execute("""
CREATE TABLE IF NOT EXISTS companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    address TEXT,
    gst_number VARCHAR(100)
)
""")

# Ledgers
cursor.execute("""
CREATE TABLE IF NOT EXISTS ledgers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT,
    ledger_name VARCHAR(255),
    ledger_group VARCHAR(255),
    balance DECIMAL(12,2),
    email VARCHAR(255)
)
""")

# Alter table for existing databases
try:
    cursor.execute("ALTER TABLE ledgers ADD COLUMN email VARCHAR(255)")
except:
    pass

# Inventory
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(255),
    quantity INT,
    unit VARCHAR(50) DEFAULT 'Pcs',
    price DECIMAL(12,2)
)
""")

try:
    cursor.execute("ALTER TABLE inventory ADD COLUMN unit VARCHAR(50) DEFAULT 'Pcs'")
except:
    pass

# Vouchers
cursor.execute("""
CREATE TABLE IF NOT EXISTS vouchers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    voucher_type VARCHAR(255),
    dr_ledger_id INT,
    cr_ledger_id INT,
    amount DECIMAL(12,2),
    narration TEXT,
    item_id INT DEFAULT NULL,
    item_quantity DECIMAL(12,2) DEFAULT 0.00
)
""")

try:
    cursor.execute("ALTER TABLE vouchers MODIFY COLUMN item_quantity DECIMAL(12,2) DEFAULT 0.00")
except:
    pass

# Settings Table — includes all user-supplied keys/config
cursor.execute("""
CREATE TABLE IF NOT EXISTS settings (
    id INT PRIMARY KEY,
    business_name VARCHAR(255) DEFAULT 'My Business',
    business_address TEXT,
    gst_number VARCHAR(100) DEFAULT '',
    currency VARCHAR(10) DEFAULT 'INR',
    fy_start DATE,
    gemini_api_key VARCHAR(512),
    smtp_email VARCHAR(255),
    smtp_password VARCHAR(512),
    ocr_api_key VARCHAR(255),
    show_tooltips INT DEFAULT 1
)
""")

# Add new key columns to existing settings tables (safe for upgrades)
for col_sql in [
    "ALTER TABLE settings ADD COLUMN gemini_api_key VARCHAR(512)",
    "ALTER TABLE settings ADD COLUMN smtp_email VARCHAR(255)",
    "ALTER TABLE settings ADD COLUMN smtp_password VARCHAR(512)",
    "ALTER TABLE settings ADD COLUMN ocr_api_key VARCHAR(255)",
    "ALTER TABLE settings ADD COLUMN show_tooltips INT DEFAULT 1",
]:
    try:
        cursor.execute(col_sql)
    except:
        pass

# Remove old ai_api_key column if it exists
try:
    cursor.execute("ALTER TABLE settings DROP COLUMN ai_api_key")
except:
    pass

# Initialize settings row if not exists
cursor.execute("SELECT id FROM settings WHERE id = 1")
if not cursor.fetchone():
    cursor.execute("INSERT INTO settings (id, business_name, show_tooltips) VALUES (1, 'My Business', 1)")

# Users Table for Auth
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    password VARCHAR(255)
)
""")

# Initialize default user if empty
cursor.execute("SELECT id FROM users")
if not cursor.fetchone():
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")

db.commit()