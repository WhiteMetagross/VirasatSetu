import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import DeceasedPerson, Claimant, User, AuditLog, AssetMatch
from app.schemas.schemas import (
    DeceasedPersonCreate, DeceasedPersonResponse, DeceasedVerifyRequest
)
from app.utils.auth import get_current_user, require_admin
from app.services.matching_service import run_matching_for_deceased
from app.services.notification_service import send_notification

router = APIRouter(prefix="/api/deceased", tags=["Deceased Persons"])

@router.post("", response_model=DeceasedPersonResponse)
def create_deceased_record(
    payload: DeceasedPersonCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dec = DeceasedPerson(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        full_name=payload.full_name,
        date_of_birth=payload.date_of_birth,
        date_of_death=payload.date_of_death,
        gender=payload.gender,
        last_known_city=payload.last_known_city,
        last_known_state=payload.last_known_state,
        death_cert_ref=(payload.death_cert_ref.strip() if payload.death_cert_ref and payload.death_cert_ref.strip() else "Pending Civil Issuance"),
        death_reg_date=payload.death_reg_date,
        issuing_authority=payload.issuing_authority,
        sample_identity_ref=payload.sample_identity_ref.strip().upper(),
        status="Pending Verification"
    )
    db.add(dec)
    db.commit()
    db.refresh(dec)

    # If claimant details were provided with submission, create Claimant
    if payload.claimant_name and payload.claimant_relationship:
        claimant = Claimant(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            deceased_person_id=dec.id,
            name=payload.claimant_name,
            relationship_to_deceased=payload.claimant_relationship,
            email=payload.claimant_email or current_user.email,
            mobile=payload.claimant_mobile or current_user.mobile or "",
            claimant_type=payload.claimant_type or "Nominee",
            status="Pending"
        )
        db.add(claimant)
        db.commit()

    # Log audit
    audit = AuditLog(
        user_id=current_user.id,
        action="DECEASED_RECORD_SUBMITTED",
        entity_type="deceased_person",
        entity_id=dec.id,
        details=f"User {current_user.full_name} submitted death record for '{dec.full_name}'."
    )
    db.add(audit)
    db.commit()

    # Notify family user
    send_notification(
        db=db,
        user_id=current_user.id,
        title="Death Record Submitted for Verification",
        message=(
            f"Your submitted record for '{dec.full_name}' (Death Certificate: {dec.death_cert_ref}) "
            "has been received and is currently under review by our administrative verification cell."
        ),
        notification_type="verification",
        link="/dashboard"
    )

    return dec

@router.get("", response_model=List[DeceasedPersonResponse])
def get_deceased_records(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "admin":
        records = db.query(DeceasedPerson).order_by(DeceasedPerson.created_at.desc()).all()
    else:
        records = db.query(DeceasedPerson).filter(DeceasedPerson.user_id == current_user.id).order_by(DeceasedPerson.created_at.desc()).all()

    result = []
    for r in records:
        match_count = db.query(AssetMatch).filter(AssetMatch.deceased_person_id == r.id).count()
        r_dict = DeceasedPersonResponse(
            id=r.id,
            user_id=r.user_id,
            full_name=r.full_name,
            date_of_birth=r.date_of_birth,
            date_of_death=r.date_of_death,
            gender=r.gender,
            last_known_city=r.last_known_city,
            last_known_state=r.last_known_state,
            death_cert_ref=r.death_cert_ref,
            death_reg_date=r.death_reg_date,
            issuing_authority=r.issuing_authority,
            sample_identity_ref=r.sample_identity_ref,
            status=r.status,
            admin_notes=r.admin_notes,
            created_at=r.created_at,
            updated_at=r.updated_at,
            submitted_by_name=r.submitted_by_user.full_name if r.submitted_by_user else None,
            total_matches=match_count
        )
        result.append(r_dict)
    return result

@router.get("/{deceased_id}", response_model=DeceasedPersonResponse)
def get_single_deceased_record(
    deceased_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dec = db.query(DeceasedPerson).filter(DeceasedPerson.id == deceased_id).first()
    if not dec:
        raise HTTPException(status_code=404, detail="Deceased record not found")
    
    # Permission check: admin can view all, family can view only own
    if current_user.role != "admin" and dec.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this record")

    match_count = db.query(AssetMatch).filter(AssetMatch.deceased_person_id == dec.id).count()
    return DeceasedPersonResponse(
        id=dec.id,
        user_id=dec.user_id,
        full_name=dec.full_name,
        date_of_birth=dec.date_of_birth,
        date_of_death=dec.date_of_death,
        gender=dec.gender,
        last_known_city=dec.last_known_city,
        last_known_state=dec.last_known_state,
        death_cert_ref=dec.death_cert_ref,
        death_reg_date=dec.death_reg_date,
        issuing_authority=dec.issuing_authority,
        sample_identity_ref=dec.sample_identity_ref,
        status=dec.status,
        admin_notes=dec.admin_notes,
        created_at=dec.created_at,
        updated_at=dec.updated_at,
        submitted_by_name=dec.submitted_by_user.full_name if dec.submitted_by_user else None,
        total_matches=match_count
    )

@router.patch("/{deceased_id}/verify", response_model=DeceasedPersonResponse)
def verify_deceased_record(
    deceased_id: str,
    payload: DeceasedVerifyRequest,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    dec = db.query(DeceasedPerson).filter(DeceasedPerson.id == deceased_id).first()
    if not dec:
        raise HTTPException(status_code=404, detail="Deceased record not found")

    dec.status = payload.status.capitalize()
    dec.admin_notes = payload.admin_notes
    db.commit()
    db.refresh(dec)

    # Log audit
    audit = AuditLog(
        user_id=current_admin.id,
        action="DECEASED_RECORD_VERIFICATION",
        entity_type="deceased_person",
        entity_id=dec.id,
        details=f"Admin {current_admin.full_name} set status to '{dec.status}'. Notes: {dec.admin_notes or 'None'}"
    )
    db.add(audit)
    db.commit()

    if dec.status == "Verified":
        # Step 4 of the Plan: Once verified, automated matching triggers!
        run_matching_for_deceased(db, dec.id)

        send_notification(
            db=db,
            user_id=dec.user_id,
            title="Death Record Verified",
            message=(
                f"Your submitted record for '{dec.full_name}' has been verified by the administrator. "
                "Automated financial asset matching has been executed across Bank, Insurance, and Mutual Fund datasets."
            ),
            notification_type="verification",
            link=f"/dashboard/deceased/{dec.id}/matches"
        )
    elif dec.status == "Rejected":
        send_notification(
            db=db,
            user_id=dec.user_id,
            title="Death Record Verification Update",
            message=f"Your submitted record for '{dec.full_name}' was not approved. Reason: {dec.admin_notes or 'Please re-verify certificate details'}.",
            notification_type="verification",
            link="/dashboard"
        )

    match_count = db.query(AssetMatch).filter(AssetMatch.deceased_person_id == dec.id).count()
    return DeceasedPersonResponse(
        id=dec.id,
        user_id=dec.user_id,
        full_name=dec.full_name,
        date_of_birth=dec.date_of_birth,
        date_of_death=dec.date_of_death,
        gender=dec.gender,
        last_known_city=dec.last_known_city,
        last_known_state=dec.last_known_state,
        death_cert_ref=dec.death_cert_ref,
        death_reg_date=dec.death_reg_date,
        issuing_authority=dec.issuing_authority,
        sample_identity_ref=dec.sample_identity_ref,
        status=dec.status,
        admin_notes=dec.admin_notes,
        created_at=dec.created_at,
        updated_at=dec.updated_at,
        submitted_by_name=dec.submitted_by_user.full_name if dec.submitted_by_user else None,
        total_matches=match_count
    )
