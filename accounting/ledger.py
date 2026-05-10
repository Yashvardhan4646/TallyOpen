from database.db import cursor, db

def create_ledger(company_id, name, group_name, balance=0):

    sql = """
    INSERT INTO ledgers(
        company_id,
        ledger_name,
        ledger_group,
        balance
    )
    VALUES(%s, %s, %s, %s)
    """

    values = (
        company_id,
        name,
        group_name,
        balance
    )

    cursor.execute(sql, values)

    db.commit()

    print("Ledger Created")


def view_ledgers():

    cursor.execute("SELECT * FROM ledgers")

    data = cursor.fetchall()

    print("\nLEDGERS\n")

    for row in data:
        print(row)


def update_ledger(
    ledger_id,
    name,
    group_name,
    balance
):

    sql = """
    UPDATE ledgers
    SET ledger_name=%s,
        ledger_group=%s,
        balance=%s
    WHERE id=%s
    """

    values = (
        name,
        group_name,
        balance,
        ledger_id
    )

    cursor.execute(sql, values)

    db.commit()

    print("Ledger Updated")


def delete_ledger(ledger_id):

    sql = "DELETE FROM ledgers WHERE id=%s"

    cursor.execute(sql, (ledger_id,))

    db.commit()

    print("Ledger Deleted")