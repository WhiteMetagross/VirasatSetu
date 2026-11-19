import re
from difflib import SequenceMatcher
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.models.models import DeceasedPerson, FinancialAsset, AssetMatch, AuditLog
from app.services.notification_service import send_notification

def normalize_text(text: str) -> str:
    if not text:
        return ""
    # Remove honorifics, extra whitespace, convert to lower
    text = re.sub(r'\b(mr|mrs|ms|shri|smt|late|dr)\.?\b', '', text, flags=re.IGNORECASE)
    return " ".join(text.lower().strip().split())

def calculate_name_similarity(name1: str, name2: str) -> Tuple[int, str]:
    n1 = normalize_text(name1)
    n2 = normalize_text(name2)
    if not n1 or not n2:
        return 0, "No name provided"
    
    if n1 == n2:
        return 25, f"Exact Name Match ('{name1}' == '{name2}')"
    
    # Token set check (like 'Rajesh Kumar' vs 'Kumar Rajesh')
    tokens1 = set(n1.split())
    tokens2 = set(n2.split())
    if tokens1 and tokens1 == tokens2:
        return 23, f"Name Token Match ('{name1}' ~ '{name2}')"

    ratio = SequenceMatcher(None, n1, n2).ratio()
    if ratio >= 0.85:
        score = int(25 * ratio)
        return score, f"High Name Similarity ({int(ratio * 100)}%)"
    elif ratio >= 0.65:
        score = int(18 * ratio)
        return score, f"Moderate Name Similarity ({int(ratio * 100)}%)"
    return 0, f"Low Name Similarity ({int(ratio * 100)}%)"

def run_matching_for_deceased(db: Session, deceased_id: str) -> List[AssetMatch]:
    deceased = db.query(DeceasedPerson).filter(DeceasedPerson.id == deceased_id).first()
    if not deceased or deceased.status != "Verified":
        return []

    # Get all active/unclaimed financial assets
    assets = db.query(FinancialAsset).all()

    # Clear previous matches for this deceased person to avoid duplicates upon re-matching
    db.query(AssetMatch).filter(AssetMatch.deceased_person_id == deceased_id).delete()
    db.commit()

    generated_matches = []

    for asset in assets:
        score = 0
        reasons = []

        # 1. Identity Reference Match (50 points)
        dec_id_ref = deceased.sample_identity_ref.strip().upper() if deceased.sample_identity_ref else ""
        ast_id_ref = asset.sample_identity_ref.strip().upper() if asset.sample_identity_ref else ""

        if dec_id_ref and ast_id_ref and dec_id_ref == ast_id_ref:
            score += 50
            reasons.append(f"Exact Identity Match: {dec_id_ref} (+50 pts)")
        elif dec_id_ref and ast_id_ref and (dec_id_ref in ast_id_ref or ast_id_ref in dec_id_ref):
            score += 30
            reasons.append(f"Partial Identity Reference Match (+30 pts)")

        # 2. Name Similarity Match (25 points)
        name_score, name_reason = calculate_name_similarity(deceased.full_name, asset.holder_name)
        if name_score > 0:
            score += name_score
            reasons.append(f"{name_reason} (+{name_score} pts)")

        # 3. Exact Date of Birth Match (15 points)
        if deceased.date_of_birth and asset.date_of_birth:
            if deceased.date_of_birth.strip() == asset.date_of_birth.strip():
                score += 15
                reasons.append(f"Exact Date of Birth Match ({deceased.date_of_birth}) (+15 pts)")
            elif deceased.date_of_birth[:4] == asset.date_of_birth[:4]:
                score += 8
                reasons.append(f"Same Birth Year ({deceased.date_of_birth[:4]}) (+8 pts)")

        # 4. Other Reference Details: Nominee / Location (10 points)
        other_pts = 0
        if asset.nominee_ref:
            # Check if any claimant of deceased or family member surname appears in nominee
            nominee_norm = normalize_text(asset.nominee_ref)
            dec_last_name = deceased.full_name.strip().split()[-1].lower() if deceased.full_name else ""
            if dec_last_name and dec_last_name in nominee_norm:
                other_pts += 10
                reasons.append(f"Nominee Family Connection '{asset.nominee_ref}' (+10 pts)")
        
        if other_pts == 0 and deceased.last_known_city and asset.details_json:
            if deceased.last_known_city.lower() in asset.details_json.lower():
                other_pts += 5
                reasons.append(f"Location / Branch City Match ({deceased.last_known_city}) (+5 pts)")

        score += other_pts
        score = min(score, 100)

        # Qualification threshold: 60 or above
        if score >= 60:
            category = "Strong potential match" if score >= 80 else "Requires manual review"
            match_entry = AssetMatch(
                deceased_person_id=deceased.id,
                financial_asset_id=asset.id,
                matching_score=score,
                matching_reason="; ".join(reasons),
                match_category=category,
                review_status="Approved" if score >= 80 else "Pending"
            )
            db.add(match_entry)
            generated_matches.append(match_entry)

    db.commit()

    # Log audit
    audit = AuditLog(
        user_id=deceased.user_id,
        action="MATCHING_EXECUTED",
        entity_type="deceased_person",
        entity_id=deceased.id,
        details=f"Matching algorithm executed for '{deceased.full_name}'. Found {len(generated_matches)} potential financial records."
    )
    db.add(audit)
    db.commit()

    # Send Notification to submitter user if matches were discovered
    if generated_matches:
        send_notification(
            db=db,
            user_id=deceased.user_id,
            title="Potential Financial Assets Discovered",
            message=(
                f"Great news! Virasat Setu automated discovery identified {len(generated_matches)} potential "
                f"unclaimed financial record(s) matching your submitted record for '{deceased.full_name}'. "
                "Please review your dashboard and submit claimant heir verification to initiate claims."
            ),
            notification_type="match_found",
            link=f"/dashboard/deceased/{deceased.id}/matches"
        )

    return generated_matches
