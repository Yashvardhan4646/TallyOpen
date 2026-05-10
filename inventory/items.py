from database.db import cursor, db

def add_item(name, quantity, price):

    sql = """
    INSERT INTO inventory(
        item_name,
        quantity,
        price
    )
    VALUES(%s, %s, %s)
    """

    cursor.execute(sql, (name, quantity, price))

    db.commit()

    print("Item Added")


def view_inventory():

    cursor.execute("SELECT * FROM inventory")

    items = cursor.fetchall()

    print("\nINVENTORY\n")

    for item in items:
        print(item)


def update_inventory(
    item_id,
    name,
    quantity,
    price
):

    sql = """
    UPDATE inventory
    SET item_name=%s,
        quantity=%s,
        price=%s
    WHERE id=%s
    """

    values = (
        name,
        quantity,
        price,
        item_id
    )

    cursor.execute(sql, values)

    db.commit()

    print("Inventory Updated")


def delete_inventory(item_id):

    sql = "DELETE FROM inventory WHERE id=%s"

    cursor.execute(sql, (item_id,))

    db.commit()

    print("Inventory Deleted")