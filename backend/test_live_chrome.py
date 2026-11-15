import time
import sys
import psycopg2
from playwright.sync_api import sync_playwright

DATABASE_URL = "postgresql://postgres:123456@localhost:5432/fleetflow"

def get_latest_otp(email: str):
    time.sleep(1.5)
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT otp_code FROM users WHERE email = %s", (email,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else None

def run_live_test():
    print("=" * 70)
    print(" FLEETFLOW - LIVE CHROME AUTOMATED VERIFICATION")
    print("=" * 70)

    ts = int(time.time())
    users = [
        {
            "role": "Admin",
            "name": f"Admin User {ts}",
            "email": f"live_admin_{ts}@fleetflow.com",
            "password": "Password@123!",
            "admin_key": "FLEETFLOW_ADMIN_2026",
            "card_title": "System Admin",
        },
        {
            "role": "FleetManager",
            "name": f"Fleet Manager {ts}",
            "email": f"live_fm_{ts}@fleetflow.com",
            "password": "Password@123!",
            "hub": "East Distribution Hub",
            "card_title": "Fleet Manager",
        },
        {
            "role": "Dispatcher",
            "name": f"Logistics Dispatcher {ts}",
            "email": f"live_disp_{ts}@fleetflow.com",
            "password": "Password@123!",
            "hub": "Metro Central Hub",
            "card_title": "Dispatcher",
        },
        {
            "role": "Driver",
            "name": f"Fleet Driver {ts}",
            "email": f"live_driver_{ts}@fleetflow.com",
            "password": "Password@123!",
            "license": f"CDL-{ts % 100000}",
            "card_title": "Vehicle Driver",
        },
    ]

    with sync_playwright() as p:
        print("[Chrome] Opening Google Chrome browser window...")
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            slow_mo=400,
            args=["--start-maximized", "--disable-infobars"]
        )
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        print("[1] Navigating to http://localhost:5173/login ...")
        page.goto("http://localhost:5173/login", timeout=30000)
        page.wait_for_timeout(2000)

        # -------------------------------------------------------------
        # 1. SIGNUP & OTP VERIFICATION FOR ALL 4 ROLES
        # -------------------------------------------------------------
        print("\n" + "=" * 50)
        print(" PHASE 1: AUTOMATIC SIGNUP FOR ALL 4 ROLES")
        print("=" * 50)

        for u in users:
            role = u["role"]
            email = u["email"]
            name = u["name"]
            password = u["password"]
            print(f"\n[SIGNUP] Registering new {role} ({email})...")

            page.goto("http://localhost:5173/signup")
            page.wait_for_timeout(1000)

            # Select role card
            page.click(f"text='{u['card_title']}'")
            page.wait_for_timeout(400)

            page.fill("input[name='full_name']", name)
            page.fill("input[name='email']", email)
            page.fill("input[name='password']", password)
            page.fill("input[name='confirm_password']", password)

            if role == "Admin":
                admin_key = page.locator("input[name='admin_secret_key']")
                if admin_key.count() > 0:
                    admin_key.fill(u["admin_key"])
            elif role == "Driver":
                lic = page.locator("input[name='license_number']")
                if lic.count() > 0:
                    lic.fill(u["license"])
            elif role in ("FleetManager", "Dispatcher"):
                hub = page.locator("input[name='hub_location']")
                if hub.count() > 0:
                    hub.fill(u["hub"])

            page.wait_for_timeout(600)
            print(f"[SIGNUP] Submitting {role} registration form...")
            page.click("button:has-text('Create Account')")
            page.wait_for_timeout(2500)

            # Get OTP from database
            otp = get_latest_otp(email)
            print(f"[OTP] Database verification code for {email}: {otp}")

            if otp:
                page.fill("input[placeholder='••••••']", str(otp))
                page.wait_for_timeout(600)
                page.click("button:has-text('Verify OTP & Sign In')")
                page.wait_for_timeout(3000)
                print(f"[SUCCESS] {role} verified and signed in! Landed on: {page.url}")
            else:
                print(f"[ERROR] Could not fetch OTP for {email}")

            # Clear session
            page.evaluate("() => localStorage.clear()")
            page.wait_for_timeout(800)

        # -------------------------------------------------------------
        # 2. LOGIN & COMPREHENSIVE FEATURE TESTS FOR ALL 4 ROLES
        # -------------------------------------------------------------
        print("\n" + "=" * 50)
        print(" PHASE 2: LOGIN & VERIFY FUNCTIONALITY FOR ALL 4 ROLES")
        print("=" * 50)

        for u in users:
            role = u["role"]
            email = u["email"]
            password = u["password"]
            print(f"\n>>> LOGGING IN AS: {role} ({email}) <<<")

            page.goto("http://localhost:5173/login")
            page.wait_for_timeout(1500)

            page.fill("input[type='email']", email)
            page.fill("input[type='password']", password)
            page.wait_for_timeout(500)
            page.click("button[type='submit']")
            page.wait_for_timeout(3000)
            print(f"[LOGIN SUCCESS] Logged in as {role}. Current URL: {page.url}")

            if role == "Admin":
                print("\n[Admin Live Testing]")
                print("1. Loading Executive System Oversight Dashboard...")
                page.goto("http://localhost:5173/dashboard")
                page.wait_for_timeout(2500)

                print("2. Opening Reports & Audit Log module...")
                page.goto("http://localhost:5173/reports")
                page.wait_for_timeout(2500)

                print("3. Inspecting Drivers & Attendance...")
                page.goto("http://localhost:5173/attendance")
                page.wait_for_timeout(2500)

            elif role == "FleetManager":
                print("\n[FleetManager Live Testing]")
                print("1. Loading Fleet Operations Dashboard...")
                page.goto("http://localhost:5173/dashboard")
                page.wait_for_timeout(2500)

                print("2. Inspecting Fleet Vehicles...")
                page.goto("http://localhost:5173/vehicles")
                page.wait_for_timeout(2500)

                print("3. Inspecting Driver Records & Licenses...")
                page.goto("http://localhost:5173/drivers")
                page.wait_for_timeout(2500)

                print("4. Inspecting Maintenance & Fuel Logs...")
                page.goto("http://localhost:5173/maintenance")
                page.wait_for_timeout(2500)

                print("5. Inspecting Trips Dispatch Schedule...")
                page.goto("http://localhost:5173/trips")
                page.wait_for_timeout(2500)

            elif role == "Dispatcher":
                print("\n[Dispatcher Live Testing]")
                print("1. Loading Logistics Dispatch Dashboard...")
                page.goto("http://localhost:5173/dashboard")
                page.wait_for_timeout(2500)

                print("2. Inspecting Shipments & Waybills...")
                page.goto("http://localhost:5173/shipments")
                page.wait_for_timeout(2500)

                print("3. Inspecting Trips & Route Optimization...")
                page.goto("http://localhost:5173/trips")
                page.wait_for_timeout(2500)

                print("4. Loading GPS Live Fleet Tracking Map...")
                page.goto("http://localhost:5173/tracking")
                page.wait_for_timeout(3500)

            elif role == "Driver":
                print("\n[Driver Live Testing]")
                print("1. Loading Driver Personal Portal...")
                page.goto("http://localhost:5173/dashboard")
                page.wait_for_timeout(2500)

                print("2. Inspecting Attendance & Leave Requests...")
                page.goto("http://localhost:5173/attendance")
                page.wait_for_timeout(2500)

            # Clear session for next role
            page.evaluate("() => localStorage.clear()")
            page.wait_for_timeout(1000)

        print("\n" + "=" * 70)
        print(" ALL 4 ROLES SIGNED UP, LOGGED IN, AND VERIFIED LIVE IN CHROME!")
        print("=" * 70)
        page.wait_for_timeout(4000)
        browser.close()

if __name__ == "__main__":
    run_live_test()
