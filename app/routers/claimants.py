import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Claimant, DeceasedPerson, User, AuditLog
from app.schemas.schemas import ClaimantCreate, ClaimantResponse, ClaimantVerifyRequest
from app.utils.auth import get_current_user, require_admin
from app.services.notification_service import send_notification

router = APIRouter(prefix="/api/claimants", tags=["Claimant Heir Verification"])

@router.post("", response_model=ClaimantResponse)
def submit_claimant_verification(
    payload: ClaimantCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dec = db.query(DeceasedPerson).filter(DeceasedPerson.id == payload.deceased_person_id).first()
    if not dec:
        raise HTTPException(status_code=404, detail="Deceased person record not found")

    claimant = Claimant(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        deceased_person_id=payload.deceased_person_id,
        name=payload.name,
        relationship_to_deceased=payload.relationship,
        email=str(payload.email),
        mobile=payload.mobile,
        claimant_type=payload.claimant_type,
        status="Pending"
    )
    db.add(claimant)
    db.commit()
    db.refresh(claimant)

    # Log audit
    audit = AuditLog(
        user_id=current_user.id,
        action="CLAIMANT_VERIFICATION_SUBMITTED",
        entity_type="claimant",
        entity_id=claimant.id,
        details=f"Claimant '{claimant.name}' ({claimant.relationship_to_deceased}) submitted verification for deceased '{dec.full_name}'."
    )
    db.add(audit)
    db.commit()

    send_notification(
        db=db,
        user_id=current_user.id,
        title="Claimant Heir Verification Submitted",
        message=f"Your heir/nominee verification details for '{dec.full_name}' have been submitted for institutional review.",
        notification_type="verification",
        link="/dashboard"
    )

    return ClaimantResponse(
        id=claimant.id,
        user_id=claimant.user_id,
        deceased_person_id=claimant.deceased_person_id,
        name=claimant.name,
        relationship=claimant.relationship_to_deceased,
        email=claimant.email,
        mobile=claimant.mobile,
        claimant_type=claimant.claimant_type,
        status=claimant.status,
        admin_notes=claimant.admin_notes,
        created_at=claimant.created_at,
        deceased_name=dec.full_name
    )

@router.get("", response_model=List[ClaimantResponse])
def get_claimants(
    deceased_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Claimant)
    if current_user.role != "admin" and current_user.role != "institution_rep":
        query = query.filter(Claimant.user_id == current_user.id)
    if deceased_id:
        query = query.filter(Claimant.deceased_person_id == deceased_id)

    claimants = query.order_by(Claimant.created_at.desc()).all()
    result = []
    for c in claimants:
        result.append(ClaimantResponse(
            id=c.id,
            user_id=c.user_id,
            deceased_person_id=c.deceased_person_id,
            name=c.name,
            relationship=c.relationship_to_deceased,
            email=c.email,
            mobile=c.mobile,
            claimant_type=c.claimant_type,
            status=c.status,
            admin_notes=c.admin_notes,
            created_at=c.created_at,
            deceased_name=c.deceased_person.full_name if c.deceased_person else None
        ))
    return result

@router.patch("/{claimant_id}/verify", response_model=ClaimantResponse)
def verify_claimant(
    claimant_id: str,
    payload: ClaimantVerifyRequest,
    current_admin: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_admin.role not in ["admin", "institution_rep"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    claimant = db.query(Claimant).filter(Claimant.id == claimant_id).first()
    if not claimant:
        raise HTTPException(status_code=404, detail="Claimant not found")

    claimant.status = payload.status
    claimant.admin_notes = payload.admin_notes
    db.commit()
    db.refresh(claimant)

    send_notification(
        db=db,
        user_id=claimant.user_id,
        title=f"Claimant Heir Status: {claimant.status}",
        message=f"Your heir verification status has been updated to '{claimant.status}'. Remarks: {claimant.admin_notes or 'Proceed with claim application.'}",
        notification_type="verification",
        link="/dashboard"
    )

    return ClaimantResponse(
        id=claimant.id,
        user_id=claimant.user_id,
        deceased_person_id=claimant.deceased_person_id,
        name=claimant.name,
        relationship=claimant.relationship_to_deceased,
        email=claimant.email,
        mobile=claimant.mobile,
        claimant_type=claimant.claimant_type,
        status=claimant.status,
        admin_notes=claimant.admin_notes,
        created_at=claimant.created_at,
        deceased_name=claimant.deceased_person.full_name if claimant.deceased_person else None
    )
