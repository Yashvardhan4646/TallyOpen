from database.db import cursor, db
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):

    hashed = hash_password(password)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100),
        password TEXT
    )
    """)

    sql = """
    INSERT INTO users(username, password)
    VALUES(%s, %s)
    """

    cursor.execute(sql, (username, hashed))
    db.commit()

    print("User Created")

def login(username, password):

    hashed = hash_password(password)

    sql = """
    SELECT * FROM users
    WHERE username=%s AND password=%s
    """

    cursor.execute(sql, (username, hashed))

    user = cursor.fetchone()

    if user:
        print("Login Success")
        return True

    print("Invalid Credentials")
    return False