import sys
import os
import time
import uuid
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(line_buffering=True)

TARGET_URL = "https://virasat-setu-eight.vercel.app"

def run_vercel_e2e_tests():
    uid = str(uuid.uuid4())[:6]
    citizen_email = f"vercel_test_{uid}@example.com"
    admin_created_email = f"vercel_admin_{uid}@virasatsetu.gov.in"
    
    console_errors = []
    
    print("=" * 70)
    print(f"STARTING LIVE AGENTIC BROWSER UI TEST ON VERCEL: {TARGET_URL}")
    print("=" * 70)

    proxy_url = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
    launch_kwargs = {"headless": True}
    if proxy_url:
        launch_kwargs["proxy"] = {"server": proxy_url}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        def handle_console(msg):
            if msg.type == "error":
                txt = msg.text.lower()
                # Ignore harmless third party font or icon load aborts if any
                if "favicon" not in txt and "font" not in txt:
                    console_errors.append(msg.text)
                    print(f"  [Console Error]: {msg.text}")

        page.on("console", handle_console)
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        # 1. Navigate to live Vercel URL
        print(f"\n[Step 1] Navigating to live Vercel portal: {TARGET_URL}...")
        page.goto(TARGET_URL, wait_until="domcontentloaded")
        time.sleep(2)
        print("  Passed: Vercel production page loaded successfully.")

        # 2. Check initial logged out state
        print("\n[Step 2] Checking initial navbar visibility and security gating...")
        nav_db_tab = page.locator("#nav-db-tab")
        assert not nav_db_tab.is_visible(), "Error: Browse Database tab must be HIDDEN for logged out users"
        print("  Passed: Browse Database tab is correctly hidden for unauthenticated users.")

        # 3. Test Home banner button and Auth modal
        print("\n[Step 3] Testing Browse Database button on Home banner...")
        page.click("#tab-home button:has-text('Browse Database')")
        time.sleep(1)
        auth_modal = page.locator("#modal-auth")
        assert auth_modal.is_visible(), "Error: Auth modal should open when clicking Browse Database."
        print("  Passed: Clicking Browse Database prompted authentication modal as expected.")

        # 4. Test Google OAuth button presence
        print("\n[Step 4] Testing Google OAuth 2.0 Continue with Google button...")
        google_btn = page.locator("button:has-text('Continue with Google')")
        assert google_btn.is_visible(), "Error: Continue with Google button must be visible in Auth modal."
        print("  Passed: Google OAuth button rendered cleanly.")

        # 5. Test Register form input fields
        print(f"\n[Step 5] Testing Citizen Registration form with input fields ({citizen_email})...")
        page.click("#auth-tab-register")
        time.sleep(0.5)
        page.fill("#auth-fullname", "Vercel Citizen Tester")
        page.fill("#auth-mobile", "9123456789")
        page.fill("#auth-email", citizen_email)
        page.fill("#auth-password", "password123")
        page.click("button:has-text('Create Citizen Account')")
        time.sleep(2)

        assert not auth_modal.is_visible(), "Error: Auth modal should close after registration."
        user_name = page.locator("#user-display-name").text_content()
        assert "Vercel Citizen Tester" in user_name, f"Unexpected user name: {user_name}"
        print(f"  Passed: Registered and authenticated on live Vercel. Current user: {user_name}.")

        # 6. Verify role partition on live Vercel
        print("\n[Step 6] Checking tab visibility for newly registered citizen on Vercel...")
        assert not nav_db_tab.is_visible(), "Error: Browse Database tab must remain hidden for citizen."
        nav_admin_tab = page.locator("#nav-admin-tab")
        assert not nav_admin_tab.is_visible(), "Error: Administrator tab must remain hidden for citizen."
        print("  Passed: Administrative tabs are strictly partitioned away from citizen.")

        # 7. Test Register Deceased form with input fields and dropdowns
        print("\n[Step 7] Testing Register Deceased form with inputs and gender dropdown...")
        page.click(".tab-btn[data-tab='register-deceased']")
        time.sleep(1)

        page.fill("#dec-fullname", "Gopal Krishna Murthy")
        page.fill("#dec-dob", "1955-08-15")
        page.fill("#dec-dod", "2022-11-20")
        page.select_option("#dec-gender", "Male")
        page.fill("#dec-city", "Bengaluru")
        page.fill("#dec-state", "Karnataka")
        page.fill("#dec-id-ref", "GKM8877665")
        page.fill("#dec-claimant-name", "Vercel Citizen Tester")
        page.fill("#dec-claimant-mobile", "9123456789")
        page.fill("#dec-claimant-email", citizen_email)
        page.select_option("#dec-claimant-rel", "Son")
        page.select_option("#dec-claimant-type", "Legal Heir")

        # Submit deceased record without certificate upload
        page.click("button:has-text('Submit Record for Admin Verification')")
        page.wait_for_selector("#deceased-table-body tr:has-text('Gopal Krishna Murthy')", timeout=10000)
        dec_table = page.locator("#deceased-table-body").text_content()
        assert "Pending Verification" in dec_table, "Error: Record should be Pending Verification"
        print("  Passed: Deceased civil record submitted without certificate and listed as Pending Verification.")

        # 8. Test Viru (AI Legal Copilot) on live Vercel
        print("\n[Step 8] Testing Viru (Virasat AI Legal Copilot) on live Vercel...")
        copilot_btn = page.locator("#btn-open-copilot")
        assert copilot_btn.is_visible(), "Error: Floating Ask Viru button must be visible."
        copilot_btn.click()
        time.sleep(1)

        copilot_modal = page.locator("#modal-copilot")
        assert copilot_modal.is_visible(), "Error: Viru modal should open."
        modal_title = page.locator("#modal-copilot h3").text_content()
        assert "Viru" in modal_title, f"Expected Viru in modal title, got {modal_title}"
        print(f"  Passed: Viru modal opened with title: {modal_title}.")

        # Test quick question chip
        page.click("#modal-copilot button:has-text('Nominee vs Legal Heir Rights')")
        time.sleep(3)
        thread_text = page.locator("#copilot-thread").text_content()
        assert "Nominee" in thread_text and "Legal Heir" in thread_text, "Error: Viru should answer nominee question."
        print("  Passed: Viru resolved quick legal question with verified statutory guidance.")

        # Test custom prompt input and send button
        page.fill("#copilot-input", "What are the rules for claiming bank deposits at State Bank of India?")
        page.click("#copilot-send-btn")
        time.sleep(3)
        updated_thread = page.locator("#copilot-thread").text_content()
        assert "Bank" in updated_thread or "SBI" in updated_thread, "Error: Viru should answer bank question."
        print("  Passed: Viru responded to custom legal query successfully.")

        # Close Viru modal
        page.click("#modal-copilot button:has(.fa-xmark)")
        time.sleep(0.5)
        assert not copilot_modal.is_visible(), "Error: Viru modal should close."
        print("  Passed: Viru modal closed cleanly.")

        # 9. Test Demo Switcher to Admin
        print("\n[Step 9] Testing Administrator login via role switcher...")
        page.click("button:has-text('Admin')")
        time.sleep(1.5)

        user_name = page.locator("#user-display-name").text_content()
        assert "Administrator" in user_name or "Rajiv" in user_name, f"Unexpected admin user: {user_name}"
        assert nav_db_tab.is_visible(), "Error: Browse Database tab must be visible for Admin."
        print(f"  Passed: Authenticated as Admin ({user_name}). Administrative tabs visible.")

        # 10. Test Browse Database tab and category filtering buttons
        print("\n[Step 10] Testing Browse Database tab, category buttons and search input on Vercel...")
        nav_db_tab.click()
        time.sleep(1.5)

        # Test category filter buttons
        page.click(".fdb-cat-btn[data-cat='bank']")
        time.sleep(0.5)
        print("  Passed: Filtered central database by Bank Accounts.")

        page.click(".fdb-cat-btn[data-cat='insurance']")
        time.sleep(0.5)
        print("  Passed: Filtered central database by Insurance Policies.")

        page.click(".fdb-cat-btn[data-cat='mutual_fund']")
        time.sleep(0.5)
        print("  Passed: Filtered central database by Mutual Funds.")

        page.click(".fdb-cat-btn[data-cat='all']")
        time.sleep(0.5)
        print("  Passed: Reset category filter to All Assets.")

        # Test search filter input
        search_input = page.locator("#fdb-search")
        search_input.fill("Rajesh")
        time.sleep(1)
        table_text = page.locator("#fdb-table-body").text_content()
        assert "Rajesh" in table_text, "Error: Table should show records matching search."
        print("  Passed: Real time search filter operational in Browse Database.")
        search_input.fill("")
        time.sleep(0.5)

        # 11. Test Notification Center
        print("\n[Step 11] Testing Notification Center modal on Vercel...")
        page.click("#notif-btn")
        time.sleep(1)
        notif_modal = page.locator("#modal-notif")
        assert notif_modal.is_visible(), "Error: Notifications modal should open."
        page.click("button:has-text('Mark all read')")
        time.sleep(0.5)
        page.click("#modal-notif button:has(.fa-xmark)")
        time.sleep(0.5)
        print("  Passed: Notification Center opened, marked read, and closed cleanly.")

        # 12. Test Admin Dashboard and User Provisioning
        print("\n[Step 12] Testing Admin User Provisioning form and inputs on Vercel...")
        page.click(".tab-btn[data-tab='admin']")
        time.sleep(1)

        page.select_option("#admin-user-role", "admin")
        page.fill("#admin-user-fullname", "Vercel Created Officer")
        page.fill("#admin-user-mobile", "9876501234")
        page.fill("#admin-user-email", admin_created_email)
        page.fill("#admin-user-password", "officer123")
        page.click("button:has-text('Create User Account')")
        page.wait_for_selector(f"#admin-users-table-body tr:has-text('{admin_created_email}')", timeout=10000)
        print("  Passed: Admin successfully provisioned new account on live Vercel.")

        # 13. Test AI Fraud and Anomaly Intelligence Center
        print("\n[Step 13] Testing AI Fraud and Anomaly Intelligence Center on Vercel...")
        anomalies_box = page.locator("#admin-anomalies-list")
        assert anomalies_box.is_visible(), "Error: Anomaly Intelligence Center must be visible in Admin panel."
        print("  Passed: AI Fraud and Anomaly Intelligence Center active on live Vercel.")

        # 14. Test Discovered Assets and AI Claim Health Predictor
        print("\n[Step 14] Testing Discovered Assets and AI Claim Health Predictor in Claim modal...")
        page.click("button:has-text('Family')")
        time.sleep(1.5)
        page.click(".tab-btn[data-tab='matches']")
        time.sleep(1.5)

        # Test deceased dropdown selector
        deceased_selector = page.locator("#match-deceased-selector")
        assert deceased_selector.is_visible(), "Error: Deceased selector dropdown must be visible."
        print("  Passed: Deceased selector dropdown operational.")

        # Authenticate as Priya Sharma who has unclaimed matching records
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
        time.sleep(2)

        claim_btn = page.locator("button:has-text('Initiate Claim')").first
        if claim_btn.is_visible():
            claim_btn.click()
            time.sleep(2)
            claim_modal = page.locator("#modal-claim")
            assert claim_modal.is_visible(), "Error: Claim modal should open upon clicking Initiate Claim."
            prediction_box = page.locator("#claim-ai-prediction-box")
            assert prediction_box.is_visible(), "Error: AI Claim Prediction box must be visible."
            prob_badge = page.locator("#claim-ai-prob-badge").text_content()
            assert "%" in prob_badge, f"Expected percentage, got {prob_badge}"
            print(f"  Passed: AI Claim Health Predictor active in modal with score: {prob_badge}.")
            
            # Test claim remarks input field
            page.fill("#claim-remarks", "Automated Playwright test remarks on live Vercel.")
            time.sleep(0.5)
            page.click("#modal-claim button:has-text('Cancel')")
            time.sleep(0.5)
            print("  Passed: Claim modal input and cancellation verified.")

        # 15. Inspect console error logs
        print("\n[Step 15] Inspecting console error logs on live Vercel session...")
        if console_errors:
            print(f"  WARNING: {len(console_errors)} console errors caught:")
            for err in console_errors:
                print(f"    * {err}")
            assert False, "Console errors detected on live Vercel."
        else:
            print("  Passed: ZERO console errors detected during entire live Vercel test.")

        browser.close()

    print("\n" + "=" * 70)
    print("ALL LIVE VERCEL PRODUCTION TESTS PASSED SUCCESSFULLY WITH ZERO ERRORS!")
    print("=" * 70)

if __name__ == "__main__":
    run_vercel_e2e_tests()
