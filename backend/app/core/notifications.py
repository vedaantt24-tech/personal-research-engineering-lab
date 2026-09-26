from __future__ import annotations

import smtplib
from email.message import EmailMessage

from app.core.config import settings

def send_email(to: str, subject: str, body: str) -> bool:
    if not settings.smtp_host or not settings.smtp_from:
        return False
    msg = EmailMessage()
    msg["From"] = settings.smtp_from
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            if settings.smtp_starttls:
                smtp.starttls()
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password or "")
            smtp.send_message(msg)
        return True
    except Exception:
        return False
