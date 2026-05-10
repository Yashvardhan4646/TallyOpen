from database.db import cursor, db

def add_voucher(
    voucher_type,
    ledger_id,
    amount,
    narration
):

    sql = """
    INSERT INTO vouchers(
        voucher_type,
        ledger_id,
        amount,
        narration
    )
    VALUES(%s, %s, %s, %s)
    """

    values = (
        voucher_type,
        ledger_id,
        amount,
        narration
    )

    cursor.execute(sql, values)

    db.commit()

    print("Voucher Added")


def view_vouchers():

    cursor.execute("SELECT * FROM vouchers")

    data = cursor.fetchall()

    print("\nVOUCHERS\n")

    for row in data:
        print(row)


def delete_voucher(voucher_id):

    sql = "DELETE FROM vouchers WHERE id=%s"

    cursor.execute(sql, (voucher_id,))

    db.commit()

    print("Voucher Deleted")