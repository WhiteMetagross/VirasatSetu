"""
AI Claim Success Predictor and Fraud Anomaly Detection Service:
Calculates claim approval probability for citizens and provides an
exclusive fraud and anomaly risk panel for administrators and institutions.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.models import Claim, AssetMatch, FinancialAsset, Claimant, DeceasedPerson, Document


def predict_claim_approval(
    asset_match_id: str,
    claimant_id: str = None,
    claimant_name: str = None,
    claimant_relationship: str = None,
    db: Session = None
) -> Dict[str, Any]:
    """
    Evaluates claim parameters and calculates approval likelihood probability
    with prescriptive recommendations for the citizen before formal submission.
    """
    if not db:
        return {"probability": 75, "status": "Moderate Likelihood", "factors": [], "advice": []}

    match = db.query(AssetMatch).filter(AssetMatch.id == asset_match_id).first()
    if not match:
        return {"probability": 50, "status": "Moderate Likelihood", "factors": [], "advice": []}

    asset = match.financial_asset
    deceased = match.deceased_person

    score = 0
    factors = []
    advice = []

    # 1. Matching Engine Strength (up to 40%)
    if match.matching_score >= 90:
        score += 40
        factors.append(f"Strong Automated Match Evidence ({match.matching_score}/100 points)")
    elif match.matching_score >= 70:
        score += 30
        factors.append(f"Moderate Automated Match Evidence ({match.matching_score}/100 points)")
    else:
        score += 15
        factors.append(f"Basic Match Evidence ({match.matching_score}/100 points)")
        advice.append("Provide secondary identity proof to elevate match confidence.")

    # 2. Deceased Civil Verification Status (up to 25%)
    if deceased and deceased.status == "Verified":
        score += 25
        factors.append("Deceased Municipal Record Verified by Civil Authority")
    else:
        score += 5
        factors.append("Deceased Record Civil Verification in Progress")
        advice.append("Await administrator civil verification before final institutional sign off.")

    # 3. Claimant Relationship and Nominee Alignment (up to 20%)
    rel = (claimant_relationship or "").lower()
    nominee = (asset.nominee_ref or "").lower() if asset else ""

    if nominee and claimant_name and claimant_name.lower() in nominee:
        score += 20
        factors.append("Claimant Name Matches Official Nominee on File")
    elif rel in ["son", "daughter", "spouse", "mother", "father", "wife", "husband"]:
        score += 15
        factors.append(f"Primary Class 1 Legal Heir Declared ({claimant_relationship})")
    elif rel in ["brother", "sister", "nominee", "grandson", "granddaughter"]:
        score += 10
        factors.append(f"Recognized Kinship ({claimant_relationship})")
    else:
        score += 5
        advice.append("Attach Legal Heir Certificate from Tahsildar to substantiate kinship.")

    # 4. Uploaded Documentation Presence (up to 15%)
    if deceased:
        docs = db.query(Document).filter(Document.deceased_person_id == deceased.id).all()
        if len(docs) >= 2:
            score += 15
            factors.append("Supporting Civil and Succession Documents Uploaded")
        elif len(docs) == 1:
            score += 10
            factors.append("Single Verification Document Attached")
            advice.append("Upload succession or legal heir certificate to maximize approval speed.")
        else:
            advice.append("Uploading an identity proof and death certificate expedites settlement.")

    score = min(max(score, 25), 98)

    status_label = "High Approval Likelihood" if score >= 80 else "Moderate Approval Likelihood" if score >= 60 else "Action Required"

    return {
        "probability": score,
        "status": status_label,
        "factors": factors,
        "advice": advice,
        "asset_type": asset.asset_type if asset else "unknown",
        "institution_name": asset.institution_name if asset else "Institution"
    }


def detect_fraud_and_anomalies(db: Session) -> List[Dict[str, Any]]:
    """
    Scans platform claims and financial assets to identify anomalies, duplicate
    claim conflicts, and high value dormancy risks.
    STRICTLY ACCESSIBLE BY ADMINISTRATORS AND INSTITUTION REPRESENTATIVES ONLY.
    """
    anomalies = []

    claims = db.query(Claim).all()

    # 1. Detect Duplicate Claim Conflict (multiple claims for same financial asset)
    asset_claim_map: Dict[str, List[Claim]] = {}
    for c in claims:
        asset_claim_map.setdefault(c.financial_asset_id, []).append(c)

    for asset_id, mapped_claims in asset_claim_map.items():
        if len(mapped_claims) > 1:
            first_c = mapped_claims[0]
            first_ast = first_c.financial_asset
            first_inst = first_c.institution
            claimants = [f"{c.claimant.name if c.claimant else 'Heir'} ({c.claim_reference})" for c in mapped_claims]
            anomalies.append({
                "id": f"anom_dup_{asset_id[:8]}",
                "risk_level": "High Risk",
                "risk_score": 92,
                "category": "Duplicate Claim Conflict",
                "asset_reference": (first_ast.account_ref if first_ast else first_c.claim_reference),
                "institution_name": (first_inst.name if first_inst else "Financial Institution"),
                "details": f"Detected {len(mapped_claims)} conflicting claims submitted for the same asset folio: {', '.join(claimants)}.",
                "recommended_action": "Freeze claim disbursement pending civil court interpleader or mutual NOC verification."
            })

    # 2. Detect High Value Dormancy without Civil Verification
    for c in claims:
        ast = c.financial_asset
        inst = c.institution
        approx_val = ast.approximate_value if ast else 0.0
        if approx_val >= 500000.0:  # Over 5 Lakhs
            deceased = db.query(DeceasedPerson).filter(DeceasedPerson.id == c.deceased_person_id).first()
            if deceased and deceased.status != "Verified":
                anomalies.append({
                    "id": f"anom_highval_{c.id[:8]}",
                    "risk_level": "Medium Risk",
                    "risk_score": 74,
                    "category": "High Valuation Unverified Profile",
                    "asset_reference": (ast.account_ref if ast else c.claim_reference),
                    "institution_name": (inst.name if inst else "Financial Institution"),
                    "details": f"Claim {c.claim_reference} exceeds ₹5,00,000 threshold while deceased record is still pending civil verification.",
                    "recommended_action": "Mandate Succession Certificate under Indian Succession Act 1925 before approval."
                })

    # 3. Detect Missing Claimant Legal Capacity
    for c in claims:
        clm = c.claimant
        inst = c.institution
        ast = c.financial_asset
        rel = (getattr(clm, "relationship_to_deceased", None) or getattr(clm, "relationship", "") or "").lower()
        if not rel or rel == "other":
            anomalies.append({
                "id": f"anom_rel_{c.id[:8]}",
                "risk_level": "Medium Risk",
                "risk_score": 65,
                "category": "Unspecified Claimant Capacity",
                "asset_reference": (ast.account_ref if ast else c.claim_reference),
                "institution_name": (inst.name if inst else "Financial Institution"),
                "details": f"Claimant {clm.name if clm else 'Citizen'} filed claim {c.claim_reference} without specifying recognized kinship class.",
                "recommended_action": "Request family tree affidavit and Tahsildar Legal Heir certificate."
            })

    # Sort anomalies by risk score descending
    anomalies.sort(key=lambda x: x["risk_score"], reverse=True)
    return anomalies
