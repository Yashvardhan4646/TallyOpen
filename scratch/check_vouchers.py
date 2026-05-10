import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yash@root",
    database="tally_clone"
)
cursor = db.cursor()
cursor.execute("SELECT voucher_type, amount, narration FROM vouchers")
for row in cursor.fetchall():
    print(row)
