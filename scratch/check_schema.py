import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yash@root",
    database="tally_clone"
)
cursor = db.cursor()
cursor.execute("DESCRIBE inventory")
for row in cursor.fetchall():
    print(row)
