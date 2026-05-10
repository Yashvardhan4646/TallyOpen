from database.db import cursor, db

def create_company(name, address, gst):

    sql = """
    INSERT INTO companies(name, address, gst_number)
    VALUES(%s, %s, %s)
    """

    cursor.execute(sql, (name, address, gst))

    db.commit()

    print("Company Created")


def view_companies():

    cursor.execute("SELECT * FROM companies")

    data = cursor.fetchall()

    print("\nCOMPANIES\n")

    for row in data:
        print(row)


def update_company(company_id, name, address, gst):

    sql = """
    UPDATE companies
    SET name=%s,
        address=%s,
        gst_number=%s
    WHERE id=%s
    """

    values = (name, address, gst, company_id)

    cursor.execute(sql, values)

    db.commit()

    print("Company Updated")


def delete_company(company_id):

    sql = "DELETE FROM companies WHERE id=%s"

    cursor.execute(sql, (company_id,))

    db.commit()

    print("Company Deleted")