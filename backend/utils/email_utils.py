# backend/utils/email_utils.py
import smtplib
from email.mime.text import MIMEText
from config import EMAIL_FROM, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

def send_email(subject, body, to_email):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, [to_email], msg.as_string())
