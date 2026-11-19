import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from sqlalchemy.orm import Session
from app.config import settings
from app.models.models import Notification, User

def send_notification(
    db: Session,
    user_id: str,
    title: str,
    message: str,
    notification_type: str = "system",
    link: str = None
) -> Notification:
    user = db.query(User).filter(User.id == user_id).first()
    recipient_email = user.email if user else "user@example.com"
    recipient_name = user.full_name if user else "Valued Citizen"

    # Build formatted simulated email
    email_subject = f"[Virasat Setu Notification] {title}"
    email_body = f"""

VIRASAT SETU : DIGITAL INHERITANCE AND ASSET DISCOVERY

To: {recipient_name} <{recipient_email}>
Subject: {email_subject}
Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

Dear {recipient_name},

{message}

For your security:
- Virasat Setu never asks for full bank account numbers, passwords, or PINs.
- To inspect details or submit heir verification, log in to your secure portal.

Portal Link: {link or 'https://virasatsetu.gov.in/dashboard'}

Warm regards,
Virasat Setu Asset Discovery Cell
Government Prototype Portal

"""
    email_sent = False
    log_info = f"[Simulated Email Dispatched to {recipient_email} at {datetime.utcnow().isoformat()}]\n{email_body.strip()}"

    # Try real SMTP if configured
    if settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = email_subject
            msg["From"] = settings.FROM_EMAIL
            msg["To"] = recipient_email
            msg.attach(MIMEText(message, "plain"))
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=5) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.FROM_EMAIL, [recipient_email], msg.as_string())
            email_sent = True
            log_info = f"[Real Email Sent successfully via SMTP to {recipient_email}]"
        except Exception as e:
            log_info = f"[SMTP Delivery Note: {str(e)} - Logged in notification audit]\n{email_body.strip()}"
    else:
        email_sent = True  # Simulated success

    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link,
        is_read=False,
        email_sent=email_sent,
        email_logs=log_info
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif
