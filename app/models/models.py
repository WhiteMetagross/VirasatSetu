import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship as sa_relationship
from app.database import Base

def gen_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "profiles"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    mobile = Column(String(20), nullable=True)
    role = Column(String(50), default="family_user", nullable=False)  # family_user, admin, institution_rep
    institution_id = Column(String(36), ForeignKey("institutions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    institution = sa_relationship("Institution", back_populates="representatives")
    deceased_persons = sa_relationship("DeceasedPerson", back_populates="submitted_by_user", cascade="all, delete-orphan")
    claimants = sa_relationship("Claimant", back_populates="user", cascade="all, delete-orphan")
    notifications = sa_relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    documents = sa_relationship("Document", back_populates="user", cascade="all, delete-orphan")


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    category = Column(String(50), nullable=False)  # bank, insurance, mutual_fund
    contact_email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    representatives = sa_relationship("User", back_populates="institution")
    financial_assets = sa_relationship("FinancialAsset", back_populates="institution")
    claims = sa_relationship("Claim", back_populates="institution")


class DeceasedPerson(Base):
    __tablename__ = "deceased_persons"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("profiles.id"), nullable=False)
    full_name = Column(String(255), nullable=False, index=True)
    date_of_birth = Column(String(20), nullable=False)
    date_of_death = Column(String(20), nullable=False)
    gender = Column(String(20), nullable=False)
    last_known_city = Column(String(100), nullable=True)
    last_known_state = Column(String(100), nullable=True)
    death_cert_ref = Column(String(100), nullable=False)
    death_reg_date = Column(String(20), nullable=True)
    issuing_authority = Column(String(255), nullable=True)
    sample_identity_ref = Column(String(100), nullable=False, index=True)  # PAN, Sample Aadhaar
    status = Column(String(50), default="Pending Verification", nullable=False)  # Pending Verification, Verified, Rejected
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    submitted_by_user = sa_relationship("User", back_populates="deceased_persons")
    claimants = sa_relationship("Claimant", back_populates="deceased_person", cascade="all, delete-orphan")
    matches = sa_relationship("AssetMatch", back_populates="deceased_person", cascade="all, delete-orphan")
    documents = sa_relationship("Document", back_populates="deceased_person", cascade="all, delete-orphan")
    claims = sa_relationship("Claim", back_populates="deceased_person", cascade="all, delete-orphan")


class Claimant(Base):
    __tablename__ = "claimants"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("profiles.id"), nullable=False)
    deceased_person_id = Column(String(36), ForeignKey("deceased_persons.id"), nullable=False)
    name = Column(String(255), nullable=False)
    relationship_to_deceased = Column("relationship", String(100), nullable=False)  # Son, Spouse, Daughter, etc.
    email = Column(String(255), nullable=False)
    mobile = Column(String(50), nullable=False)
    claimant_type = Column(String(50), default="Nominee", nullable=False)  # Nominee, Legal Heir
    status = Column(String(50), default="Pending", nullable=False)  # Pending, Approved, Rejected, Additional Documents Required
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = sa_relationship("User", back_populates="claimants")
    deceased_person = sa_relationship("DeceasedPerson", back_populates="claimants")
    claims = sa_relationship("Claim", back_populates="claimant", cascade="all, delete-orphan")
    documents = sa_relationship("Document", back_populates="claimant")


class FinancialAsset(Base):
    __tablename__ = "financial_assets"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    institution_id = Column(String(36), ForeignKey("institutions.id"), nullable=False)
    asset_type = Column(String(50), nullable=False, index=True)  # bank, insurance, mutual_fund
    institution_name = Column(String(255), nullable=False)
    holder_name = Column(String(255), nullable=False, index=True)
    date_of_birth = Column(String(20), nullable=True)
    sample_identity_ref = Column(String(100), nullable=False, index=True)
    account_ref = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)  # Savings, Fixed Deposit, Term Policy, Folio Equity
    nominee_ref = Column(String(255), nullable=True)
    status = Column(String(50), default="Unclaimed", nullable=False)
    unclaimed_status = Column(String(100), default="Dormant > 10 Yrs", nullable=True)
    approximate_value = Column(Float, default=0.0)
    details_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    institution = sa_relationship("Institution", back_populates="financial_assets")
    matches = sa_relationship("AssetMatch", back_populates="financial_asset")
    claims = sa_relationship("Claim", back_populates="financial_asset")


class AssetMatch(Base):
    __tablename__ = "asset_matches"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    deceased_person_id = Column(String(36), ForeignKey("deceased_persons.id"), nullable=False)
    financial_asset_id = Column(String(36), ForeignKey("financial_assets.id"), nullable=False)
    matching_score = Column(Integer, nullable=False)
    matching_reason = Column(Text, nullable=False)
    match_category = Column(String(50), nullable=False)  # Strong potential match, Requires manual review
    review_status = Column(String(50), default="Pending", nullable=False)  # Pending, Approved, Rejected
    created_at = Column(DateTime, default=datetime.utcnow)

    deceased_person = sa_relationship("DeceasedPerson", back_populates="matches")
    financial_asset = sa_relationship("FinancialAsset", back_populates="matches")
    claim = sa_relationship("Claim", back_populates="asset_match", uselist=False)


class Claim(Base):
    __tablename__ = "claims"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    claim_reference = Column(String(50), unique=True, nullable=False)
    claimant_id = Column(String(36), ForeignKey("claimants.id"), nullable=False)
    asset_match_id = Column(String(36), ForeignKey("asset_matches.id"), nullable=False)
    deceased_person_id = Column(String(36), ForeignKey("deceased_persons.id"), nullable=False)
    financial_asset_id = Column(String(36), ForeignKey("financial_assets.id"), nullable=False)
    institution_id = Column(String(36), ForeignKey("institutions.id"), nullable=False)
    status = Column(String(50), default="Submitted", nullable=False)  # Submitted, Under Review, Documents Required, Approved, Rejected, Completed
    remarks = Column(Text, nullable=True)
    submission_date = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    claimant = sa_relationship("Claimant", back_populates="claims")
    asset_match = sa_relationship("AssetMatch", back_populates="claim")
    deceased_person = sa_relationship("DeceasedPerson", back_populates="claims")
    financial_asset = sa_relationship("FinancialAsset", back_populates="claims")
    institution = sa_relationship("Institution", back_populates="claims")
    documents = sa_relationship("Document", back_populates="claim")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("profiles.id"), nullable=False)
    deceased_person_id = Column(String(36), ForeignKey("deceased_persons.id"), nullable=True)
    claimant_id = Column(String(36), ForeignKey("claimants.id"), nullable=True)
    claim_id = Column(String(36), ForeignKey("claims.id"), nullable=True)
    document_type = Column(String(100), nullable=False)  # death_certificate, id_proof, heir_proof, etc.
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    content_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = sa_relationship("User", back_populates="documents")
    deceased_person = sa_relationship("DeceasedPerson", back_populates="documents")
    claimant = sa_relationship("Claimant", back_populates="documents")
    claim = sa_relationship("Claim", back_populates="documents")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("profiles.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="system", nullable=False)  # verification, match_found, claim_update, doc_request, system
    link = Column(String(255), nullable=True)
    is_read = Column(Boolean, default=False)
    email_sent = Column(Boolean, default=False)
    email_logs = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = sa_relationship("User", back_populates="notifications")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
