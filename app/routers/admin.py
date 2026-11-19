import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db, engine, Base
from app.models.models import (
    User, DeceasedPerson, FinancialAsset, AssetMatch, Claim, AuditLog, Institution
)
from app.schemas.schemas import (
    AdminDashboardStats, FinancialAssetResponse, FinancialAssetCreate
)
from app.utils.auth import require_admin, get_current_user

router = APIRouter(prefix="/api/admin", tags=["Administrator Dashboard"])

@router.get("/stats", response_model=AdminDashboardStats)
def get_admin_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    total_users = db.query(User).count()
    total_deceased = db.query(DeceasedPerson).count()
    pending_verif = db.query(DeceasedPerson).filter(DeceasedPerson.status == "Pending Verification").count()
    
    bank_count = db.query(FinancialAsset).filter(FinancialAsset.asset_type == "bank").count()
    ins_count = db.query(FinancialAsset).filter(FinancialAsset.asset_type == "insurance").count()
    mf_count = db.query(FinancialAsset).filter(FinancialAsset.asset_type == "mutual_fund").count()
    total_financial = bank_count + ins_count + mf_count

    total_matches = db.query(AssetMatch).count()
    strong_matches = db.query(AssetMatch).filter(AssetMatch.matching_score >= 80).count()

    total_claims = db.query(Claim).count()
    pending_claims = db.query(Claim).filter(Claim.status.in_(["Submitted", "Under Review", "Documents Required"])).count()

    return AdminDashboardStats(
        total_users=total_users,
        total_deceased=total_deceased,
        pending_verifications=pending_verif,
        total_financial_records=total_financial,
        bank_records_count=bank_count,
        insurance_records_count=ins_count,
        mutual_funds_count=mf_count,
        total_matches=total_matches,
        strong_matches_count=strong_matches,
        total_claims=total_claims,
        pending_claims=pending_claims
    )

@router.get("/financial-assets", response_model=List[FinancialAssetResponse])
def get_all_financial_assets(
    asset_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(FinancialAsset)
    if asset_type:
        query = query.filter(FinancialAsset.asset_type == asset_type)
    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            (FinancialAsset.holder_name.ilike(s)) |
            (FinancialAsset.sample_identity_ref.ilike(s)) |
            (FinancialAsset.account_ref.ilike(s)) |
            (FinancialAsset.institution_name.ilike(s))
        )
    return query.limit(limit).all()

@router.post("/financial-assets", response_model=FinancialAssetResponse)
def add_financial_asset(
    payload: FinancialAssetCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    inst = db.query(Institution).filter(Institution.id == payload.institution_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")

    fa = FinancialAsset(
        id=str(uuid.uuid4()),
        institution_id=payload.institution_id,
        asset_type=payload.asset_type,
        institution_name=inst.name,
        holder_name=payload.holder_name,
        date_of_birth=payload.date_of_birth,
        sample_identity_ref=payload.sample_identity_ref.strip().upper(),
        account_ref=payload.account_ref,
        category=payload.category,
        nominee_ref=payload.nominee_ref,
        status=payload.status or "Unclaimed",
        unclaimed_status=payload.unclaimed_status or "Dormant > 10 Yrs",
        approximate_value=payload.approximate_value or 0.0,
        details_json=payload.details_json
    )
    db.add(fa)
    db.commit()
    db.refresh(fa)

    # Log audit
    audit = AuditLog(
        user_id=admin.id,
        action="FINANCIAL_ASSET_CREATED",
        entity_type="financial_asset",
        entity_id=fa.id,
        details=f"Admin {admin.full_name} added sample record {fa.account_ref} ({fa.holder_name})."
    )
    db.add(audit)
    db.commit()

    return fa

@router.get("/audit-logs")
def get_audit_logs(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
    limit: int = 50
):
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()

@router.post("/demo/reset")
def reset_demo_database(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # Wipe and reseed
    from seed.sample_data import seed_all
    Base.metadata.drop_all(bind=engine)
    seed_all()
    return {"message": "Demo database successfully reset to clean presentation state with Rajesh Kumar scenario."}
