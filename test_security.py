"""
Security Verification Suite for Virasat Setu Platform:
Validates cybersecurity defenses including SQL injection prevention,
Cross Site Scripting (XSS) defense, Cross Site Request Forgery (CSRF) protection,
HTTP security headers, file upload security, and IDOR access control.
"""

import json
import uuid
import urllib.request
import urllib.error

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
            response_headers = dict(res.headers)
            try:
                parsed = json.loads(body)
            except Exception:
                parsed = body
            return res.status, parsed, response_headers
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8")
        response_headers = dict(err.headers)
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = body
        return err.code, parsed, response_headers


def test_security_headers():
    print("Testing HTTP defensive security headers:")
    status_code, body, headers = make_request(f"{BASE_URL}/")
    assert status_code == 200, f"Expected 200 but received {status_code}"

    csp = headers.get("content-security-policy", "")
    assert "default-src 'self'" in csp, "Content Security Policy missing expected default-src directive."
    assert "frame-ancestors 'none'" in csp, "Content Security Policy missing frame ancestors directive."

    assert headers.get("x-frame-options") == "DENY", "X Frame Options header missing or not DENY."
    assert headers.get("x-content-type-options") == "nosniff", "X Content Type Options header missing or not nosniff."
    assert headers.get("x-xss-protection") == "1; mode=block", "X XSS Protection header missing or incorrect."
    assert headers.get("referrer-policy") == "strict-origin-when-cross-origin", "Referrer Policy header missing or incorrect."
    assert headers.get("cross-origin-opener-policy") == "same-origin", "COOP header missing or incorrect."
    print("Defensive security headers verified successfully.")


def test_csrf_protection():
    print("Testing CSRF protection on state modifying API endpoints:")
    # 1. State modifying request without any auth or CSRF client header should be rejected
    status_code, body, _ = make_request(
        f"{BASE_URL}/api/claims",
        method="POST",
        data={"asset_match_id": "test-match", "remarks": "Test Remarks"}
    )
    assert status_code == 403, f"Expected 403 Forbidden for state change without CSRF header, got {status_code}"
    assert "CSRF verification failed" in str(body), f"Unexpected response message: {body}"
    print("CSRF protection rejected state modifying request missing client verification headers.")

    # 2. State modifying request with custom client header passes CSRF layer
    status_code, body, _ = make_request(
        f"{BASE_URL}/api/claims",
        method="POST",
        data={"asset_match_id": "test-match", "remarks": "Test Remarks"},
        headers={"X-CSRF-Token": "virasat-setu-csrf-protection"}
    )
    # The CSRF layer allows it through; the endpoint then requires bearer authentication (401)
    assert status_code == 401, f"Expected 401 Authentication Required after passing CSRF layer, got {status_code}"
    print("CSRF protection correctly permitted request carrying authorized custom client header.")


def test_sql_injection_defense():
    print("Testing SQL injection signature detection and input sanitization:")
    sqli_payloads = [
        "Robert'; DROP TABLE users;",
        "Administrator' OR '1'='1",
        "UNION ALL SELECT null, null, null",
        "User'; DELETE FROM financial_assets;"
    ]

    for payload in sqli_payloads:
        unique_email = f"sqli_{uuid.uuid4().hex[:8]}@example.com"
        status_code, body, _ = make_request(
            f"{BASE_URL}/api/auth/register",
            method="POST",
            data={
                "email": unique_email,
                "password": "Password123",
                "full_name": payload,
                "role": "family_user"
            },
            headers={"X-CSRF-Token": "virasat-setu-csrf-protection"}
        )
        assert status_code == 400, f"Expected 400 Bad Request for SQL injection payload, got {status_code}"
        assert "Security alert" in str(body), f"Expected security alert in response, got {body}"
        print(f"SQL injection attempt blocked: {payload}")

    print("SQL injection defense in depth verified successfully.")


def test_xss_prevention():
    print("Testing Cross Site Scripting prevention and input sanitization:")
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert(1)>",
        "javascript:alert(document.cookie)",
        "<iframe src='javascript:alert(1)'></iframe>"
    ]

    for payload in xss_payloads:
        unique_email = f"xss_{uuid.uuid4().hex[:8]}@example.com"
        status_code, body, _ = make_request(
            f"{BASE_URL}/api/auth/register",
            method="POST",
            data={
                "email": unique_email,
                "password": "Password123",
                "full_name": payload,
                "role": "family_user"
            },
            headers={"X-CSRF-Token": "virasat-setu-csrf-protection"}
        )
        assert status_code == 400, f"Expected 400 Bad Request for XSS payload, got {status_code}"
        assert "Security alert" in str(body), f"Expected security alert in response, got {body}"
        print(f"XSS payload attempt blocked: {payload}")

    print("XSS prevention verified successfully.")


def test_document_security():
    print("Testing document repository security and IDOR protection:")
    # 1. Login as family user
    status_code, family_login, _ = make_request(
        f"{BASE_URL}/api/auth/login",
        method="POST",
        data={"email": "rajesh.family@example.com", "password": "family123"},
        headers={"X-CSRF-Token": "virasat-setu-csrf-protection"}
    )
    assert status_code == 200, "Family login failed."
    family_token = family_login["access_token"]

    # 2. Test malicious file upload rejection via multipart upload
    boundary = "----SecurityTestBoundary12345"
    malicious_files = [
        ("malicious.exe", b"MZ executable content", "application/x-msdownload"),
        ("exploit.html", b"<script>alert(1)</script>", "text/html"),
        ("../../etc/passwd.pdf", b"%PDF-1.4 sample content", "application/pdf")
    ]

    for filename, content, mime in malicious_files:
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f"Content-Type: {mime}\r\n\r\n"
        ).encode("utf-8") + content + f"\r\n--{boundary}--\r\n".encode("utf-8")

        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Authorization": f"Bearer {family_token}",
            "X-CSRF-Token": "virasat-setu-csrf-protection"
        }

        status_code, response, _ = make_request(
            f"{BASE_URL}/api/documents/upload?document_type=Identity+Proof",
            method="POST",
            data=body,
            headers=headers
        )
        assert status_code == 400, f"Expected 400 for unsafe upload {filename}, got {status_code}"
        print(f"Malicious upload blocked: {filename}")

    # 3. Test valid PDF upload
    valid_pdf_content = b"%PDF-1.4 valid test pdf file content for inheritance verification"
    valid_body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="identity_proof.pdf"\r\n'
        f"Content-Type: application/pdf\r\n\r\n"
    ).encode("utf-8") + valid_pdf_content + f"\r\n--{boundary}--\r\n".encode("utf-8")

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Authorization": f"Bearer {family_token}",
        "X-CSRF-Token": "virasat-setu-csrf-protection"
    }

    status_code, upload_res, _ = make_request(
        f"{BASE_URL}/api/documents/upload?document_type=Identity+Proof",
        method="POST",
        data=valid_body,
        headers=headers
    )
    assert status_code == 200, f"Expected 200 for valid PDF upload, got {status_code}"
    doc_id = upload_res["id"]
    print("Valid PDF document upload accepted successfully.")

    # 4. Test IDOR protection: Register a new distinct user and attempt to download User A document
    other_email = f"other_{uuid.uuid4().hex[:8]}@example.com"
    status_code, reg_res, _ = make_request(
        f"{BASE_URL}/api/auth/register",
        method="POST",
        data={
            "email": other_email,
            "password": "Password123",
            "full_name": "Unrelated User",
            "role": "family_user"
        },
        headers={"X-CSRF-Token": "virasat-setu-csrf-protection"}
    )
    assert status_code == 200, "Registration for other user failed."
    other_token = reg_res["access_token"]

    status_code, idor_res, _ = make_request(
        f"{BASE_URL}/api/documents/{doc_id}/download",
        method="GET",
        headers={"Authorization": f"Bearer {other_token}"}
    )
    assert status_code == 403, f"Expected 403 Forbidden for IDOR attempt, got {status_code}"
    print("IDOR access control check verified successfully: Unauthorized user cannot download document.")


def run_all_security_tests():
    print("STARTING COMPREHENSIVE CYBERSECURITY VALIDATION SUITE:")
    test_security_headers()
    test_csrf_protection()
    test_sql_injection_defense()
    test_xss_prevention()
    test_document_security()
    print("ALL CYBERSECURITY DEFENSES VERIFIED SUCCESSFULLY: ZERO VULNERABILITIES DETECTED.")


if __name__ == "__main__":
    run_all_security_tests()
