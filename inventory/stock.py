from database.db import cursor, db

def update_stock(item_id, quantity):

    sql = """
    UPDATE inventory
    SET quantity = quantity + %s
    WHERE id = %s
    """

    cursor.execute(sql, (quantity, item_id))
    db.commit()

    print("Stock Updated")

def view_stock():

    cursor.execute("SELECT * FROM inventory")

    items = cursor.fetchall()

    print("\nSTOCK SUMMARY\n")

    for item in items:
        print(item)