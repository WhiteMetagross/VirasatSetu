import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Claim, Claimant, AssetMatch, FinancialAsset, DeceasedPerson, User, AuditLog
from app.schemas.schemas import ClaimCreate, ClaimResponse, ClaimStatusUpdate
from app.utils.auth import get_current_user
from app.services.notification_service import send_notification

router = APIRouter(prefix="/api/claims", tags=["Claim Tracking & Processing"])

@router.post("", response_model=ClaimResponse)
def submit_claim(
    payload: ClaimCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify match exists
    match = db.query(AssetMatch).filter(AssetMatch.id == payload.asset_match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Asset match record not found")

    # Check if claim already initiated
    existing_claim = db.query(Claim).filter(Claim.asset_match_id == match.id).first()
    if existing_claim:
        raise HTTPException(status_code=400, detail="A claim has already been submitted for this asset match")

    # Claimant check: either provided or find for this user & deceased
    claimant = None
    if payload.claimant_id:
        claimant = db.query(Claimant).filter(Claimant.id == payload.claimant_id).first()
    else:
        claimant = db.query(Claimant).filter(
            Claimant.user_id == current_user.id,
            Claimant.deceased_person_id == match.deceased_person_id
        ).first()

    if not claimant:
        # Create a default claimant from current user
        claimant = Claimant(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            deceased_person_id=match.deceased_person_id,
            name=current_user.full_name,
            relationship_to_deceased="Legal Heir / Nominee",
            email=current_user.email,
            mobile=current_user.mobile or "9876543210",
            claimant_type="Nominee",
            status="Approved"
        )
        db.add(claimant)
        db.commit()

    asset = match.financial_asset
    claim_ref = f"CLM-2026-{str(uuid.uuid4())[:8].upper()}"

    claim = Claim(
        id=str(uuid.uuid4()),
        claim_reference=claim_ref,
        claimant_id=claimant.id,
        asset_match_id=match.id,
        deceased_person_id=match.deceased_person_id,
        financial_asset_id=asset.id,
        institution_id=asset.institution_id,
        status="Submitted",
        remarks=payload.remarks or "Simulated claim initiated through Virasat Setu prototype portal."
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)

    # Log audit
    audit = AuditLog(
        user_id=current_user.id,
        action="CLAIM_SUBMITTED",
        entity_type="claim",
        entity_id=claim.id,
        details=f"Claim {claim.claim_reference} submitted for {asset.institution_name} ({asset.account_ref})."
    )
    db.add(audit)
    db.commit()

    # Notify family user
    send_notification(
        db=db,
        user_id=current_user.id,
        title=f"Claim {claim.claim_reference} Submitted Successfully",
        message=(
            f"Your simulated claim application {claim.claim_reference} for {asset.institution_name} "
            f"({asset.category} Ref: {asset.account_ref}) has been submitted and queued for verification."
        ),
        notification_type="claim_update",
        link=f"/dashboard/claims"
    )

    return build_claim_response(claim, db)

def build_claim_response(c: Claim, db: Session) -> ClaimResponse:
    claimant = c.claimant
    asset = c.financial_asset
    deceased = c.deceased_person
    institution = c.institution

    return ClaimResponse(
        id=c.id,
        claim_reference=c.claim_reference,
        claimant_id=c.claimant_id,
        asset_match_id=c.asset_match_id,
        deceased_person_id=c.deceased_person_id,
        financial_asset_id=c.financial_asset_id,
        institution_id=c.institution_id,
        status=c.status,
        remarks=c.remarks,
        submission_date=c.submission_date,
        updated_at=c.updated_at,
        claimant_name=claimant.name if claimant else None,
        claimant_relationship=claimant.relationship_to_deceased if claimant else None,
        claimant_email=claimant.email if claimant else None,
        deceased_name=deceased.full_name if deceased else None,
        institution_name=institution.name if institution else None,
        asset_type=asset.asset_type if asset else None,
        account_ref=asset.account_ref if asset else None,
        asset_category=asset.category if asset else None,
        approximate_value=asset.approximate_value if asset else 0.0
    )

@router.get("", response_model=List[ClaimResponse])
def get_claims(
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Claim)

    if current_user.role == "admin":
        pass  # sees all
    elif current_user.role == "institution_rep":
        # Only sees claims for their institution
        if current_user.institution_id:
            query = query.filter(Claim.institution_id == current_user.institution_id)
    else:
        # Family user only sees claims they initiated (matching their claimants or submitted deceased)
        user_claimant_ids = [c.id for c in current_user.claimants]
        query = query.filter(Claim.claimant_id.in_(user_claimant_ids))

    if status:
        query = query.filter(Claim.status == status)

    claims = query.order_by(Claim.submission_date.desc()).all()
    return [build_claim_response(c, db) for c in claims]

@router.get("/{claim_id}", response_model=ClaimResponse)
def get_single_claim(
    claim_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    return build_claim_response(claim, db)

@router.patch("/{claim_id}/status", response_model=ClaimResponse)
def update_claim_status(
    claim_id: str,
    payload: ClaimStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["admin", "institution_rep"]:
        raise HTTPException(status_code=403, detail="Not authorized to update claim status")

    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    # If institution_rep, verify institution matches
    if current_user.role == "institution_rep" and current_user.institution_id != claim.institution_id:
        raise HTTPException(status_code=403, detail="Not authorized for this institution")

    old_status = claim.status
    claim.status = payload.status
    if payload.remarks:
        claim.remarks = payload.remarks
    claim.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(claim)

    # Log audit
    audit = AuditLog(
        user_id=current_user.id,
        action="CLAIM_STATUS_UPDATED",
        entity_type="claim",
        entity_id=claim.id,
        details=f"Status updated from '{old_status}' to '{claim.status}' by {current_user.full_name}. Remarks: {claim.remarks or 'None'}"
    )
    db.add(audit)
    db.commit()

    # Notify family user
    recipient_user_id = claim.claimant.user_id if claim.claimant else None
    if recipient_user_id:
        send_notification(
            db=db,
            user_id=recipient_user_id,
            title=f"Claim Status Update: {claim.status}",
            message=(
                f"Your claim application {claim.claim_reference} ({claim.institution.name}) "
                f"has been updated to '{claim.status}'. Remarks: {claim.remarks or 'No additional remarks.'}"
            ),
            notification_type="claim_update",
            link="/dashboard/claims"
        )

    return build_claim_response(claim, db)
