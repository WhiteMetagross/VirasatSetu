"""
Virasat Setu Notifications Router:
Provides endpoints to fetch notifications, mark items as read,
and dispatch email notifications to citizens and legal heirs.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Notification, User
from app.schemas.schemas import NotificationResponse
from app.utils.auth import get_current_user, get_optional_current_user
from app.services.notification_service import trigger_manual_email_notification

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


class SendEmailNotificationRequest(BaseModel):
    recipient_email: str
    title: str = "Asset Discovery and Succession Update"
    message: str
    notification_type: Optional[str] = "system"
    link: Optional[str] = "/dashboard"


class TestEmailNotificationRequest(BaseModel):
    email: Optional[str] = "xerontitan99@gmail.com"


@router.get("", response_model=List[NotificationResponse])
def get_user_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves all notifications for the authenticated user."""
    notifs = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).all()
    return notifs


@router.patch("/{notif_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notif_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marks an individual notification as read."""
    notif = db.query(Notification).filter(
        Notification.id == notif_id,
        Notification.user_id == current_user.id
    ).first()
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif


@router.post("/read-all")
def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marks all unread notifications as read for the current user."""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read."}


@router.post("/send-email")
def send_email_notification_endpoint(
    req: SendEmailNotificationRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Dispatches an email notification to any citizen or legal heir.
    Accessible for direct platform testing and verification.
    """
    user_id = current_user.id if current_user else None
    result = trigger_manual_email_notification(
        db=db,
        recipient_email=req.recipient_email,
        title=req.title,
        message=req.message,
        notification_type=req.notification_type or "system",
        link=req.link,
        user_id=user_id
    )
    return result


@router.post("/test-email")
def send_test_email_notification(
    req: TestEmailNotificationRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Dispatches a comprehensive asset discovery notification email
    to the designated testing address (defaults to xerontitan99@gmail.com).
    """
    target_email = req.email or "xerontitan99@gmail.com"
    user_id = current_user.id if current_user else None

    title = "Asset Discovery Update: Matched Financial Holdings Discovered"
    message = (
        "Good news from Virasat Setu:\n\n"
        "Our automated matching engine has successfully cross referenced your registered family profile "
        "and identified ten potential dormant and unclaimed assets across scheduled commercial banks, "
        "the National Pension System (PFRDA), the Department of Posts (PPF and NSC), "
        "the Employees Provident Fund Organisation (EPFO), Life Insurance Corporation of India (LIC), "
        "and CDSL equity demat accounts.\n\n"
        "Discovered Assets Highlights:\n"
        "1. National Pension System (NPS Tier 1): Rs 14,80,000 (PRAN: 1100••••8172)\n"
        "2. Department of Posts (Public Provident Fund): Rs 8,65,000 (PPF: DEL••••1928)\n"
        "3. Life Insurance Corporation (Jeevan Anand Policy): Rs 8,50,000 (POL: 928••••635)\n"
        "4. CDSL Equity Demat Portfolio: Rs 9,15,000 (BO: 1203••••8271)\n"
        "5. State Bank of India (Fixed Deposit): Rs 3,45,000 (SB: 401••••4102)\n\n"
        "Next Steps:\n"
        "Please log in to your Virasat Setu dashboard to verify details, review prescriptive checklist advice "
        "from Viru Legal Copilot, and file succession claims directly with institutional desks."
    )

    result = trigger_manual_email_notification(
        db=db,
        recipient_email=target_email,
        title=title,
        message=message,
        notification_type="match_found",
        link="/dashboard",
        user_id=user_id
    )
    return result
