from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Institution, FinancialAsset, Claim, User
from app.schemas.schemas import InstitutionResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/institutions", tags=["Institutions"])

@router.get("", response_model=List[InstitutionResponse])
def get_institutions(db: Session = Depends(get_db)):
    return db.query(Institution).all()

@router.get("/my")
def get_my_institution_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "institution_rep" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized as institution representative")

    institution_id = current_user.institution_id
    if not institution_id:
        # Default to first institution if admin testing
        first_inst = db.query(Institution).first()
        institution_id = first_inst.id if first_inst else None

    inst = db.query(Institution).filter(Institution.id == institution_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")

    total_assets = db.query(FinancialAsset).filter(FinancialAsset.institution_id == inst.id).count()
    claims_count = db.query(Claim).filter(Claim.institution_id == inst.id).count()
    pending_claims = db.query(Claim).filter(
        Claim.institution_id == inst.id,
        Claim.status.in_(["Submitted", "Under Review", "Documents Required"])
    ).count()
    approved_claims = db.query(Claim).filter(
        Claim.institution_id == inst.id,
        Claim.status.in_(["Approved", "Completed"])
    ).count()

    return {
        "institution": InstitutionResponse.from_orm(inst),
        "total_assets": total_assets,
        "total_claims": claims_count,
        "pending_claims": pending_claims,
        "approved_claims": approved_claims
    }
