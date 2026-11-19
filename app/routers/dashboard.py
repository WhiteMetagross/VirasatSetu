from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import DeceasedPerson, AssetMatch, Claim, Notification, User, AuditLog
from app.schemas.schemas import FamilyDashboardStats
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard Overview"])

@router.get("/family-stats", response_model=FamilyDashboardStats)
def get_family_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Total deceased submitted by this user
    user_deceased = db.query(DeceasedPerson).filter(DeceasedPerson.user_id == current_user.id).all()
    dec_ids = [d.id for d in user_deceased]
    total_deceased = len(dec_ids)

    # Total potential assets identified for user's deceased persons
    total_assets = 0
    if dec_ids:
        total_assets = db.query(AssetMatch).filter(AssetMatch.deceased_person_id.in_(dec_ids)).count()

    # Claims in progress for this user
    user_claimant_ids = [c.id for c in current_user.claimants]
    claims = []
    if user_claimant_ids:
        claims = db.query(Claim).filter(Claim.claimant_id.in_(user_claimant_ids)).all()
    
    in_progress = sum(1 for c in claims if c.status in ["Submitted", "Under Review", "Documents Required"])

    # Unread notifications
    unread = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()

    # Recent activity logs or notifications
    recent_notifs = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).limit(5).all()

    recent_activities = [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "type": n.notification_type,
            "created_at": n.created_at.isoformat(),
            "link": n.link
        }
        for n in recent_notifs
    ]

    claims_summary = [
        {
            "id": c.id,
            "reference": c.claim_reference,
            "institution": c.institution.name if c.institution else "N/A",
            "status": c.status,
            "asset_category": c.financial_asset.category if c.financial_asset else "N/A",
            "value": c.financial_asset.approximate_value if c.financial_asset else 0.0,
            "submission_date": c.submission_date.isoformat()
        }
        for c in claims
    ]

    return FamilyDashboardStats(
        total_deceased=total_deceased,
        total_potential_assets=total_assets,
        claims_in_progress=in_progress,
        unread_notifications=unread,
        recent_activities=recent_activities,
        claims_summary=claims_summary
    )
