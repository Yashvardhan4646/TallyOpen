import smtplib
from email.message import EmailMessage
import os

def send_invoice_email(to_email, pdf_path, invoice_id, settings=None):
    """
    Sends an email with the PDF invoice attached via Gmail SMTP.
    Returns (success_bool, message_str)
    """
    smtp_email    = (settings or {}).get("smtp_email", "")
    smtp_password = (settings or {}).get("smtp_password", "")
    business_name = (settings or {}).get("business_name", "Our Business")

    if not smtp_email or not smtp_password:
        return False, "SMTP Email or App Password not configured in Settings."

    try:
        msg = EmailMessage()
        msg['Subject'] = f'Your Bill / Invoice — INV-{invoice_id}'
        msg['From']    = smtp_email
        msg['To']      = to_email
        msg.set_content(
            f'Dear Customer,\n\nPlease find your bill attached.\n\nThank you!\n\n— {business_name}'
        )

        with open(pdf_path, 'rb') as f:
            msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=os.path.basename(pdf_path))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15) as smtp:
            smtp.login(smtp_email, smtp_password)
            smtp.send_message(msg)

        return True, "Email sent successfully!"
    except smtplib.SMTPAuthenticationError:
        return False, "Authentication Failed: Check if your App Password is correct."
    except Exception as e:
        return False, f"Failed: {str(e)}"

def send_test_email(settings):
    """Sends a test email to the configured SMTP email address."""
    smtp_email = settings.get("smtp_email", "")
    if not smtp_email:
        return False, "No email configured."
    
    try:
        msg = EmailMessage()
        msg['Subject'] = 'TallyOpen - Email Test'
        msg['From']    = smtp_email
        msg['To']      = smtp_email
        msg.set_content("Success! Your TallyOpen email system is working correctly.")

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15) as smtp:
            smtp.login(smtp_email, settings.get("smtp_password", ""))
            smtp.send_message(msg)
        return True, "Test Success! Check your inbox."
    except Exception as e:
        return False, str(e)


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
