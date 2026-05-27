#!/usr/bin/env python3
"""
Fast Token Updater - No App Secret Needed
==========================================
This script generates a URL for you to open in your browser.
After authorization, it asks you to paste the token back here.

Usage: python3 get_token.py
"""

import os, sys, requests, json

PAGE_ID = "1105214619347449"
APP_ID  = "4369627469965832"

SCOPES = ",".join([
    "pages_show_list",
    "pages_read_engagement",
    "pages_manage_posts",
    "pages_manage_metadata",
    "pages_messaging",
    "publish_video",
    "business_management",
])

def save_token_to_env(token, path=".env"):
    lines = open(path).readlines() if os.path.exists(path) else []
    out, done = [], False
    for line in lines:
        if line.startswith("FB_ACCESS_TOKEN="):
            out.append(f"FB_ACCESS_TOKEN={token}\n")
            done = True
        elif line.startswith("FB_PAGE_ID="):
            out.append(f"FB_PAGE_ID={PAGE_ID}\n")
        else:
            out.append(line)
    if not done:
        out.append(f"FB_ACCESS_TOKEN={token}\n")
    open(path, "w").writelines(out)
    print("✅ .env updated with new token!")

def main():
    print("=" * 65)
    print("  Facebook Token Setup — Step by Step")
    print("=" * 65)
    print()
    print("STEP 1: Open this URL in your browser:")
    print()
    print(f"  https://www.facebook.com/dialog/oauth?client_id={APP_ID}&redirect_uri=https://developers.facebook.com/tools/explorer/&scope={SCOPES}&response_type=token")
    print()
    print("STEP 2: Click 'Continue as [your name]', then 'Allow'.")
    print()
    print("STEP 3: After you allow, you'll be redirected to developers.facebook.com.")
    print("        Copy the 'access_token' value from the URL bar.")
    print("        (It starts with EAAZ... and is very long)")
    print()

    user_token = input("Paste your User Token here: ").strip().strip("'\"")
    if not user_token or len(user_token) < 20:
        sys.exit("❌ Invalid token.")

    # Verify the token
    print("\nVerifying token...")
    r = requests.get(f"https://graph.facebook.com/me?access_token={user_token}")
    me = r.json()
    if "error" in me:
        sys.exit(f"❌ Token invalid: {me['error']['message']}")
    print(f"✅ Verified! Logged in as: {me.get('name')} (ID: {me.get('id')})")

    # Get the page access token
    print(f"\nFetching Page Access Token for page {PAGE_ID}...")
    r2 = requests.get(f"https://graph.facebook.com/me/accounts?access_token={user_token}")
    pages = r2.json().get("data", [])
    if not pages:
        print("⚠️  No pages found for this token.")
        print("   Make sure you authorized with the correct Facebook account.")
        sys.exit(1)

    page_token = None
    page_name  = None
    print("\nPages accessible with this token:")
    for p in pages:
        print(f"  • {p['name']} (ID: {p['id']})")
        if p["id"] == PAGE_ID:
            page_token = p["access_token"]
            page_name  = p["name"]

    if not page_token:
        print(f"\n⚠️  Page {PAGE_ID} ('Dark' Den') not found in the list above.")
        print("   Make sure you're logged in as the page admin.")
        sys.exit(1)

    print(f"\n✅ Got Page Token for '{page_name}'!")

    # Verify video permissions
    print("\nVerifying video posting permission...")
    with open("/tmp/test_bridge.jpg", "rb") as f:
        r3 = requests.post(
            f"https://graph.facebook.com/{PAGE_ID}/photos",
            data={"caption": "Bridge token test ✅", "access_token": page_token},
            files={"source": f}
        )
    d3 = r3.json()
    if "error" in d3:
        err_msg = d3["error"]["message"]
        if "pages_manage_posts" in err_msg:
            print(f"❌ Still missing pages_manage_posts!")
            print()
            print("  This happens when the App hasn't been granted this permission.")
            print("  FIX: In Facebook Developer Console:")
            print("    1. Go to: https://developers.facebook.com/apps/4369627469965832/")
            print("    2. Click 'App Review' → 'Permissions and Features'")
            print("    3. Find 'pages_manage_posts' and click 'Request Advanced Access'")
            print("    4. Once approved, run this script again.")
            print()
            print("  ALTERNATIVE: Use Graph API Explorer with this app:")
            print("    https://developers.facebook.com/tools/explorer/4369627469965832/")
            print("    Select permissions, generate token, paste it above.")
        else:
            print(f"⚠️  Post test error: {err_msg}")
    else:
        print(f"✅ Test post successful! Post ID: {d3.get('id')}")
        # Clean up test post
        post_id = d3.get("id")
        if post_id:
            requests.delete(f"https://graph.facebook.com/{post_id}?access_token={page_token}")

    # Save token regardless (in case video works but photo doesn't)
    save_token_to_env(page_token)

    print("\n" + "=" * 65)
    print("  Token saved to .env")
    print(f"  Page: {page_name} (ID: {PAGE_ID})")
    print("\n  Now run: python3 run_local.py")
    print("=" * 65)

if __name__ == "__main__":
    main()
