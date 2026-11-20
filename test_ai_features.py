"""
Comprehensive AI Features Verification Suite for Virasat Setu:
Validates Google OAuth 2.0 integration, Virasat AI Legal Copilot,
Machine Learning Indian Transliteration matching, Claim Success Predictor,
and Administrator Restricted Fraud Anomaly Detection.
"""

import json
import urllib.request
import urllib.error
from app.services.matching_service import calculate_name_similarity

BASE_URL = "http://127.0.0.1:8000"


def make_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    encoded_data = None
    if data is not None:
        if isinstance(data, (dict, list)):
            encoded_data = json.dumps(data).encode("utf-8")
            if "Content-Type" not in headers:
                headers["Content-Type"] = "application/json"
        elif isinstance(data, bytes):
            encoded_data = data

    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            body = res.read().decode("utf-8")
            try:
                parsed = json.loads(body)
            except Exception:
                parsed = body
            return res.status, parsed
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = body
        return err.code, parsed


def test_google_oauth_endpoints():
    print("Testing Google OAuth 2.0 integration:")
    # 1. Config endpoint
    status, config = make_request(f"{BASE_URL}/api/auth/google/config")
    assert status == 200, f"Expected 200 for Google config, got {status}"
    assert "auth_provider" in config, "Missing auth_provider in Google config."
    print("Google OAuth 2.0 public configuration verified successfully.")

    # 2. Login endpoint
    status, auth_res = make_request(
        f"{BASE_URL}/api/auth/google/login",
        method="POST",
        data={
            "email": "test.google.citizen@gmail.com",
            "full_name": "Test Google Citizen"
        }
    )
    assert status == 200, f"Expected 200 for Google sign in, got {status}"
    assert "access_token" in auth_res, "Missing access_token in Google auth response."
    assert auth_res["user"]["role"] == "family_user", "Google user should default to family_user role."
    print("Google OAuth 2.0 login and citizen auto provisioning verified successfully.")
    return auth_res["access_token"]


def test_ai_copilot_service():
    print("Testing Virasat AI Legal Copilot endpoint:")
    test_queries = [
        "What is the difference between nominee rights and legal heir rights in Indian banking?",
        "How to claim a deceased bank account at State Bank of India without a succession certificate?",
        "What documents are needed for LIC life insurance death claim settlement?"
    ]

    for q in test_queries:
        status, copilot_res = make_request(
            f"{BASE_URL}/api/ai/copilot",
            method="POST",
            data={"query": q}
        )
        assert status == 200, f"Expected 200 for AI Copilot, got {status}"
        assert len(copilot_res["answer"]) > 50, "AI Copilot returned an empty or abbreviated answer."
        assert "source" in copilot_res, "Missing source attribute in AI response."
        assert len(copilot_res.get("followups", [])) > 0, "AI Copilot should suggest follow up questions."
        print(f"Copilot query resolved successfully (Source: {copilot_res['source']}): {q[:45]}...")

    print("Virasat AI Copilot functionality verified successfully.")


def test_ml_transliteration_matching():
    print("Testing Machine Learning Indian Name Transliteration Engine:")
    name_pairs = [
        ("Laxmi Devi", "Lakshmi Devi"),
        ("Rameshwar Dayal Agarwal", "Rameshwar Dayal Aggarwal"),
        ("Sunil Choudhary", "Sunil Chowdhury"),
        ("Virender Singh", "Virendra Singh")
    ]

    for n1, n2 in name_pairs:
        score, reason = calculate_name_similarity(n1, n2)
        assert score >= 20, f"Expected ML transliteration score >= 20 for '{n1}' vs '{n2}', got {score}"
        print(f"ML Transliteration Match: '{n1}' vs '{n2}' -> Score: {score}/25 ({reason})")

    print("Machine Learning Indian Transliteration Engine verified successfully.")


def test_claim_health_predictor(token):
    print("Testing AI Claim Health Predictor:")
    # First get an existing match for Ramesh Kumar
    status, matches = make_request(
        f"{BASE_URL}/api/deceased",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert status == 200, "Failed to retrieve deceased records."

    # Login as demo family user
    status, family_login = make_request(
        f"{BASE_URL}/api/auth/login",
        method="POST",
        data={"email": "rajesh.family@example.com", "password": "family123"}
    )
    family_token = family_login["access_token"]

    status, dec_list = make_request(
        f"{BASE_URL}/api/deceased",
        headers={"Authorization": f"Bearer {family_token}"}
    )
    rajesh = next(r for r in dec_list if r["full_name"] == "Rajesh Kumar")

    status, matches = make_request(
        f"{BASE_URL}/api/matches/{rajesh['id']}",
        headers={"Authorization": f"Bearer {family_token}"}
    )
    assert len(matches) > 0, "No matches found for Rajesh Kumar."
    test_match_id = matches[0]["id"]

    # Call AI claim health predictor
    status, pred = make_request(
        f"{BASE_URL}/api/ai/predict-claim",
        method="POST",
        data={
            "asset_match_id": test_match_id,
            "claimant_name": "Ramesh Kumar",
            "claimant_relationship": "Son"
        },
        headers={"Authorization": f"Bearer {family_token}"}
    )
    assert status == 200, f"Expected 200 for claim prediction, got {status}"
    assert pred["probability"] >= 60, f"Expected high probability for son of verified deceased, got {pred['probability']}"
    assert len(pred["factors"]) > 0, "Missing predictive strength factors."
    print(f"Claim Health Prediction verified: {pred['probability']}% ({pred['status']})")


def test_fraud_anomaly_detection_rbac(family_token):
    print("Testing AI Fraud Anomaly Detection Role Based Access Control:")
    # 1. Family user should be rejected with 403 Forbidden
    status, res = make_request(
        f"{BASE_URL}/api/ai/admin/fraud-anomalies",
        headers={"Authorization": f"Bearer {family_token}"}
    )
    assert status == 403, f"Expected 403 Forbidden for family user, got {status}"
    print("Fraud Anomaly panel access properly restricted: Family citizen rejected with 403 Forbidden.")

    # 2. Administrator user should be permitted
    status, admin_login = make_request(
        f"{BASE_URL}/api/auth/login",
        method="POST",
        data={"email": "admin@virasatsetu.gov.in", "password": "admin123"}
    )
    admin_token = admin_login["access_token"]

    status, anomalies = make_request(
        f"{BASE_URL}/api/ai/admin/fraud-anomalies",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert status == 200, f"Expected 200 for admin, got {status}"
    assert isinstance(anomalies, list), "Expected list of anomaly objects."
    print(f"Administrator Fraud Anomaly Intelligence Center verified: {len(anomalies)} anomaly items evaluated.")


def run_all():
    print("STARTING AI AND OAUTH VERIFICATION SUITE:")
    token = test_google_oauth_endpoints()
    test_ai_copilot_service()
    test_ml_transliteration_matching()
    test_claim_health_predictor(token)
    test_fraud_anomaly_detection_rbac(token)
    print("ALL AI MODULES AND GOOGLE OAUTH SUITES PASSED SUCCESSFULLY WITH ZERO ERRORS.")


if __name__ == "__main__":
    run_all()
