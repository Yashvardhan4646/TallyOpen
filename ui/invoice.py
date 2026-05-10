from reportlab.pdfgen import canvas
from accounting.gst import calculate_gst

def generate_invoice(
    customer_name,
    item_name,
    amount,
    gst_percent
):

    gst_data = calculate_gst(amount, gst_percent)

    pdf = canvas.Canvas("invoice.pdf")

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(200, 800, "TAX INVOICE")

    pdf.setFont("Helvetica", 12)

    pdf.drawString(50, 740, f"Customer: {customer_name}")
    pdf.drawString(50, 710, f"Item: {item_name}")

    pdf.drawString(50, 680, f"Amount: ₹{amount}")
    pdf.drawString(50, 650, f"GST: ₹{gst_data['gst']}")
    pdf.drawString(50, 620, f"Total: ₹{gst_data['total']}")

    pdf.save()

    print("Invoice Generated")