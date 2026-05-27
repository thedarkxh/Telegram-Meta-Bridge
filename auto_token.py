"""
Fully automated Facebook token retrieval using headless Playwright.
Logs into Facebook, navigates to Graph API Explorer, captures token.

Usage: FB_EMAIL=email FB_PASSWORD=pass python3 auto_token.py
  OR:  python3 auto_token.py  (will prompt for credentials)
"""
import os, sys, time, re, json, urllib.parse, requests, getpass

PAGE_ID   = "1105214619347449"
APP_ID    = "4369627469965832"
SCOPES    = [
    "pages_show_list",
    "pages_read_engagement",
    "pages_manage_posts",
    "pages_manage_metadata",
    "publish_video",
    "business_management",
    "pages_messaging",
]

def save_to_env(token, path=".env"):
    lines = open(path).readlines() if os.path.exists(path) else []
    out, done = [], False
    for line in lines:
        if line.startswith("FB_ACCESS_TOKEN="):
            out.append(f"FB_ACCESS_TOKEN={token}\n"); done = True
        elif line.startswith("FB_PAGE_ID="):
            out.append(f"FB_PAGE_ID={PAGE_ID}\n")
        else:
            out.append(line)
    if not done:
        out.append(f"FB_ACCESS_TOKEN={token}\n")
    open(path, "w").writelines(out)
    print("✅ Token saved to .env")

def get_page_token(user_token):
    try:
        r = requests.get("https://graph.facebook.com/me/accounts",
                         params={"access_token": user_token}, timeout=10)
        for p in r.json().get("data", []):
            if p["id"] == PAGE_ID:
                return p["access_token"], p["name"]
    except Exception as e:
        print(f"  Page token lookup failed: {e}")
    return user_token, "profile"

def extract_token_from_url(url):
    if "access_token=" not in url:
        return None
    frag   = urllib.parse.urlparse(url).fragment
    qs     = urllib.parse.parse_qs(frag)
    token  = qs.get("access_token", [None])[0]
    if not token:
        # Try query string
        qs2   = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        token = qs2.get("access_token", [None])[0]
    return token

def main():
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

    fb_email    = os.getenv("FB_EMAIL", "").strip()
    fb_password = os.getenv("FB_PASSWORD", "").strip()
    if not fb_email:
        fb_email = input("Facebook email/phone: ").strip()
    if not fb_password:
        fb_password = getpass.getpass("Facebook password: ")
    if not fb_email or not fb_password:
        sys.exit("❌ Email and password required.")

    auth_url = (
        f"https://www.facebook.com/dialog/oauth"
        f"?client_id={APP_ID}"
        f"&redirect_uri={urllib.parse.quote('https://developers.facebook.com/tools/explorer/')}"
        f"&scope={urllib.parse.quote(','.join(SCOPES))}"
        f"&response_type=token"
        f"&display=popup"
    )

    captured = [None]

    with sync_playwright() as pw:
        print("🌐 Launching headless Firefox...")
        browser = pw.firefox.launch(
            headless=True,
            args=["--no-sandbox"]
        )
        ctx  = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
            locale="en-US",
        )
        page = ctx.new_page()

        try:
            # ── Login ────────────────────────────────────────────────────
            print("🔑 Step 1/4: Logging in to Facebook...")
            page.goto("https://www.facebook.com/login", timeout=30000,
                      wait_until="domcontentloaded")
            time.sleep(2)

            # Handle cookie popups
            for sel in [
                "button:has-text('Allow all cookies')",
                "button:has-text('Accept All')",
                "[data-cookiebanner='accept_button']",
                "[data-testid='cookie-policy-manage-dialog-accept-button']",
            ]:
                try:
                    btn = page.locator(sel).first
                    if btn.is_visible(timeout=1500):
                        btn.click(); time.sleep(1); break
                except Exception: pass

            # Fill credentials
            try:
                page.fill("#email", fb_email, timeout=10000)
                page.fill("#pass",  fb_password)
                page.press("#pass", "Enter")
            except PWTimeout:
                page.fill('[name="email"]', fb_email)
                page.fill('[name="pass"]',  fb_password)
                page.press('[name="pass"]', "Enter")

            # Wait for login
            time.sleep(5)
            url_after = page.url
            print(f"  URL after login: {url_after[:70]}")

            if "login" in url_after and "checkpoint" not in url_after and "two_step" not in url_after:
                print("⚠️  Still on login page — may need 2FA or wrong credentials")
                # Take screenshot for debugging
                page.screenshot(path="/tmp/fb_login_debug.png")
                print("  Screenshot saved to /tmp/fb_login_debug.png")
            else:
                print("✅ Login appears successful!")

            # ── OAuth dialog ─────────────────────────────────────────────
            print("🔑 Step 2/4: Opening OAuth permission dialog...")
            page.goto(auth_url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(4)

            current_url = page.url
            print(f"  OAuth URL: {current_url[:80]}")

            # Check if token already in URL (already authorized before)
            tok = extract_token_from_url(current_url)
            if tok:
                captured[0] = tok
                print("✅ Token already in URL (previously authorized)!")
            else:
                # Click authorization buttons
                for attempt in range(5):
                    for sel in [
                        "button:has-text('Continue as')",
                        "button:has-text('Continue')",
                        "button:has-text('Allow')",
                        "button:has-text('OK')",
                        "button:has-text('Save')",
                        "[data-testid='btn-confirm-login-btn']",
                        "div[role='button']:has-text('Continue')",
                        "div[role='button']:has-text('Allow')",
                        "span:has-text('Continue')",
                    ]:
                        try:
                            btn = page.locator(sel).first
                            if btn.is_visible(timeout=1000):
                                print(f"  Clicking: {sel}")
                                btn.click()
                                time.sleep(3)
                                url_now = page.url
                                tok = extract_token_from_url(url_now)
                                if tok:
                                    captured[0] = tok
                                    break
                        except Exception: pass
                    if captured[0]:
                        break
                    time.sleep(2)

            # ── Also try directly fetching a token from settings ──────────
            if not captured[0]:
                print("🔑 Step 3/4: Trying developer token endpoint...")
                # Try to fetch token via Graph API directly
                # Log into developers.facebook.com
                page.goto("https://developers.facebook.com/tools/explorer/", timeout=30000,
                          wait_until="domcontentloaded")
                time.sleep(5)
                content = page.content()

                # Look for token in page source
                m = re.search(r'"accessToken"\s*:\s*"(EAA[A-Za-z0-9]+)"', content)
                if m:
                    captured[0] = m.group(1)
                    print(f"✅ Found token in page source!")
                else:
                    # Try evaluating JS to get token from the explorer
                    try:
                        result = page.evaluate("""
                            () => {
                                // Try to find access token in page state
                                const inputs = document.querySelectorAll('input');
                                for (const input of inputs) {
                                    if (input.value && input.value.startsWith('EAA') && input.value.length > 50) {
                                        return input.value;
                                    }
                                }
                                // Try localStorage
                                const keys = Object.keys(localStorage);
                                for (const k of keys) {
                                    const v = localStorage.getItem(k);
                                    if (v && v.includes('EAA')) {
                                        const m = v.match(/EAA[A-Za-z0-9]{50,}/);
                                        if (m) return m[0];
                                    }
                                }
                                return null;
                            }
                        """)
                        if result:
                            captured[0] = result
                            print(f"✅ Got token from JS!")
                    except Exception as e:
                        print(f"  JS eval failed: {e}")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback; traceback.print_exc()
            page.screenshot(path="/tmp/fb_error_debug.png")
            print("  Screenshot: /tmp/fb_error_debug.png")
        finally:
            browser.close()

    token = captured[0]
    if not token:
        print("\n❌ Automated token capture failed.")
        print("\n📋 Please do this manually (2 minutes):")
        print(f"\n   1. Open: {auth_url}")
        print("   2. Click Allow/Continue")
        print("   3. Copy the access_token from the redirect URL")
        print("   4. Run: python3 get_token.py\n")
        sys.exit(1)

    print(f"\n✅ Got token ({len(token)} chars)")

    # Get page-specific token
    r_me = requests.get(f"https://graph.facebook.com/me?access_token={token}", timeout=10)
    if "error" not in r_me.json():
        print(f"  User: {r_me.json().get('name')}")
        page_token, page_name = get_page_token(token)
    else:
        page_token = token
        page_name  = "unknown"

    # Test video upload
    print("\n🧪 Testing Facebook video upload...")
    with open("/tmp/test_video.mp4", "rb") as f:
        r_v = requests.post(
            f"https://graph.facebook.com/{PAGE_ID}/videos",
            data={"description": "Bridge connectivity test ✅", "access_token": page_token},
            files={"source": f},
            timeout=90
        )
    dv = r_v.json()
    if "error" in dv:
        print(f"⚠️  Video test: {dv['error']['message']}")
    else:
        print(f"🎉 VIDEO UPLOAD SUCCESS! Post ID: {dv.get('id')}")
        if dv.get("id"):
            requests.delete(f"https://graph.facebook.com/{dv['id']}?access_token={page_token}")

    save_to_env(page_token)
    print(f"\n✅ Done! Token for '{page_name}' saved.")
    print("   Run: python3 run_local.py")

if __name__ == "__main__":
    main()
