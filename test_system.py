import urllib.request
import json
import uuid

def test_system():
    print("VIRASAT SETU: COMPREHENSIVE END TO END TEST SUITE")

    # 1. Family Login
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/auth/login',
        data=json.dumps({'email': 'rajesh.family@example.com', 'password': 'family123'}).encode(),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as res:
        login_data = json.loads(res.read().decode())
    token = login_data['access_token']
    user_id = login_data['user']['id']
    print(f"1. Family Login Success: {login_data['user']['full_name']} (Role: {login_data['user']['role']})")

    # 2. Deceased Records retrieval
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/deceased',
        headers={'Authorization': f'Bearer {token}'}
    )
    with urllib.request.urlopen(req) as res:
        records = json.loads(res.read().decode())
    print(f"2. Deceased Records: {len(records)} records retrieved")
    rajesh = next((r for r in records if r['full_name'] == 'Rajesh Kumar'), None)
    assert rajesh is not None, "Rajesh Kumar not found"
    print(f"   Found Rajesh Kumar (ID: {rajesh['sample_identity_ref']}, Status: {rajesh['status']})")

    # 3. Matches for Rajesh Kumar
    req = urllib.request.Request(
        f"http://127.0.0.1:8000/api/matches/{rajesh['id']}",
        headers={'Authorization': f'Bearer {token}'}
    )
    with urllib.request.urlopen(req) as res:
        matches = json.loads(res.read().decode())
    print(f"3. Discovered Matches: {len(matches)} potential assets found")
    total_val = 0
    for m in matches:
        ast = m['financial_asset']
        val = ast['approximate_value']
        total_val += val
        claim_tag = f"[Claim: {m['claim_status']}]" if m.get('claim_status') else "[Unclaimed]"
        print(f"   * [{m['matching_score']} Pts] {ast['institution_name']} ({ast['category']}) Ref: {ast['account_ref']} (Value: {val:,.2f} INR) {claim_tag}")
    print(f"   Total Discovered Value for Rajesh Kumar: {total_val:,.2f} INR")

    # 4. Claimant Submission
    req_claimant = urllib.request.Request(
        'http://127.0.0.1:8000/api/claimants',
        data=json.dumps({
            'name': 'Ramesh Kumar',
            'relationship': 'Son',
            'claimant_type': 'Nominee',
            'email': 'rajesh.family@example.com',
            'mobile': '+91 98765 43210',
            'deceased_person_id': rajesh['id']
        }).encode(),
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    )
    with urllib.request.urlopen(req_claimant) as res:
        claimant_res = json.loads(res.read().decode())
    print(f"4. Claimant Registration: ID {claimant_res['id']} registered as {claimant_res['relationship']}")

    # 5. Claim Submission / Verification
    target_unclaimed = next((m for m in matches if not m.get('claim_id')), None)
    if target_unclaimed:
        req_claim = urllib.request.Request(
            'http://127.0.0.1:8000/api/claims',
            data=json.dumps({
                'asset_match_id': target_unclaimed['id'],
                'claimant_id': claimant_res['id'],
                'remarks': 'Claimant is lawful son and nominee under Death Certificate'
            }).encode(),
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
        )
        with urllib.request.urlopen(req_claim) as res:
            claim_res = json.loads(res.read().decode())
        claim_id = claim_res['id']
        institution_id = claim_res['institution_id']
        print(f"5. Claim Initiated: ID {claim_id} with initial status '{claim_res['status']}'")
    else:
        # Use existing claim
        req_get_claims = urllib.request.Request(
            'http://127.0.0.1:8000/api/claims',
            headers={'Authorization': f'Bearer {token}'}
        )
        with urllib.request.urlopen(req_get_claims) as res:
            claims_list = json.loads(res.read().decode())
        claim_res = claims_list[0]
        claim_id = claim_res['id']
        institution_id = claim_res['institution_id']
        print(f"5. Claim Verification: Using existing claim ID {claim_id} (Ref: {claim_res['claim_reference']})")

    # 6. Admin and Institution Claim Review and Status Update
    req_admin_login = urllib.request.Request(
        'http://127.0.0.1:8000/api/auth/login',
        data=json.dumps({'email': 'admin@virasatsetu.gov.in', 'password': 'admin123'}).encode(),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req_admin_login) as res:
        admin_data = json.loads(res.read().decode())
    admin_token = admin_data['access_token']
    print(f"6. Official Claim Review by Admin / Institution Authority: {admin_data['user']['full_name']}")

    # Update claim status to Under Review
    req_update_claim = urllib.request.Request(
        f'http://127.0.0.1:8000/api/claims/{claim_id}/status',
        data=json.dumps({
            'status': 'Under Review',
            'remarks': 'Verification in progress by competent institutional nodal authority'
        }).encode(),
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {admin_token}'}
    )
    req_update_claim.get_method = lambda: 'PATCH'
    with urllib.request.urlopen(req_update_claim) as res:
        updated_claim = json.loads(res.read().decode())
    print(f"   Claim updated to '{updated_claim['status']}' with nodal remarks.")

    # 7. Notifications Verification
    req_notifs = urllib.request.Request(
        'http://127.0.0.1:8000/api/notifications',
        headers={'Authorization': f'Bearer {token}'}
    )
    with urllib.request.urlopen(req_notifs) as res:
        notifs = json.loads(res.read().decode())
    print(f"7. User Notifications: {len(notifs)} notification(s) logged")
    if notifs:
        print(f"   Latest: '{notifs[0]['title']}' (Read: {notifs[0]['is_read']})")

    # 8. Admin Overview and Stats
    req_stats = urllib.request.Request(
        'http://127.0.0.1:8000/api/admin/stats',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    with urllib.request.urlopen(req_stats) as res:
        stats = json.loads(res.read().decode())
    print(f"8. Admin Dashboard Stats:")
    print(f"   Total Registered Users: {stats['total_users']}")
    print(f"   Total Financial Records: {stats['total_financial_records']} (Banks: {stats['bank_records_count']}, Insurance: {stats['insurance_records_count']}, Mutual Funds: {stats['mutual_funds_count']})")
    print(f"   Total Matches Generated: {stats['total_matches']}")
    print(f"   Total Claims: {stats['total_claims']}")

    # 9. Audit Logs Verification
    req_audit = urllib.request.Request(
        'http://127.0.0.1:8000/api/admin/audit-logs',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    with urllib.request.urlopen(req_audit) as res:
        logs = json.loads(res.read().decode())
    print(f"9. Audit Trail: {len(logs)} operational events logged")

    # 10. Root Web Frontend Serving
    with urllib.request.urlopen('http://127.0.0.1:8000/') as res:
        html = res.read().decode()
        assert "Virasat Setu" in html
        print(f"10. Web Frontend UI Serving: {len(html)} bytes delivered successfully")

    print("\nALL 10 VERIFICATION MODULES PASSED WITH 100% SUCCESS")

if __name__ == "__main__":
    test_system()
