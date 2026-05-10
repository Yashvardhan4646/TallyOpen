import smtplib
from email.message import EmailMessage
import os

def send_invoice_email(to_email, pdf_path, invoice_id, settings=None):
    """
    Sends an email with the PDF invoice attached via Gmail SMTP.
    Reads SMTP credentials from the settings dict (from DB), not hardcoded.
    """
    smtp_email    = (settings or {}).get("smtp_email", "")
    smtp_password = (settings or {}).get("smtp_password", "")
    business_name = (settings or {}).get("business_name", "Our Business")

    if not smtp_email or not smtp_password:
        print("Email sending skipped: no SMTP email/password configured in Settings → Keys.")
        return False

    try:
        msg = EmailMessage()
        msg['Subject'] = f'Your Bill / Invoice — INV-{invoice_id}'
        msg['From']    = smtp_email
        msg['To']      = to_email
        msg.set_content(
            f'Dear Customer,\n\n'
            f'Please find your bill (invoice) attached to this email.\n\n'
            f'Thank you for your business!\n\n'
            f'— {business_name}'
        )

        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
            msg.add_attachment(pdf_data, maintype='application', subtype='pdf',
                               filename=os.path.basename(pdf_path))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(smtp_email, smtp_password)
            smtp.send_message(msg)

        print(f"Successfully sent invoice INV-{invoice_id} to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_report_email(to_email, png_path, settings=None):
    """
    Sends an email with the PNG report snapshot attached via Gmail SMTP.
    """
    smtp_email    = (settings or {}).get("smtp_email", "")
    smtp_password = (settings or {}).get("smtp_password", "")
    business_name = (settings or {}).get("business_name", "Our Business")

    if not smtp_email or not smtp_password:
        print("Email sending skipped: no SMTP email/password configured in Settings → Keys.")
        return False

    try:
        msg = EmailMessage()
        msg['Subject'] = 'Your Financial Report Snapshot'
        msg['From']    = smtp_email
        msg['To']      = to_email
        msg.set_content(
            f'Hello,\n\nPlease find the requested financial report snapshot attached.\n\n'
            f'Best regards,\n{business_name}'
        )

        with open(png_path, 'rb') as f:
            img_data = f.read()
            msg.add_attachment(img_data, maintype='image', subtype='png',
                               filename=os.path.basename(png_path))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(smtp_email, smtp_password)
            smtp.send_message(msg)

        print(f"Successfully sent report PNG to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send report email: {e}")
        return False
