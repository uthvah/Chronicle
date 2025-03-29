# kindle_service.py

import smtplib
from email.message import EmailMessage
from config import KINDLE_EMAIL, SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD

def send_to_kindle(epub_path):
    """
    Sends the given EPUB file to the configured Kindle email.
    """
    try:
        msg = EmailMessage()
        msg["Subject"] = "Your Processed eBook"
        msg["From"] = SMTP_USERNAME
        msg["To"] = KINDLE_EMAIL
        msg.set_content("Please find attached your processed eBook.")

        # Read and attach the file
        with open(epub_path, "rb") as f:
            file_data = f.read()
            file_name = epub_path.split("\\")[-1]  # Windows path separator
        msg.add_attachment(file_data, maintype="application", subtype="epub+zip", filename=file_name)

        # Connect to SMTP and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print("Error sending to Kindle:", e)
        return False
