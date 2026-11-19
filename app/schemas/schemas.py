from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Auth and Profile Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    mobile: Optional[str] = None
    role: Optional[str] = "family_user"
    institution_id: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    mobile: Optional[str] = None
    role: str
    institution_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None


# Institution Schemas
class InstitutionResponse(BaseModel):
    id: str
    name: str
    code: str
    category: str
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True


# Deceased Person Schemas
class DeceasedPersonCreate(BaseModel):
    full_name: str
    date_of_birth: str  # YYYY-MM-DD
    date_of_death: str  # YYYY-MM-DD
    gender: str
    last_known_city: Optional[str] = None
    last_known_state: Optional[str] = None
    death_cert_ref: str
    death_reg_date: Optional[str] = None
    issuing_authority: Optional[str] = None
    sample_identity_ref: str  # PAN / Sample Aadhaar
    # Optional claimant information entered during death registration
    claimant_name: Optional[str] = None
    claimant_relationship: Optional[str] = None
    claimant_email: Optional[str] = None
    claimant_mobile: Optional[str] = None
    claimant_type: Optional[str] = "Nominee"

class DeceasedVerifyRequest(BaseModel):
    status: str  # "Verified" or "Rejected"
    admin_notes: Optional[str] = None

class DeceasedPersonResponse(BaseModel):
    id: str
    user_id: str
    full_name: str
    date_of_birth: str
    date_of_death: str
    gender: str
    last_known_city: Optional[str] = None
    last_known_state: Optional[str] = None
    death_cert_ref: str
    death_reg_date: Optional[str] = None
    issuing_authority: Optional[str] = None
    sample_identity_ref: str
    status: str
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    submitted_by_name: Optional[str] = None
    total_matches: Optional[int] = 0

    class Config:
        from_attributes = True


# Financial Asset Schemas
class FinancialAssetCreate(BaseModel):
    institution_id: str
    asset_type: str  # bank, insurance, mutual_fund
    institution_name: str
    holder_name: str
    date_of_birth: Optional[str] = None
    sample_identity_ref: str
    account_ref: str
    category: str
    nominee_ref: Optional[str] = None
    status: Optional[str] = "Unclaimed"
    unclaimed_status: Optional[str] = "Dormant > 10 Yrs"
    approximate_value: Optional[float] = 0.0
    details_json: Optional[str] = None

class FinancialAssetResponse(BaseModel):
    id: str
    institution_id: str
    asset_type: str
    institution_name: str
    holder_name: str
    date_of_birth: Optional[str] = None
    sample_identity_ref: str
    account_ref: str
    category: str
    nominee_ref: Optional[str] = None
    status: str
    unclaimed_status: Optional[str] = None
    approximate_value: float
    details_json: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Asset Match Schemas
class AssetMatchResponse(BaseModel):
    id: str
    deceased_person_id: str
    financial_asset_id: str
    matching_score: int
    matching_reason: str
    match_category: str
    review_status: str
    created_at: datetime
    financial_asset: Optional[FinancialAssetResponse] = None
    deceased_person_name: Optional[str] = None
    claim_id: Optional[str] = None
    claim_status: Optional[str] = None

    class Config:
        from_attributes = True


# Claimant Schemas
class ClaimantCreate(BaseModel):
    deceased_person_id: str
    name: str
    relationship: str
    email: EmailStr
    mobile: str
    claimant_type: str = "Nominee"  # Nominee or Legal Heir

class ClaimantVerifyRequest(BaseModel):
    status: str  # Approved, Rejected, Additional Documents Required
    admin_notes: Optional[str] = None

class ClaimantResponse(BaseModel):
    id: str
    user_id: str
    deceased_person_id: str
    name: str
    relationship: str
    email: str
    mobile: str
    claimant_type: str
    status: str
    admin_notes: Optional[str] = None
    created_at: datetime
    deceased_name: Optional[str] = None

    class Config:
        from_attributes = True


# Claim Schemas
class ClaimCreate(BaseModel):
    asset_match_id: str
    claimant_id: Optional[str] = None
    remarks: Optional[str] = None

class ClaimStatusUpdate(BaseModel):
    status: str  # Submitted, Under Review, Documents Required, Approved, Rejected, Completed
    remarks: Optional[str] = None

class ClaimResponse(BaseModel):
    id: str
    claim_reference: str
    claimant_id: str
    asset_match_id: str
    deceased_person_id: str
    financial_asset_id: str
    institution_id: str
    status: str
    remarks: Optional[str] = None
    submission_date: datetime
    updated_at: datetime
    # Nested helpers for display
    claimant_name: Optional[str] = None
    claimant_relationship: Optional[str] = None
    claimant_email: Optional[str] = None
    deceased_name: Optional[str] = None
    institution_name: Optional[str] = None
    asset_type: Optional[str] = None
    account_ref: Optional[str] = None
    asset_category: Optional[str] = None
    approximate_value: Optional[float] = 0.0

    class Config:
        from_attributes = True


# Document Schemas
class DocumentResponse(BaseModel):
    id: str
    user_id: str
    deceased_person_id: Optional[str] = None
    claimant_id: Optional[str] = None
    claim_id: Optional[str] = None
    document_type: str
    file_name: str
    file_path: str
    file_size: int
    content_type: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Notification Schemas
class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    notification_type: str
    link: Optional[str] = None
    is_read: bool
    email_sent: bool
    email_logs: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Dashboard Stats Schemas
class FamilyDashboardStats(BaseModel):
    total_deceased: int
    total_potential_assets: int
    claims_in_progress: int
    unread_notifications: int
    recent_activities: List[Dict[str, Any]]
    claims_summary: List[Dict[str, Any]]

class AdminDashboardStats(BaseModel):
    total_users: int
    total_deceased: int
    pending_verifications: int
    total_financial_records: int
    bank_records_count: int
    insurance_records_count: int
    mutual_funds_count: int
    total_matches: int
    strong_matches_count: int
    total_claims: int
    pending_claims: int
