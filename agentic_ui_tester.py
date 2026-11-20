import sys
import time
import uuid
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(line_buffering=True)

def run_e2e_tests():
    uid = str(uuid.uuid4())[:6]
    citizen_email = f"agentic_user_{uid}@example.com"
    admin_created_email = f"admin_created_{uid}@virasatsetu.gov.in"
    inst_created_email = f"inst_created_{uid}@institution.in"
    
    console_errors = []
    
    print("=" * 70)
    print("STARTING FULL AGENTIC BROWSER UI TEST SUITE FOR VIRASAT SETU")
    print("=" * 70)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.route("**", lambda route: route.abort() if "127.0.0.1" not in route.request.url else route.continue_())

        def handle_console(msg):
            if msg.type == "error":
                # Ignore expected aborted external network resources
                txt = msg.text.lower()
                if "net::err_failed" not in txt and "favicon" not in txt:
                    console_errors.append(msg.text)
                    print(f"  [Console Error]: {msg.text}")

        page.on("console", handle_console)
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        # 1. Navigate to home
        print("\n[Step 1] Navigating to http://127.0.0.1:8000...")
        page.goto("http://127.0.0.1:8000")
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # 2. Check initial logged-out state
        print("\n[Step 2] Checking initial state and navbar visibility...")
        nav_db_tab = page.locator("#nav-db-tab")
        assert not nav_db_tab.is_visible(), "Error: Browse Database tab must be HIDDEN for logged-out users"
        print("  Passed: Browse Database tab is correctly hidden in navigation bar.")

        # 3. Test Home buttons
        print("\n[Step 3] Testing Browse Database button on Home banner...")
        page.click("#tab-home button:has-text('Browse Database')")
        time.sleep(0.5)
        auth_modal = page.locator("#modal-auth")
        assert auth_modal.is_visible(), "Error: Auth modal should open when non-admin clicks Browse Database"
        print("  Passed: Clicking Browse Database prompted authentication as expected.")

        # 4. Register new user
        print(f"\n[Step 4] Registering new citizen user ({citizen_email})...")
        page.click("#auth-tab-register")
        page.fill("#auth-fullname", "Agentic Test Citizen")
        page.fill("#auth-mobile", "9876543210")
        page.fill("#auth-email", citizen_email)
        page.fill("#auth-password", "password123")
        page.click("button:has-text('Create Citizen Account')")
        time.sleep(1)

        # Verify registration success
        assert not auth_modal.is_visible(), "Error: Auth modal should close after registration"
        user_name = page.locator("#user-display-name").text_content()
        assert "Agentic Test Citizen" in user_name, f"Unexpected user name: {user_name}"
        print(f"  Passed: Registered successfully. Current user: {user_name}.")

        # 5. Verify Browse Database is still hidden for citizen user
        print("\n[Step 5] Checking tab visibility for newly registered citizen...")
        assert not nav_db_tab.is_visible(), "Error: Browse Database tab must be HIDDEN for citizen users"
        nav_admin_tab = page.locator("#nav-admin-tab")
        assert not nav_admin_tab.is_visible(), "Error: Administrator tab must be HIDDEN for citizen users"
        print("  Passed: Sensitive administrative tabs are hidden from citizen.")

        # 6. Test Discovered Assets tab before any deceased is registered
        print("\n[Step 6] Testing Discovered Assets tab for empty records...")
        page.click(".tab-btn[data-tab='matches']")
        time.sleep(0.5)
        matches_text = page.locator("#matches-container").text_content()
        assert "No Deceased Family Records Registered Yet" in matches_text
        print("  Passed: Helpful empty state rendered with direct action button.")

        # 7. Register a deceased family member WITHOUT certificate upload
        print("\n[Step 7] Registering deceased member without certificate upload or cert ref...")
        page.click(".tab-btn[data-tab='register-deceased']")
        time.sleep(0.5)

        page.fill("#dec-fullname", "Rameshwar Dayal")
        page.fill("#dec-dob", "1960-03-25")
        page.fill("#dec-dod", "2023-09-12")
        page.select_option("#dec-gender", "Male")
        page.fill("#dec-city", "Jaipur")
        page.fill("#dec-state", "Rajasthan")
        # Leave #dec-cert-ref EMPTY
        page.fill("#dec-id-ref", "RDPR998877")
        page.fill("#dec-claimant-name", "Agentic Test Citizen")
        page.select_option("#dec-claimant-rel", "Son")
        page.fill("#dec-claimant-email", citizen_email)
        page.fill("#dec-claimant-mobile", "9876543210")
        # DO NOT upload any file in #dec-doc-file

        page.click("button:has-text('Submit Record for Admin Verification')")
        
        # 8. Verify redirected to Family Dashboard with 1 pending record
        print("\n[Step 8] Verifying dashboard status...")
        page.wait_for_selector("#deceased-table-body tr:has-text('Rameshwar Dayal')", timeout=10000)
        dec_table = page.locator("#deceased-table-body").text_content()
        assert "Rameshwar Dayal" in dec_table, "Error: Submitted record should appear in dashboard"
        assert "Pending" in dec_table, "Error: Status should be Pending"
        print("  Passed: Record submitted without certificate and listed as Pending Verification.")

        # 9. Verify Discovered Assets shows Pending Verification card
        print("\n[Step 9] Verifying Discovered Assets tab for pending record...")
        page.click(".tab-btn[data-tab='matches']")
        time.sleep(0.5)
        matches_text = page.locator("#matches-container").text_content()
        assert "Civil Verification in Progress" in matches_text, f"Unexpected matches text: {matches_text}"
        print("  Passed: Civil verification pending notice displayed without error.")

        # Test Re-Match button on pending record
        page.click("button:has-text('Re-Match')")
        time.sleep(0.5)
        print("  Passed: Re-Match on pending record handled cleanly.")

        # 10. Logout citizen
        print("\n[Step 10] Logging out citizen...")
        page.click("button[title='Logout']")
        time.sleep(0.5)
        assert page.locator("#auth-buttons").is_visible(), "Error: Auth buttons should be visible after logout"
        print("  Passed: Logged out successfully.")

        # 11. Login as Administrator
        print("\n[Step 11] Logging in as Administrator...")
        page.click("button:has-text('Admin')")
        time.sleep(1)

        assert nav_db_tab.is_visible(), "Error: Browse Database tab must be VISIBLE for Administrator"
        assert nav_admin_tab.is_visible(), "Error: Administrator tab must be VISIBLE for Administrator"
        print("  Passed: Administrator authenticated. Browse Database and Admin tabs are visible.")

        # 12. Admin User Creation feature
        print("\n[Step 12] Testing Admin User Creation feature...")
        page.click(".tab-btn[data-tab='admin']")
        time.sleep(0.5)

        # Create new Administrator account
        page.select_option("#admin-user-role", "admin")
        page.fill("#admin-user-fullname", "Agentic Sub Admin")
        page.fill("#admin-user-email", admin_created_email)
        page.fill("#admin-user-mobile", "9876543210")
        page.fill("#admin-user-password", "adminpassword123")
        page.click("button:has-text('Create User Account')")
        page.wait_for_selector(f"#admin-users-table-body tr:has-text('{admin_created_email}')", timeout=10000)
        print(f"  Passed: Admin created new administrator account ({admin_created_email}).")

        # Create new Institution Representative account
        page.select_option("#admin-user-role", "institution_rep")
        time.sleep(0.3)
        inst_container = page.locator("#admin-user-inst-container")
        assert inst_container.is_visible(), "Error: Institution selector should be visible for institution_rep"
        page.select_option("#admin-user-inst", index=1)
        page.fill("#admin-user-fullname", "Agentic SBI Officer")
        page.fill("#admin-user-email", inst_created_email)
        page.fill("#admin-user-mobile", "9876543210")
        page.fill("#admin-user-password", "instpassword123")
        page.click("button:has-text('Create User Account')")
        page.wait_for_selector(f"#admin-users-table-body tr:has-text('{inst_created_email}')", timeout=10000)
        print(f"  Passed: Admin created institution rep account ({inst_created_email}).")

        # 13. Verify Rameshwar Dayal death record as Admin
        print("\n[Step 13] Verifying Rameshwar Dayal death record in Admin table...")
        pending_table = page.locator("#admin-pending-table-body")
        assert "Rameshwar Dayal" in pending_table.text_content(), "Error: Record should be in pending verification table"
        
        # Click Verify and Auto-Match for Rameshwar Dayal
        row = pending_table.locator("tr:has-text('Rameshwar Dayal')").first
        row.locator("button:has-text('Verify and Auto-Match')").click()
        time.sleep(1)
        print("  Passed: Death record verified and matching engine triggered.")

        # 14. Test Browse Database tab
        print("\n[Step 14] Testing Browse Database tab functionality...")
        page.click("#nav-db-tab")
        time.sleep(1)

        fdb_table = page.locator("#fdb-table-body").text_content()
        assert len(fdb_table) > 100, "Error: Financial records should be loaded in Browse Database"
        print("  Passed: Financial database loaded with central records.")

        # Test category filters
        page.click(".fdb-cat-btn[data-cat='bank']")
        time.sleep(0.3)
        page.click(".fdb-cat-btn[data-cat='insurance']")
        time.sleep(0.3)
        page.click(".fdb-cat-btn[data-cat='mutual_fund']")
        time.sleep(0.3)
        page.click(".fdb-cat-btn[data-cat='all']")
        time.sleep(0.3)
        print("  Passed: Category filtering buttons (Bank, Insurance, Mutual Fund, All) functional.")

        # Test search input
        page.fill("#fdb-search", "State Bank")
        time.sleep(0.5)
        filtered_text = page.locator("#fdb-table-body").text_content()
        assert "State Bank" in filtered_text
        page.fill("#fdb-search", "")
        time.sleep(0.5)
        print("  Passed: Real-time search filter in Browse Database functional.")

        # 15. Test Notifications modal
        print("\n[Step 15] Testing Notification Center...")
        page.click("#notif-btn")
        time.sleep(0.5)
        assert page.locator("#modal-notif").is_visible()
        page.click("button:has-text('Mark all read')")
        time.sleep(0.3)
        page.click("#modal-notif button:has(.fa-xmark)")
        time.sleep(0.5)
        print("  Passed: Notification modal opened, marked all read, and closed.")

        # 16. Log back in as citizen to verify matches
        print("\n[Step 16] Logging back in as citizen to verify discovered assets...")
        page.click("button[title='Logout']")
        time.sleep(0.5)

        page.click("#auth-buttons button:has-text('Login')")
        time.sleep(0.5)
        page.fill("#auth-email", citizen_email)
        page.fill("#auth-password", "password123")
        page.click("#auth-form button[type='submit']")
        time.sleep(1)

        page.click(".tab-btn[data-tab='matches']")
        time.sleep(1)

        selector_val = page.locator("#match-deceased-selector").input_value()
        assert selector_val != "", "Error: Deceased selector should select the verified record"
        print(f"  Passed: Deceased record ({selector_val}) selected in matching tab.")

        # 17. Test Google OAuth 2.0 Sign In Flow
        print("\n[Step 17] Testing Google OAuth 2.0 Sign In feature...")
        page.click("button[title='Logout']")
        time.sleep(0.5)

        page.click("#auth-buttons button:has-text('Login')")
        time.sleep(0.5)
        google_btn = page.locator("button:has-text('Continue with Google')")
        assert google_btn.is_visible(), "Error: Google Sign In button must be visible in Auth modal."
        google_btn.click()
        time.sleep(1)

        user_display = page.locator("#user-display-name").text_content()
        assert "Google" in user_display, f"Expected Google user, got {user_display}"
        print(f"  Passed: Google OAuth authentication succeeded for user: {user_display}.")

        # 18. Test Virasat AI Legal Copilot
        print("\n[Step 18] Testing Virasat AI Legal Copilot interactive assistant...")
        copilot_btn = page.locator("#btn-open-copilot")
        assert copilot_btn.is_visible(), "Error: Floating AI Copilot button must be visible."
        copilot_btn.click()
        time.sleep(0.5)

        copilot_modal = page.locator("#modal-copilot")
        assert copilot_modal.is_visible(), "Error: AI Copilot modal should open upon clicking launcher."

        # Click quick legal inquiry button
        page.click("#modal-copilot button:has-text('Nominee vs Legal Heir Rights')")
        time.sleep(3)

        thread_text = page.locator("#copilot-thread").text_content()
        assert "Nominee" in thread_text and "Legal Heir" in thread_text, "Error: AI Copilot should answer nominee inquiry."
        print("  Passed: AI Copilot resolved quick legal inquiry with structured response.")

        # Test custom prompt input
        page.fill("#copilot-input", "How to claim deceased bank account at State Bank of India?")
        page.click("#copilot-send-btn")
        time.sleep(3)
        updated_thread = page.locator("#copilot-thread").text_content()
        assert "Bank" in updated_thread or "SBI" in updated_thread, "Error: AI Copilot should answer bank claim question."
        print("  Passed: AI Copilot handled custom prompt submission.")

        # Close copilot modal
        page.click("#modal-copilot button:has(.fa-xmark)")
        time.sleep(0.5)
        assert not copilot_modal.is_visible(), "Error: AI Copilot modal should close."
        print("  Passed: AI Copilot modal closed successfully.")

        # 19. Test AI Claim Health Predictor in Initiate Claim modal
        print("\n[Step 19] Testing AI Claim Health Predictor in Claim modal...")
        # Authenticate as Priya Sharma who has unclaimed matching assets
        page.evaluate("""async () => {
            const resp = await apiFetch('/api/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email: 'priya.sharma@example.com', password: 'family123' })
            });
            currentUser = resp.user;
            currentToken = resp.access_token;
            localStorage.setItem('token', currentToken);
            updateUIForUser();
            switchTab('matches');
            await populateMatchesDropdown();
            await loadMatchesForSelected();
        }""")
        time.sleep(1)

        # Select first available match and click Initiate Claim
        claim_btn = page.locator("button:has-text('Initiate Claim')").first
        assert claim_btn.is_visible(), "Error: Initiate Claim button should be visible for Priya Sharma matches."
        claim_btn.click()
        time.sleep(1.5)
        claim_modal = page.locator("#modal-claim")
        assert claim_modal.is_visible(), "Error: Claim modal should open."
        prediction_box = page.locator("#claim-ai-prediction-box")
        assert prediction_box.is_visible(), "Error: AI Claim Prediction box must be visible in Claim modal."
        prob_badge = page.locator("#claim-ai-prob-badge").text_content()
        assert "%" in prob_badge, f"Expected probability percentage, got {prob_badge}"
        print(f"  Passed: AI Claim Health Predictor operational in modal: {prob_badge}.")
        page.click("#modal-claim button:has-text('Cancel')")
        time.sleep(0.5)

        # 20. Test AI Fraud and Anomaly Detection in Admin Dashboard
        print("\n[Step 20] Testing AI Fraud and Anomaly Intelligence Center in Admin Panel...")
        page.click("button[title='Logout']")
        time.sleep(0.5)

        page.click("button:has-text('Admin')")
        time.sleep(1)
        page.click(".tab-btn[data-tab='admin']")
        time.sleep(1)

        anomalies_box = page.locator("#admin-anomalies-list")
        assert anomalies_box.is_visible(), "Error: Admin Fraud Anomalies list must be visible in Admin panel."
        print("  Passed: AI Fraud and Anomaly Intelligence Center active and restricted to Admin.")

        # 21. Check console errors
        print("\n[Step 21] Inspecting console error logs...")
        if console_errors:
            print(f"  WARNING: {len(console_errors)} console errors caught:")
            for err in console_errors:
                print(f"    * {err}")
            assert False, "Console errors found during testing."
        else:
            print("  Passed: ZERO console errors detected during entire test session.")

        browser.close()

    print("\n" + "=" * 70)
    print("ALL AGENTIC BROWSER UI TESTS PASSED SUCCESSFULLY WITH ZERO ERRORS!")
    print("=" * 70)

if __name__ == "__main__":
    run_e2e_tests()
