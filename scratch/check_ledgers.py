import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yash@root",
    database="tally_clone"
)
cursor = db.cursor()
cursor.execute("SELECT ledger_name, ledger_group, balance FROM ledgers")
for row in cursor.fetchall():
    print(row)
