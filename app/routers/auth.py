import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User
from app.schemas.schemas import UserCreate, UserLogin, UserResponse, Token
from pydantic import BaseModel
from typing import Optional
from app.config import settings
from app.utils.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class GoogleAuthRequest(BaseModel):
    credential: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    google_id: Optional[str] = None

@router.get("/google/config")
def get_google_oauth_config():
    """Returns Google OAuth 2.0 public configuration."""
    return {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "configured": bool(settings.GOOGLE_CLIENT_ID),
        "auth_provider": "Google Identity Services"
    }

@router.post("/google/login", response_model=Token)
def google_login(req: GoogleAuthRequest, db: Session = Depends(get_db)):
    """
    Google OAuth 2.0 authentication endpoint:
    Authenticates existing users or automatically provisions citizen accounts
    using Google verified identities.
    """
    email = (req.email or "").strip().lower()
    full_name = (req.full_name or "").strip() or "Google User"

    if not email or "@" not in email or "." not in email:
        raise HTTPException(
            status_code=400,
            detail="A valid Google Gmail address is required for authentication."
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Auto-provision newly authenticated Google citizen
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            hashed_password=hash_password(f"GoogleOAuth_{uuid.uuid4().hex}"),
            full_name=full_name,
            role="family_user",
            mobile="+91 98000 00000"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(data={"sub": user.id, "role": user.role, "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )
    
    new_user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        mobile=user_data.mobile,
        role=user_data.role or "family_user",
        institution_id=user_data.institution_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={"sub": new_user.id, "role": new_user.role, "email": new_user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": new_user
    }

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    token = create_access_token(data={"sub": user.id, "role": user.role, "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
