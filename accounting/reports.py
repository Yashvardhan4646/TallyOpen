from database.db import cursor

def balance_sheet():

    cursor.execute("""
    SELECT ledger_group, SUM(balance)
    FROM ledgers
    GROUP BY ledger_group
    """)

    data = cursor.fetchall()

    print("\nBALANCE SHEET\n")

    for row in data:
        print(f"{row[0]} : ₹{row[1]}")

def trial_balance():

    cursor.execute("""
    SELECT ledger_name, balance
    FROM ledgers
    """)

    data = cursor.fetchall()

    print("\nTRIAL BALANCE\n")

    total = 0

    for row in data:
        print(f"{row[0]} : ₹{row[1]}")
        total += float(row[1])

    print("\nTOTAL :", total)

def profit_loss():

    cursor.execute("""
    SELECT SUM(balance)
    FROM ledgers
    WHERE ledger_group='Income'
    """)

    income = cursor.fetchone()[0] or 0

    cursor.execute("""
    SELECT SUM(balance)
    FROM ledgers
    WHERE ledger_group='Expense'
    """)

    expense = cursor.fetchone()[0] or 0

    profit = income - expense

    print("\nPROFIT & LOSS\n")

    print("Income :", income)
    print("Expense :", expense)
    print("Net Profit :", profit)