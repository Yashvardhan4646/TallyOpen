import pandas as pd
from database.db import cursor

def export_ledgers():

    cursor.execute("SELECT * FROM ledgers")

    data = cursor.fetchall()

    df = pd.DataFrame(data, columns=[
        "ID",
        "Company ID",
        "Ledger Name",
        "Group",
        "Balance"
    ])

    df.to_csv("ledgers.csv", index=False)

    print("Exported to ledgers.csv")

def export_inventory():

    cursor.execute("SELECT * FROM inventory")

    data = cursor.fetchall()

    df = pd.DataFrame(data, columns=[
        "ID",
        "Item Name",
        "Quantity",
        "Price"
    ])

    df.to_csv("inventory.csv", index=False)

    print("Inventory Exported")