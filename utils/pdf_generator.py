from fpdf import FPDF
import os

def sanitize_text(text):
    if text is None:
        return ""
    return str(text).replace('₹', 'Rs. ').encode('ascii', 'ignore').decode('ascii')

def generate_invoice_pdf(invoice_data, settings=None):
    """
    Generates a professional PDF invoice.
    Uses business name, address, and GST number from the settings dict (from DB).
    """
    s = settings or {}
    business_name    = sanitize_text(s.get("business_name", "My Business"))
    business_address = sanitize_text(s.get("business_address", ""))
    gst_number       = sanitize_text(s.get("gst_number", ""))
    currency_symbol  = "Rs."  # PDF is ASCII-safe

    pdf = FPDF()
    pdf.add_page()

    # ── Header bar ──
    pdf.set_fill_color(124, 111, 237)   # accent purple
    pdf.rect(0, 0, 210, 28, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 18)
    pdf.set_y(8)
    pdf.cell(0, 12, "TAX INVOICE / BILL", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_fill_color(255, 255, 255)
    pdf.set_text_color(30, 27, 75)
    pdf.ln(6)

    # ── Company Info (left) & Invoice Details (right) ──
    pdf.set_font("helvetica", "B", 13)
    pdf.cell(100, 8, business_name, new_y="LAST")

    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 8, f"Invoice #: INV-{invoice_data['id']}", align="R", new_x="LMARGIN", new_y="NEXT")

    if business_address:
        for line in business_address.split('\n'):
            line = line.strip()
            if line:
                pdf.set_font("helvetica", "", 10)
                pdf.cell(100, 6, sanitize_text(line), new_y="LAST")
                pdf.cell(0, 6, "", align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("helvetica", "", 10)
    pdf.cell(100, 6, f"Date: {invoice_data.get('date', '')}", new_y="LAST")
    pdf.cell(0, 6, "", align="R", new_x="LMARGIN", new_y="NEXT")

    if gst_number:
        pdf.cell(0, 6, f"GST Number: {gst_number}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(8)
    pdf.set_draw_color(200, 200, 220)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    # ── Bill To ──
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 7, "Bill To:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 7, f"Customer: {sanitize_text(invoice_data.get('customer_name', 'Cash Customer'))}", new_x="LMARGIN", new_y="NEXT")
    if invoice_data.get('email'):
        pdf.cell(0, 7, f"Email: {sanitize_text(invoice_data.get('email'))}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    # ── Table ──
    pdf.set_fill_color(238, 237, 255)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(140, 10, "Description", border=1, fill=True)
    pdf.cell(50, 10, "Total Amount", border=1, fill=True, align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("helvetica", "", 11)
    pdf.cell(140, 10, sanitize_text(invoice_data.get('narration', 'Sale')), border=1)
    pdf.cell(50, 10, f"{currency_symbol} {invoice_data.get('amount', '0.00')}", border=1, align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(16)

    # ── Footer ──
    pdf.set_font("helvetica", "I", 9)
    pdf.set_text_color(120, 120, 140)
    pdf.cell(0, 8, "Thank you for your business! This is a computer-generated invoice.", align="C")

    # Save PDF
    if not os.path.exists("static/invoices"):
        os.makedirs("static/invoices")

    filename = f"static/invoices/INV-{invoice_data['id']}.pdf"
    pdf.output(filename)
    return filename
