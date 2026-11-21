"""
Virasat Setu Notification Service:
Handles system notifications, audit event logging, and email delivery dispatch
for citizens, legal heirs, institutional desk officers, and administrators.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid, formatdate
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.config import settings
from app.models.models import Notification, User


def build_email_template(
    recipient_name: str,
    recipient_email: str,
    subject: str,
    message: str,
    link: Optional[str] = None
) -> Tuple[str, str]:
    """Builds clean plain text and responsive HTML email templates."""
    portal_url = link or "https://virasat-setu-eight.vercel.app/dashboard"
    if not portal_url.startswith("http"):
        portal_url = f"https://virasat-setu-eight.vercel.app{portal_url}"

    current_year = datetime.utcnow().year

    plain_body = f"""
VIRASAT SETU: NATIONAL DIGITAL INHERITANCE AND ASSET DISCOVERY PLATFORM

To: {recipient_name} <{recipient_email}>
Subject: {subject}
Date: {formatdate(localtime=True)}

Dear {recipient_name},

{message}

For your security and peace of mind:
1. Virasat Setu never asks for full bank passwords, debit card PINs, or confidential OTPs.
2. To inspect detailed asset discoveries or submit verification documents, log in directly through the official citizen portal.

Access Your Platform Account:
{portal_url}

Warm regards,
Virasat Setu Asset Discovery Cell
Government Prototype Portal
"""

    html_body = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{subject}</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 24px; color: #1e293b;">
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden;">
    <tr>
      <td style="background-color: #0f172a; padding: 24px 32px; text-align: left;">
        <div style="color: #f59e0b; font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Government of India Prototype</div>
        <div style="color: #ffffff; font-size: 20px; font-weight: bold; margin-top: 4px;">Virasat Setu</div>
        <div style="color: #94a3b8; font-size: 12px; margin-top: 2px;">National Deceased Asset Discovery and Legal Succession Portal</div>
      </td>
    </tr>
    <tr>
      <td style="padding: 32px;">
        <h2 style="font-size: 16px; color: #0f172a; margin-top: 0; margin-bottom: 16px; border-bottom: 2px solid #f1f5f9; padding-bottom: 8px;">
          {subject}
        </h2>
        <p style="font-size: 14px; color: #334155; line-height: 1.6; margin-bottom: 20px;">
          Dear <strong>{recipient_name}</strong>,
        </p>
        <div style="background-color: #f8fafc; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px; font-size: 13px; color: #1e293b; line-height: 1.6; margin-bottom: 24px;">
          {message.replace(chr(10), '<br>')}
        </div>
        <div style="text-align: center; margin: 28px 0;">
          <a href="{portal_url}" style="background-color: #0f172a; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-size: 13px; font-weight: bold; display: inline-block;">
            Access Virasat Setu Portal
          </a>
        </div>
        <div style="background-color: #f1f5f9; padding: 16px; border-radius: 8px; font-size: 11px; color: #64748b; line-height: 1.5; margin-top: 24px;">
          <strong style="color: #334155;">Security Notice:</strong><br>
          1. Virasat Setu never requests full bank account numbers, passwords, PINs, or OTPs.<br>
          2. Always verify legal heirship and asset claims through the official secured portal.
        </div>
      </td>
    </tr>
    <tr>
      <td style="background-color: #f8fafc; padding: 16px 32px; text-align: center; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0;">
        Virasat Setu Asset Discovery Cell, New Delhi, India<br>
        Year {current_year} Digital India Initiative
      </td>
    </tr>
  </table>
</body>
</html>"""

    return plain_body, html_body


def dispatch_email(
    recipient_email: str,
    recipient_name: str,
    subject: str,
    message: str,
    link: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Dispatches email using authenticated SMTP if configured,
    or records a simulated delivery log for platform audit.
    """
    clean_email = (recipient_email or "").strip().lower()
    if not clean_email or "@" not in clean_email or "." not in clean_email:
        return False, "Invalid recipient email address supplied."

    plain_body, html_body = build_email_template(
        recipient_name=recipient_name,
        recipient_email=clean_email,
        subject=subject,
        message=message,
        link=link
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.FROM_EMAIL
    msg["To"] = clean_email
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="virasatsetu.gov.in")
    msg.attach(MIMEText(plain_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    # Attempt real SMTP delivery if parameters are supplied
    if settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD:
        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=8) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.FROM_EMAIL, [clean_email], msg.as_string())
            return True, f"Real email dispatched successfully via SMTP to {clean_email} at {datetime.utcnow().isoformat()}"
        except Exception as err:
            return False, f"SMTP delivery failure: {str(err)} (Logged in notification audit trail)"

    # Graceful fallback: simulated delivery record
    return True, f"Simulated email notification dispatched successfully to {clean_email} at {datetime.utcnow().isoformat()}"


def send_notification(
    db: Session,
    user_id: str,
    title: str,
    message: str,
    notification_type: str = "system",
    link: Optional[str] = None,
    custom_recipient_email: Optional[str] = None
) -> Notification:
    """Creates a notification record and dispatches email notification."""
    user = db.query(User).filter(User.id == user_id).first()
    recipient_email = custom_recipient_email or (user.email if user else "citizen@example.com")
    recipient_name = user.full_name if user else "Valued Citizen"

    subject = f"[Virasat Setu] {title}"
    email_sent, log_info = dispatch_email(
        recipient_email=recipient_email,
        recipient_name=recipient_name,
        subject=subject,
        message=message,
        link=link
    )

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


def trigger_manual_email_notification(
    db: Session,
    recipient_email: str,
    title: str,
    message: str,
    notification_type: str = "system",
    link: Optional[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Public helper to dispatch email notifications directly to any citizen address."""
    clean_email = recipient_email.strip().lower()
    user = None
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = db.query(User).filter(User.email == clean_email).first()

    # If no existing user found, pick admin or first user for foreign key constraint
    assigned_user_id = user.id if user else None
    if not assigned_user_id:
        fallback_user = db.query(User).first()
        if fallback_user:
            assigned_user_id = fallback_user.id

    recipient_name = user.full_name if user else "Citizen Claimant"
    subject = f"[Virasat Setu] {title}"

    email_sent, log_info = dispatch_email(
        recipient_email=clean_email,
        recipient_name=recipient_name,
        subject=subject,
        message=message,
        link=link
    )

    notif_id = None
    if assigned_user_id:
        notif = Notification(
            user_id=assigned_user_id,
            title=title,
            message=f"[Dispatched to {clean_email}] {message}",
            notification_type=notification_type,
            link=link,
            is_read=False,
            email_sent=email_sent,
            email_logs=log_info
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        notif_id = notif.id

    return {
        "success": email_sent,
        "recipient": clean_email,
        "subject": subject,
        "status": "Dispatched" if email_sent else "Failed",
        "timestamp": datetime.utcnow().isoformat(),
        "delivery_log": log_info,
        "notification_id": notif_id
    }
