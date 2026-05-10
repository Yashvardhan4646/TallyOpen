from flask import Flask, render_template, request, redirect, url_for, send_file, session
from database.db import cursor, db
import database.models
import webbrowser
import threading
import io
import pandas as pd
from datetime import datetime
import google.generativeai as genai
import json

app = Flask(__name__)
app.secret_key = "tally_pro_super_secret_key"

# ─── Helper: load settings row from DB as a dict ───────────────────────────
def get_settings():
    cursor.execute("SELECT id,business_name,business_address,gst_number,currency,fy_start,gemini_api_key,smtp_email,smtp_password,ocr_api_key,show_tooltips FROM settings WHERE id=1")
    row = cursor.fetchone()
    if not row:
        return {}
    return {
        "id": row[0],
        "business_name":    row[1] or "My Business",
        "business_address": row[2] or "",
        "gst_number":       row[3] or "",
        "currency":         row[4] or "INR",
        "fy_start":         row[5],
        "gemini_api_key":   row[6] or "",
        "smtp_email":       row[7] or "",
        "smtp_password":    row[8] or "",
        "ocr_api_key":      row[9] or "",
        "show_tooltips":    row[10] if row[10] is not None else 1,
    }

@app.before_request
def check_login():
    if request.endpoint in ['login', 'static']:
        return
    if 'user_id' not in session:
        return redirect(url_for('login'))

# Inject zip, round, and live settings into every template
@app.context_processor
def inject_globals():
    s = get_settings()
    return dict(zip=zip, round=round, g_settings=s)

# =====================================
# DASHBOARD (OVERVIEW)
# =====================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cursor.execute("SELECT id FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user[0]
            session['username'] = username
            return redirect(url_for('dashboard'))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/")
def dashboard():
    cursor.execute("SELECT SUM(balance) FROM ledgers")
    res = cursor.fetchone()
    total_balance = float(res[0] or 0) if res else 0.0

    # Trend Data (Monthly)
    cursor.execute("SELECT DATE_FORMAT(date, '%b'), SUM(amount) FROM vouchers GROUP BY DATE_FORMAT(date, '%b') ORDER BY MIN(date) ASC LIMIT 12")
    trend_data = cursor.fetchall()
    trend_labels = [t[0] for t in trend_data]
    trend_values = [float(t[1]) for t in trend_data]

    # Inventory Distribution
    cursor.execute("SELECT item_name, quantity FROM inventory ORDER BY quantity DESC LIMIT 5")
    inv_dist = cursor.fetchall()
    inv_labels = [i[0] for i in inv_dist]
    inv_values = [i[1] for i in inv_dist]

    # Stats for progress bars
    cursor.execute("SELECT SUM(balance) FROM ledgers WHERE ledger_group='Sundry Debtors'")
    res = cursor.fetchone()
    receivables = float(res[0] or 0) if res else 0.0
    cursor.execute("SELECT SUM(balance) FROM ledgers WHERE ledger_group='Cash-in-hand' OR ledger_group='Bank Accounts'")
    res = cursor.fetchone()
    liquid_cash = float(res[0] or 0) if res else 0.0
    
    # Recent activity
    cursor.execute("""
        SELECT v.date, v.voucher_type, l.ledger_name, v.amount 
        FROM vouchers v
        JOIN ledgers l ON v.dr_ledger_id = l.id
        ORDER BY v.id DESC LIMIT 5
    """)
    recent_activity = cursor.fetchall()

    return render_template("index.html", 
        total_balance=total_balance, 
        trend_labels=trend_labels, trend_values=trend_values,
        inv_labels=inv_labels, inv_values=inv_values,
        receivables=receivables, liquid_cash=liquid_cash,
        recent_activity=recent_activity)

# =====================================
# COMPANIES MODULE
# =====================================
import json

@app.route("/companies")
def view_companies():
    cursor.execute("SELECT * FROM companies")
    raw_companies = cursor.fetchall()
    companies = []
    gst_count = 0
    states = set()
    for comp in raw_companies:
        addr = comp[2]
        display_addr = addr
        if comp[3]: gst_count += 1
        try:
            addr_data = json.loads(addr)
            if isinstance(addr_data, dict):
                states.add(addr_data.get('state'))
                parts = [addr_data.get('line1'), addr_data.get('line2'), addr_data.get('city'), addr_data.get('state')]
                display_addr = ", ".join([p for p in parts if p and str(p).strip()])
        except:
            pass
        companies.append((comp[0], comp[1], display_addr, comp[3], addr))
    
    return render_template("companies.html", 
        companies=companies, 
        gst_count=gst_count, 
        state_count=len(states))

@app.route("/add-company", methods=["POST"])
def add_company():
    name = request.form["name"]
    addr1 = request.form.get("address_line1", "")
    addr2 = request.form.get("address_line2", "")
    state = request.form.get("state", "")
    city = request.form.get("city", "")
    
    address_dict = {
        "line1": addr1,
        "line2": addr2,
        "state": state,
        "city": city
    }
    address = json.dumps(address_dict)
    
    gst = request.form["gst"]
    cursor.execute("INSERT INTO companies (name, address, gst_number) VALUES (%s, %s, %s)", (name, address, gst))
    db.commit()
    return redirect(url_for("view_companies"))

@app.route("/edit-company/<int:id>", methods=["POST"])
def edit_company(id):
    name = request.form["name"]
    addr1 = request.form.get("address_line1", "")
    addr2 = request.form.get("address_line2", "")
    state = request.form.get("state", "")
    city = request.form.get("city", "")
    
    address_dict = {
        "line1": addr1,
        "line2": addr2,
        "state": state,
        "city": city
    }
    address = json.dumps(address_dict)
    
    gst = request.form["gst"]
    cursor.execute("UPDATE companies SET name=%s, address=%s, gst_number=%s WHERE id=%s", (name, address, gst, id))
    db.commit()
    return redirect(url_for("view_companies"))

@app.route("/delete-company/<int:id>", methods=["GET", "POST"])
def delete_company(id):
    cursor.execute("DELETE FROM companies WHERE id=%s", (id,))
    db.commit()
    return redirect(url_for("view_companies"))

@app.route("/settings")
def settings():
    cursor.execute("SELECT * FROM settings WHERE id = 1")
    s = cursor.fetchone()
    # 0:id, 1:name, 2:address, 3:gst, 4:currency, 5:fy_start, 6:api_key
    return render_template("settings.html", settings=s)

@app.route("/update-settings", methods=["POST"])
def update_settings():
    name    = request.form.get("business_name")
    gst     = request.form.get("gst_number")
    addr    = request.form.get("address")
    cur     = request.form.get("currency")
    fy      = request.form.get("fy_start") or None
    show_tips = 1 if request.form.get("show_tooltips") == "on" else 0
    # Keys tab fields
    g_key   = request.form.get("gemini_api_key") or None
    s_email = request.form.get("smtp_email") or None
    s_pass  = request.form.get("smtp_password") or None
    ocr_key = request.form.get("ocr_api_key") or None

    # Only update key fields if user actually typed something (don't overwrite with blank)
    existing = get_settings()
    if not g_key:   g_key   = existing.get("gemini_api_key") or None
    if not s_email: s_email = existing.get("smtp_email") or None
    if not s_pass:  s_pass  = existing.get("smtp_password") or None
    if not ocr_key: ocr_key = existing.get("ocr_api_key") or None

    cursor.execute("""
        UPDATE settings
        SET business_name=%s, gst_number=%s, business_address=%s, currency=%s, fy_start=%s,
            gemini_api_key=%s, smtp_email=%s, smtp_password=%s, ocr_api_key=%s, show_tooltips=%s
        WHERE id=1
    """, (name, gst, addr, cur, fy, g_key, s_email, s_pass, ocr_key, show_tips))
    db.commit()
    return redirect(url_for("settings", success="Settings saved! Changes applied everywhere."))

@app.route("/update-password", methods=["POST"])
def update_password():
    user_id = session.get('user_id')
    current = request.form["current_password"]
    new_pass = request.form["new_password"]
    confirm = request.form["confirm_password"]
    
    if new_pass != confirm:
        return redirect(url_for("settings", error="Passwords do not match"))
        
    cursor.execute("SELECT id FROM users WHERE id=%s AND password=%s", (user_id, current))
    if cursor.fetchone():
        cursor.execute("UPDATE users SET password=%s WHERE id=%s", (new_pass, user_id))
        db.commit()
        return redirect(url_for("settings", success="Password updated successfully"))
    
    return redirect(url_for("settings", error="Incorrect current password"))

# =====================================
# LEDGERS MODULE
# =====================================
@app.route("/ledgers")
def view_ledgers():
    cursor.execute("SELECT * FROM ledgers")
    raw_ledgers = cursor.fetchall()
    
    # Standardize data types: 0:id, 1:company_id, 2:ledger_name, 3:ledger_group, 4:balance, 5:email
    ledgers = []
    for l in raw_ledgers:
        ledger = list(l)
        ledger[4] = float(l[4] or 0) # balance
        ledgers.append(ledger)
    
    total_ledger_balance = sum(l[4] for l in ledgers)
    debtors_count = len([l for l in ledgers if l[3] == 'Sundry Debtors'])
    creditors_count = len([l for l in ledgers if l[3] == 'Sundry Creditors'])
    
    # Chart data
    cursor.execute("SELECT ledger_group, SUM(balance) FROM ledgers GROUP BY ledger_group")
    group_data = cursor.fetchall()
    group_labels = [g[0] for g in group_data]
    group_values = [float(g[1] or 0) for g in group_data]
    
    cursor.execute("SELECT id, name FROM companies")
    companies = cursor.fetchall()
    return render_template("ledgers.html", 
        ledgers=ledgers, 
        companies=companies,
        total_ledger_balance=total_ledger_balance,
        debtors_count=debtors_count,
        creditors_count=creditors_count,
        group_labels=group_labels,
        group_values=group_values)

@app.route("/add-ledger", methods=["POST"])
def add_ledger():
    company_id = request.form.get("company_id", 1) # Default to 1 if missing
    name = request.form["name"]
    group = request.form["group"]
    balance = request.form.get("balance") or request.form.get("opening_balance") or 0
    email = request.form.get("email", "")
    cursor.execute("INSERT INTO ledgers (company_id, ledger_name, ledger_group, balance, email) VALUES (%s, %s, %s, %s, %s)", (company_id, name, group, balance, email))
    db.commit()
    return redirect(url_for("view_ledgers"))

@app.route("/edit-ledger/<int:id>", methods=["POST"])
def edit_ledger(id):
    name = request.form["name"]
    group = request.form["group"]
    balance = request.form["balance"]
    email = request.form.get("email", "")
    cursor.execute("UPDATE ledgers SET ledger_name=%s, ledger_group=%s, balance=%s, email=%s WHERE id=%s", (name, group, balance, email, id))
    db.commit()
    return redirect(url_for("view_ledgers"))

@app.route("/delete-ledger/<int:id>", methods=["GET", "POST"])
def delete_ledger(id):
    cursor.execute("DELETE FROM ledgers WHERE id=%s", (id,))
    db.commit()
    return redirect(url_for("view_ledgers"))

# =====================================
# INVENTORY MODULE
# =====================================
@app.route("/inventory")
def view_inventory():
    cursor.execute("SELECT * FROM inventory")
    raw_inventory = cursor.fetchall()
    
    # Standardize data types: 0:id, 1:item_name, 2:quantity, 3:price, 4:unit
    inventory = []
    for i in raw_inventory:
        item = list(i)
        item[2] = float(i[2] or 0) # qty
        item[3] = float(i[3] or 0) # price
        inventory.append(item)
    
    total_stock_value = sum(i[2] * i[3] for i in inventory)
    low_stock_count = len([i for i in inventory if i[2] < 5])
    qty_sum = sum(i[2] for i in inventory)
    avg_rate = (total_stock_value / qty_sum) if qty_sum > 0 else 0.0
    
    # Chart data
    inv_labels = [i[1] for i in inventory[:7]]
    inv_values = [i[2] * i[3] for i in inventory[:7]]
    
    return render_template("inventory.html", 
        inventory=inventory, 
        total_stock_value=total_stock_value,
        low_stock_count=low_stock_count,
        avg_rate=avg_rate,
        inv_labels=inv_labels,
        inv_values=inv_values)

@app.route("/add-inventory", methods=["POST"])
def add_inventory():
    name = request.form["name"]
    quantity = request.form["quantity"]
    unit = request.form.get("unit", "Pcs")
    rate = request.form["rate"]
    cursor.execute("INSERT INTO inventory (item_name, quantity, unit, price) VALUES (%s, %s, %s, %s)", (name, quantity, unit, rate))
    db.commit()
    return redirect(url_for("view_inventory"))

@app.route("/edit-inventory/<int:id>", methods=["POST"])
def edit_inventory(id):
    name = request.form["name"]
    quantity = request.form["quantity"]
    unit = request.form.get("unit", "Pcs")
    rate = request.form["rate"]
    cursor.execute("UPDATE inventory SET item_name=%s, quantity=%s, unit=%s, price=%s WHERE id=%s", (name, quantity, unit, rate, id))
    db.commit()
    return redirect(url_for("view_inventory"))

@app.route("/delete-inventory/<int:id>", methods=["GET", "POST"])
def delete_inventory(id):
    cursor.execute("DELETE FROM inventory WHERE id=%s", (id,))
    db.commit()
    return redirect(url_for("view_inventory"))

# =====================================
# VOUCHERS MODULE
# =====================================
@app.route("/vouchers")
def view_vouchers():
    cursor.execute("""
        SELECT v.id, v.voucher_type, l1.ledger_name as dr_ledger, l2.ledger_name as cr_ledger, v.amount, v.narration, v.date
        FROM vouchers v 
        JOIN ledgers l1 ON v.dr_ledger_id = l1.id
        JOIN ledgers l2 ON v.cr_ledger_id = l2.id
        ORDER BY v.id DESC
    """)
    raw_vouchers = cursor.fetchall()
    vouchers = []
    for v in raw_vouchers:
        vc = list(v)
        vc[4] = float(v[4] or 0) # amount
        vouchers.append(vc)
    
    total_credited = sum(v[4] for v in vouchers if v[1] in ['Receipt', 'Sales'])
    total_debited = sum(v[4] for v in vouchers if v[1] in ['Payment', 'Purchase'])
    trade_count = len(vouchers)
    
    cursor.execute("SELECT id, ledger_name FROM ledgers")
    ledgers = cursor.fetchall()
    cursor.execute("SELECT id, item_name, quantity FROM inventory")
    inventory_items = cursor.fetchall()
    today_date = datetime.now().strftime("%Y-%m-%d")
    return render_template("vouchers.html", 
        vouchers=vouchers, 
        ledgers=ledgers, 
        inventory_items=inventory_items, 
        today_date=today_date,
        total_credited=total_credited,
        total_debited=total_debited,
        trade_count=trade_count)

@app.route("/add-voucher", methods=["POST"])
def add_voucher():
    v_type = request.form["type"]
    dr_ledger_id = request.form["dr_ledger_id"]
    cr_ledger_id = request.form["cr_ledger_id"]
    amount = float(request.form["amount"])
    narration = request.form["narration"]
    v_date = request.form.get("date") or datetime.now().strftime("%Y-%m-%d")
    
    item_id = request.form.get("item_id")
    quantity = request.form.get("quantity")
    
    # Clean empty values to None for database safety
    if not item_id or item_id == "": item_id = None
    if not quantity or quantity == "": quantity = 0
    else: quantity = float(quantity)

    # 1. Update Ledgers (Double Entry)
    # Debit Side (Increase Asset/Expense, Decrease Liability/Income)
    # For simplicity in this clone, we treat balance as a net value where DR adds and CR subtracts
    cursor.execute("UPDATE ledgers SET balance = balance + %s WHERE id = %s", (amount, dr_ledger_id))
    cursor.execute("UPDATE ledgers SET balance = balance - %s WHERE id = %s", (amount, cr_ledger_id))

    # 2. Update Inventory (Interconnection)
    if item_id and quantity > 0:
        if v_type == "Sales":
            cursor.execute("UPDATE inventory SET quantity = quantity - %s WHERE id = %s", (quantity, item_id))
        elif v_type == "Purchase":
            cursor.execute("UPDATE inventory SET quantity = quantity + %s WHERE id = %s", (quantity, item_id))

    # 3. Save Voucher
    sql = """
        INSERT INTO vouchers (voucher_type, dr_ledger_id, cr_ledger_id, amount, narration, date, item_id, item_quantity) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (v_type, dr_ledger_id, cr_ledger_id, amount, narration, v_date, item_id, quantity))
    
    db.commit()
    return redirect(url_for("view_vouchers"))

@app.route("/delete-voucher/<int:id>", methods=["GET", "POST"])
def delete_voucher(id):
    cursor.execute("SELECT dr_ledger_id, cr_ledger_id, amount, voucher_type, item_id, item_quantity FROM vouchers WHERE id = %s", (id,))
    v = cursor.fetchone()
    if v:
        dr_id, cr_id, amount, v_type, item_id, qty = v
        # Reverse Ledger Balances
        cursor.execute("UPDATE ledgers SET balance = balance - %s WHERE id = %s", (amount, dr_id))
        cursor.execute("UPDATE ledgers SET balance = balance + %s WHERE id = %s", (amount, cr_id))
        
        # Reverse Inventory
        if item_id and qty > 0:
            if v_type == "Sales":
                cursor.execute("UPDATE inventory SET quantity = quantity + %s WHERE id = %s", (qty, item_id))
            elif v_type == "Purchase":
                cursor.execute("UPDATE inventory SET quantity = quantity - %s WHERE id = %s", (qty, item_id))

    cursor.execute("DELETE FROM vouchers WHERE id=%s", (id,))
    db.commit()
    return redirect(url_for("view_vouchers"))

# =====================================
# REPORTS MODULE
# =====================================
@app.route("/reports")
def reports():
    # 1. Balance Sheet Data (Assets vs Liabilities)
    cursor.execute("SELECT ledger_group, SUM(balance) FROM ledgers GROUP BY ledger_group")
    balance_sheet = cursor.fetchall()

    # 2. Profit & Loss Data (Voucher-based for better UX)
    cursor.execute("SELECT SUM(amount) FROM vouchers WHERE voucher_type IN ('Sales', 'Receipt')")
    income = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(amount) FROM vouchers WHERE voucher_type IN ('Purchase', 'Payment')")
    expense = cursor.fetchone()[0] or 0
    
    # Financial logic
    expense_abs = abs(float(expense))
    income_abs = float(income)
    profit = income_abs - expense_abs
    profit_margin = (profit / income_abs * 100) if income_abs > 0 else 0
    expense_ratio = (expense_abs / income_abs * 100) if income_abs > 0 else 0

    # Trial Balance
    cursor.execute("SELECT ledger_name, balance FROM ledgers")
    trial_balance = cursor.fetchall()
    total_tb = sum(float(row[1]) for row in trial_balance)

    # Chart Data (Monthly trend for reports)
    cursor.execute("SELECT DATE_FORMAT(date, '%b'), SUM(amount) FROM vouchers WHERE voucher_type IN ('Receipt', 'Sales') GROUP BY DATE_FORMAT(date, '%b') ORDER BY MIN(date) ASC")
    inc_trend = cursor.fetchall()
    inc_labels = [t[0] for t in inc_trend]
    inc_values = [float(t[1]) for t in inc_trend]

    cursor.execute("SELECT DATE_FORMAT(date, '%b'), SUM(amount) FROM vouchers WHERE voucher_type IN ('Payment', 'Purchase') GROUP BY DATE_FORMAT(date, '%b') ORDER BY MIN(date) ASC")
    exp_trend = cursor.fetchall()
    exp_values = [float(t[1]) for t in exp_trend]

    return render_template(
        "reports.html",
        balance_sheet=balance_sheet,
        income=income_abs,
        expense=expense_abs,
        profit=profit,
        profit_margin=profit_margin,
        expense_ratio=expense_ratio,
        trial_balance=trial_balance,
        total_tb=total_tb,
        inc_labels=inc_labels,
        inc_values=inc_values,
        exp_values=exp_values,
        bs_labels=[b[0] for b in balance_sheet],
        bs_values=[float(b[1] or 0) for b in balance_sheet]
    )

# =====================================
# BILLING & GST MODULE
# =====================================
@app.route("/billing")
def billing():
    cursor.execute("""
        SELECT v.id, v.date, l.ledger_name, v.amount, v.narration, l.email 
        FROM vouchers v 
        LEFT JOIN ledgers l ON v.dr_ledger_id = l.id
        WHERE v.voucher_type='Sales'
        ORDER BY v.id DESC
    """)
    invoices = cursor.fetchall()
    
    cursor.execute("SELECT id, name FROM companies")
    companies = cursor.fetchall()
    
    cursor.execute("SELECT id, item_name, quantity, price FROM inventory")
    inventory_items = cursor.fetchall()
    
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    return render_template("billing.html", 
        invoices=invoices, 
        companies=companies,
        inventory=inventory_items, 
        today_date=today_date)

@app.route("/generate-invoice", methods=["POST"])
def generate_invoice():
    company_id = request.form["company_id"]
    customer_name = request.form["customer_name"]
    customer_gst = request.form["customer_gst"]
    item_id = request.form["item_id"]
    quantity = float(request.form["quantity"])
    gst_rate = float(request.form["gst_rate"])
    
    # 1. Get Item Price
    cursor.execute("SELECT item_name, price, quantity FROM inventory WHERE id = %s", (item_id,))
    item = cursor.fetchone()
    if not item:
        return redirect(url_for("billing"))
    
    item_name = item[0]
    unit_price = float(item[1])
    stock_qty = float(item[2])
    
    # 2. Calculate Amounts
    subtotal = unit_price * quantity
    gst_amount = subtotal * (gst_rate / 100)
    total_amount = subtotal + gst_amount
    
    # 3. Handle Ledgers (Simplified: Dr Customer/Cash, Cr Sales)
    # Check if customer ledger exists, else use a generic one or create
    cursor.execute("SELECT id FROM ledgers WHERE ledger_name = %s LIMIT 1", (customer_name,))
    customer_row = cursor.fetchone()
    if customer_row:
        customer_ledger_id = customer_row[0]
    else:
        # Create a new ledger for this customer under Sundry Debtors
        cursor.execute("INSERT INTO ledgers (company_id, ledger_name, ledger_group, balance) VALUES (%s, %s, %s, %s)", 
                      (company_id, customer_name, 'Sundry Debtors', 0))
        customer_ledger_id = cursor.lastrowid
        
    # Find Sales Account
    cursor.execute("SELECT id FROM ledgers WHERE ledger_group = 'Sales Accounts' LIMIT 1")
    sales_row = cursor.fetchone()
    if sales_row:
        sales_ledger_id = sales_row[0]
    else:
        # Create one if missing
        cursor.execute("INSERT INTO ledgers (company_id, ledger_name, ledger_group, balance) VALUES (%s, %s, %s, %s)", 
                      (company_id, 'Sales Account', 'Sales Accounts', 0))
        sales_ledger_id = cursor.lastrowid
        
    # 4. Record Voucher
    narration = f"Sales of {item_name} (Qty: {quantity})"
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        INSERT INTO vouchers (voucher_type, dr_ledger_id, cr_ledger_id, amount, narration, date, item_id, item_quantity)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, ('Sales', customer_ledger_id, sales_ledger_id, total_amount, narration, today, item_id, quantity))
    
    # 5. Update Balances (Double Entry: Dr Customer, Cr Sales)
    cursor.execute("UPDATE ledgers SET balance = balance + %s WHERE id = %s", (total_amount, customer_ledger_id))
    cursor.execute("UPDATE ledgers SET balance = balance - %s WHERE id = %s", (total_amount, sales_ledger_id))
    
    # 6. Update Inventory
    cursor.execute("UPDATE inventory SET quantity = quantity - %s WHERE id = %s", (quantity, item_id))
    
    db.commit()
    return redirect(url_for("billing"))
def export_excel():
    try:
        # Fetch Data
        cursor.execute("SELECT * FROM ledgers")
        ledgers = cursor.fetchall()
        
        cursor.execute("SELECT * FROM vouchers")
        vouchers = cursor.fetchall()
        
        cursor.execute("SELECT * FROM inventory")
        inventory = cursor.fetchall()

        # Convert to DataFrames with safe column mapping
        df_ledgers = pd.DataFrame(ledgers, columns=["ID", "Company ID", "Name", "Group", "Balance"]) if ledgers else pd.DataFrame(columns=["ID", "Company ID", "Name", "Group", "Balance"])
        df_vouchers = pd.DataFrame(vouchers, columns=["ID", "Date", "Type", "DR_ID", "CR_ID", "Amount", "Narration", "Item_ID", "Item_Qty"]) if vouchers else pd.DataFrame(columns=["ID", "Date", "Type", "DR_ID", "CR_ID", "Amount", "Narration", "Item_ID", "Item_Qty"])
        df_inventory = pd.DataFrame(inventory, columns=["ID", "Item Name", "Quantity", "Price"]) if inventory else pd.DataFrame(columns=["ID", "Item Name", "Quantity", "Price"])

        # Create Excel in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_ledgers.to_excel(writer, index=False, sheet_name='Ledgers')
            df_vouchers.to_excel(writer, index=False, sheet_name='Vouchers')
            df_inventory.to_excel(writer, index=False, sheet_name='Inventory')

        output.seek(0)
        
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=f"TallyClone_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        )
    except Exception as e:
        print(f"EXPORT ERROR: {e}")
        return f"Error generating Excel: {str(e)}", 500

import requests
from utils.pdf_generator import generate_invoice_pdf
from utils.email_sender import send_invoice_email

@app.route("/email-report-png", methods=["POST"])
def email_report_png():
    import os
    if 'image' not in request.files or 'email' not in request.form:
        return {"error": "Missing data"}, 400

    file = request.files['image']
    to_email = request.form['email']

    if not os.path.exists("static/reports"):
        os.makedirs("static/reports")

    filename = f"static/reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    file.save(filename)

    from utils.email_sender import send_report_email
    s = get_settings()
    success = send_report_email(to_email, filename, settings=s)

    if success:
        return {"success": True}
    else:
        return {"error": "Email failed. Please check your SMTP settings in Settings → Keys tab."}, 500

# =====================================
# INTEGRATIONS: PDF EMAIL & OCR
# =====================================
@app.route("/send-invoice-email", methods=["POST"])
def send_invoice_email_route():
    voucher_id = request.form.get("voucher_id")
    target_email = request.form.get("email")

    if not voucher_id or not target_email:
        return redirect(url_for("billing"))

    cursor.execute("""
        SELECT v.id, v.date, l.ledger_name, l.email, v.amount, v.narration
        FROM vouchers v
        LEFT JOIN ledgers l ON v.dr_ledger_id = l.id
        WHERE v.id = %s
    """, (voucher_id,))
    v = cursor.fetchone()

    if v:
        s = get_settings()
        invoice_data = {
            'id': v[0],
            'date': v[1],
            'customer_name': v[2],
            'email': target_email,
            'amount': v[4],
            'narration': v[5]
        }
        pdf_path = generate_invoice_pdf(invoice_data, settings=s)
        send_invoice_email(target_email, pdf_path, voucher_id, settings=s)

    return redirect(url_for("billing"))

@app.route("/ocr-scan", methods=["POST"])
def ocr_scan():
    if 'file' not in request.files:
        return {"error": "No file uploaded"}, 400

    file = request.files['file']
    s = get_settings()
    ocr_key = s.get("ocr_api_key") or "helloworld"   # 'helloworld' is OCR.space free tier key

    try:
        response = requests.post(
            'https://api.ocr.space/parse/image',
            files={'file': (file.filename, file.stream, file.mimetype)},
            data={'apikey': ocr_key, 'language': 'eng'}
        )
        result = response.json()
        
        if result.get('IsErroredOnProcessing'):
            return {"error": "Failed to process image"}, 500
            
        parsed_text = result['ParsedResults'][0]['ParsedText']
        
        import re
        
        # 1. Extract Amount
        total_amount = 0
        
        # Try finding explicit keywords first
        amount_match = re.search(r'(?i)(?:total|amount|rs\.?|inr|₹|paid|sum)[\s:-]*([\d,]+(?:\.\d{1,2})?)', parsed_text)
        if amount_match:
            try:
                total_amount = float(amount_match.group(1).replace(',', ''))
            except:
                pass
                
        if total_amount == 0:
            # Fallback 1: Look specifically for numbers formatted as currency (with decimals)
            decimal_amounts = re.findall(r'\b\d{1,3}(?:,\d{3})*\.\d{2}\b', parsed_text)
            if decimal_amounts:
                total_amount = max([float(a.replace(',', '')) for a in decimal_amounts])
            else:
                # Fallback 2: Any number, but filter out long IDs/Phone numbers (>6 digits)
                amounts = re.findall(r'\b\d+\b', parsed_text)
                valid_amounts = [float(a) for a in amounts if len(a) <= 6]
                if valid_amounts:
                    total_amount = max(valid_amounts)
                    
        # 2. Extract Date (DD/MM/YYYY or YYYY-MM-DD)
        extracted_date = ""
        date_match = re.search(r'\b(\d{2})[/-](\d{2})[/-](\d{4})\b', parsed_text)
        if date_match:
            d, m, y = date_match.groups()
            extracted_date = f"{y}-{m}-{d}"
        else:
            date_match2 = re.search(r'\b(\d{4})[/-](\d{2})[/-](\d{2})\b', parsed_text)
            if date_match2:
                y, m, d = date_match2.groups()
                extracted_date = f"{y}-{m}-{d}"
                
        # 3. Extract Narration (First non-empty line usually is the Merchant)
        lines = [line.strip() for line in parsed_text.split('\n') if len(line.strip()) > 2]
        narration = "Scanned Receipt"
        if len(lines) > 0:
            narration = f"Receipt from: {lines[0]}"
            
        return {
            "text": parsed_text, 
            "extracted_amount": total_amount,
            "extracted_date": extracted_date,
            "extracted_narration": narration
        }
        
    except Exception as e:
        print("OCR Error:", e)
        return {"error": str(e)}, 500

@app.route("/ask-ai", methods=["POST"])
def ask_ai():
    data = request.json
    user_query = data.get("query", "")

    if not user_query:
        return {"error": "No query provided"}, 400

    s = get_settings()
    api_key = s.get("gemini_api_key", "")
    if not api_key:
        return {"error": "No Gemini API key set. Please go to Settings → Keys and add your Google Gemini API key."}, 400

    try:
        genai.configure(api_key=api_key)

        cursor.execute("SELECT ledger_name, ledger_group, balance FROM ledgers")
        ledgers = cursor.fetchall()
        ledger_text = "ACCOUNTS:\n" + "\n".join([f"{l[0]} ({l[1]}): Rs.{l[2]}" for l in ledgers])

        cursor.execute("SELECT item_name, quantity, price FROM inventory")
        inventory = cursor.fetchall()
        inv_text = "STOCK:\n" + "\n".join([f"{i[0]}: {i[1]} units at Rs.{i[2]}" for i in inventory])

        cursor.execute("SELECT date, voucher_type, amount FROM vouchers ORDER BY id DESC LIMIT 20")
        vouchers = cursor.fetchall()
        voucher_text = "RECENT ENTRIES:\n" + "\n".join([f"{v[0]} - {v[1]}: Rs.{v[2]}" for v in vouchers])

        system_prompt = f"""You are a friendly accounting helper for {s.get('business_name','this business')}.
Here is the current business data:

{ledger_text}

{inv_text}

{voucher_text}

Answer the user's question in very simple, plain language. Avoid accounting jargon. You can use markdown."""

        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(f"{system_prompt}\n\nQuestion: {user_query}")
        return {"answer": response.text}
    except Exception as e:
        print("Gemini API Error:", e)
        return {"error": str(e)}, 500

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    import os
    # Open browser once
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        threading.Timer(1.5, open_browser).start()
    app.run(debug=True)