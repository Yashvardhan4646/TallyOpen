from database.db import cursor, db

def purchase_item(item_id, quantity):

    sql = """
    UPDATE inventory
    SET quantity = quantity + %s
    WHERE id = %s
    """

    cursor.execute(sql, (quantity, item_id))
    db.commit()

    print("Purchase Entry Added")