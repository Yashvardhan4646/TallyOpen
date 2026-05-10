from fpdf import FPDF
import os

def sanitize_text(text):
    if text is None:
        return ""
    return str(text).replace('₹', 'Rs. ').encode('ascii', 'ignore').decode('ascii')

def generate_invoice_pdf(invoice_data, settings=None):
    """
    Generates a professional, well-designed PDF invoice.
    Uses business name, address, and GST number from the settings dict.
    """
    s = settings or {}
    business_name    = sanitize_text(s.get("business_name", "My Business"))
    business_address = sanitize_text(s.get("business_address", ""))
    gst_number       = sanitize_text(s.get("gst_number", ""))
    currency_symbol  = "Rs."  # PDF is ASCII-safe

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ── DESIGN HEADER ──
    # Top accent line
    pdf.set_fill_color(124, 111, 237) # Accent Purple
    pdf.rect(0, 0, 210, 5, 'F')

    # Title
    pdf.set_font("helvetica", "B", 24)
    pdf.set_text_color(30, 27, 75) # Dark Blue
    pdf.set_y(15)
    pdf.cell(0, 10, "INVOICE", align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(100, 100, 120)
    pdf.cell(0, 5, f"INV-{invoice_data['id']}", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"Date: {invoice_data.get('date', '')}", align="R", new_x="LMARGIN", new_y="NEXT")

    # ── SENDER INFO ──
    pdf.set_y(15)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(30, 27, 75)
    pdf.cell(100, 8, business_name, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(80, 80, 100)
    if business_address:
        for line in business_address.split('\n'):
            line = line.strip()
            if line:
                pdf.cell(100, 5, sanitize_text(line), new_x="LMARGIN", new_y="NEXT")
    
    if gst_number:
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(100, 6, f"GSTIN: {gst_number}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)

    # ── BILL TO ──
    pdf.set_fill_color(249, 250, 251) # Very Light Gray
    pdf.rect(10, pdf.get_y(), 190, 25, 'F')
    
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(124, 111, 237)
    pdf.set_x(15)
    pdf.cell(0, 8, "BILL TO", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(30, 27, 75)
    pdf.set_x(15)
    pdf.cell(0, 7, sanitize_text(invoice_data.get('customer_name', 'Valued Customer')), new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(80, 80, 100)
    pdf.set_x(15)
    pdf.cell(0, 5, sanitize_text(invoice_data.get('email', '')), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(12)

    # ── TABLE HEADER ──
    pdf.set_fill_color(30, 27, 75) # Dark Blue Header
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 10)
    
    pdf.cell(10, 10, "#", fill=True, align="C")
    pdf.cell(100, 10, " Description", fill=True)
    pdf.cell(30, 10, "Qty", fill=True, align="C")
    pdf.cell(50, 10, "Total", fill=True, align="R", new_x="LMARGIN", new_y="NEXT")

    # ── TABLE ROWS ──
    pdf.set_text_color(30, 27, 75)
    pdf.set_font("helvetica", "", 10)
    
    # Calculate row height
    item_name = invoice_data.get('item_name') or invoice_data.get('narration') or "Sales Entry"
    qty = invoice_data.get('quantity') or 1
    total_amount = float(invoice_data.get('amount') or 0)
    gst_rate = float(invoice_data.get('gst_rate') or 0)
    
    # Backward calculate taxable value and GST
    taxable_value = total_amount / (1 + (gst_rate / 100))
    gst_amount = total_amount - taxable_value
    cgst = gst_amount / 2
    sgst = gst_amount / 2
    
    pdf.cell(10, 12, "1", border="B", align="C")
    pdf.cell(100, 12, f" {sanitize_text(item_name)}", border="B")
    pdf.cell(30, 12, str(qty), border="B", align="C")
    pdf.cell(50, 12, f"{currency_symbol} {total_amount:,.2f}", border="B", align="R", new_x="LMARGIN", new_y="NEXT")

    # ── TOTALS ──
    pdf.ln(5)
    pdf.set_x(120)
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(100, 100, 120)
    
    pdf.cell(40, 7, "Taxable Value:", align="R")
    pdf.cell(40, 7, f"{currency_symbol} {taxable_value:,.2f}", align="R", new_x="LMARGIN", new_y="NEXT")
    
    if gst_rate > 0:
        pdf.set_x(120)
        pdf.cell(40, 7, f"CGST ({gst_rate/2}%):", align="R")
        pdf.cell(40, 7, f"{currency_symbol} {cgst:,.2f}", align="R", new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(120)
        pdf.cell(40, 7, f"SGST ({gst_rate/2}%):", align="R")
        pdf.cell(40, 7, f"{currency_symbol} {sgst:,.2f}", align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)
    pdf.set_x(120)
    pdf.set_draw_color(124, 111, 237)
    pdf.line(130, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    
    pdf.set_x(120)
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(30, 27, 75)
    pdf.cell(40, 10, "Grand Total:", align="R")
    
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(124, 111, 237)
    pdf.cell(40, 10, f"{currency_symbol} {total_amount:,.2f}", align="R", new_x="LMARGIN", new_y="NEXT")

    # ── SIGNATURE AREA ──
    pdf.set_y(-60)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(140, pdf.get_y(), 190, pdf.get_y())
    pdf.set_y(-55)
    pdf.set_x(140)
    pdf.set_font("helvetica", "", 9)
    pdf.set_text_color(100, 100, 120)
    pdf.cell(50, 5, "Authorized Signature", align="C", new_x="LMARGIN", new_y="NEXT")

    # ── FOOTER ──
    pdf.set_y(-30)
    pdf.set_font("helvetica", "I", 9)
    pdf.set_text_color(150, 150, 170)
    pdf.cell(0, 5, "Thank you for choosing our services!", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "This is a computer-generated document and does not require a physical signature.", align="C")

    # Save PDF
    if not os.path.exists("static/invoices"):
        os.makedirs("static/invoices")

    filename = f"static/invoices/INV-{invoice_data['id']}.pdf"
    pdf.output(filename)
    return filename
