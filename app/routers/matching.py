from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import DeceasedPerson, AssetMatch, FinancialAsset, Claim, User
from app.schemas.schemas import AssetMatchResponse, FinancialAssetResponse
from app.utils.auth import get_current_user
from app.services.matching_service import run_matching_for_deceased

router = APIRouter(tags=["Asset Discovery & Matching"])

@router.post("/api/matching/{deceased_id}", response_model=List[AssetMatchResponse])
def trigger_matching(
    deceased_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dec = db.query(DeceasedPerson).filter(DeceasedPerson.id == deceased_id).first()
    if not dec:
        raise HTTPException(status_code=404, detail="Deceased person record not found")

    if current_user.role != "admin" and dec.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if dec.status != "Verified":
        raise HTTPException(
            status_code=400,
            detail="Matching can only be performed on records that have been verified by an administrator"
        )

    matches = run_matching_for_deceased(db, dec.id)
    return get_matches_for_deceased(dec.id, current_user, db)

@router.get("/api/matches/{deceased_id}", response_model=List[AssetMatchResponse])
def get_matches_for_deceased(
    deceased_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dec = db.query(DeceasedPerson).filter(DeceasedPerson.id == deceased_id).first()
    if not dec:
        raise HTTPException(status_code=404, detail="Deceased person record not found")

    if current_user.role != "admin" and dec.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    matches = db.query(AssetMatch).filter(
        AssetMatch.deceased_person_id == deceased_id
    ).order_by(AssetMatch.matching_score.desc()).all()

    result = []
    for m in matches:
        asset = m.financial_asset
        claim = db.query(Claim).filter(Claim.asset_match_id == m.id).first()

        asset_resp = None
        if asset:
            asset_resp = FinancialAssetResponse(
                id=asset.id,
                institution_id=asset.institution_id,
                asset_type=asset.asset_type,
                institution_name=asset.institution_name,
                holder_name=asset.holder_name,
                date_of_birth=asset.date_of_birth,
                sample_identity_ref=asset.sample_identity_ref,
                account_ref=asset.account_ref,
                category=asset.category,
                nominee_ref=asset.nominee_ref,
                status=asset.status,
                unclaimed_status=asset.unclaimed_status,
                approximate_value=asset.approximate_value,
                details_json=asset.details_json,
                created_at=asset.created_at
            )

        match_resp = AssetMatchResponse(
            id=m.id,
            deceased_person_id=m.deceased_person_id,
            financial_asset_id=m.financial_asset_id,
            matching_score=m.matching_score,
            matching_reason=m.matching_reason,
            match_category=m.match_category,
            review_status=m.review_status,
            created_at=m.created_at,
            financial_asset=asset_resp,
            deceased_person_name=dec.full_name,
            claim_id=claim.id if claim else None,
            claim_status=claim.status if claim else None
        )
        result.append(match_resp)

    return result
