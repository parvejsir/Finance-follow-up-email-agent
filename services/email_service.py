import smtplib
from email.message import EmailMessage
import os

def send_secure_email(recipient, subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = os.getenv("SENDER_EMAIL", "sikandarrohit4545@gmail.com")
    msg['To'] = recipient

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(msg['From'], os.getenv("EMAIL_APP_PASSWORD"))
            smtp.send_message(msg)
        return True, None
    except Exception as e:
        return False, str(e)
    