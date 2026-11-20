"""
Virasat Setu Artificial Intelligence Router:
Exposes AI Copilot chat, claim success probability prediction,
and administrator exclusive fraud anomaly detection.
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User
from app.utils.auth import get_current_user
from app.services.ai_copilot_service import get_ai_copilot_response
from app.services.fraud_prediction_service import predict_claim_approval, detect_fraud_and_anomalies

router = APIRouter(prefix="/api/ai", tags=["Artificial Intelligence & Copilot"])


class AICopilotRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None


class AICopilotResponse(BaseModel):
    answer: str
    source: str
    followups: List[str] = Field(default_factory=list)


class ClaimPredictionRequest(BaseModel):
    asset_match_id: str
    claimant_id: Optional[str] = None
    claimant_name: Optional[str] = None
    claimant_relationship: Optional[str] = None


class ClaimPredictionResponse(BaseModel):
    probability: int
    status: str
    factors: List[str]
    advice: List[str]
    asset_type: Optional[str] = None
    institution_name: Optional[str] = None


@router.post("/copilot", response_model=AICopilotResponse)
def ask_ai_copilot(req: AICopilotRequest):
    """
    Virasat AI Copilot endpoint:
    Processes citizen queries on succession law, statutory nominee rules,
    and institutional claim procedures using Gemini AI with intelligent fallback.
    """
    res = get_ai_copilot_response(req.query, req.context)
    return AICopilotResponse(
        answer=res["answer"],
        source=res["source"],
        followups=res.get("followups", [])
    )


@router.post("/predict-claim", response_model=ClaimPredictionResponse)
def predict_claim_health(
    req: ClaimPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Predicts claim approval likelihood and surfaces prescriptive advice
    for citizens before formal claim submission.
    """
    prediction = predict_claim_approval(
        asset_match_id=req.asset_match_id,
        claimant_id=req.claimant_id,
        claimant_name=req.claimant_name or current_user.full_name,
        claimant_relationship=req.claimant_relationship,
        db=db
    )
    return ClaimPredictionResponse(**prediction)


@router.get("/admin/fraud-anomalies")
def get_fraud_anomalies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Administrative and Institutional Fraud Anomaly Detection endpoint.
    STRICTLY ACCESSIBLE BY ADMINISTRATORS AND INSTITUTION DESK OFFICERS ONLY.
    """
    if current_user.role not in ["admin", "institution_rep"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted: Fraud anomaly intelligence is reserved for administrators and institutional officers."
        )

    return detect_fraud_and_anomalies(db)
