import sqlite3, shutil, os, re, requests, time
from playwright.sync_api import sync_playwright

def extract_cookies():
    profile = os.path.expanduser('~/.mozilla/firefox/h46d03bx.default-esr')
    db = f'{profile}/cookies.sqlite'
    shutil.copy(db, '/tmp/fb_cookies_full.sqlite')
    try: shutil.copy(db + '-wal', '/tmp/fb_cookies_full.sqlite-wal')
    except: pass
    
    conn = sqlite3.connect('/tmp/fb_cookies_full.sqlite')
    cur = conn.cursor()
    cur.execute("SELECT host, name, value, path FROM moz_cookies WHERE host LIKE '%facebook%'")
    rows = cur.fetchall()
    conn.close()
    
    pw_cookies = []
    for host, name, value, path in rows:
        domain = host if host.startswith('.') else '.' + host
        pw_cookies.append({'name': name, 'value': value, 'domain': domain, 'path': path or '/'})
    return pw_cookies

def get_new_token():
    try:
        pw_cookies = extract_cookies()
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
                viewport={'width': 1280, 'height': 720}
            )
            context.add_cookies(pw_cookies)
            page = context.new_page()
            
            try:
                page.goto('https://developers.facebook.com/tools/explorer/', wait_until='domcontentloaded', timeout=15000)
                time.sleep(3)  # Wait for the react app to render
            except Exception as e:
                print(f"Page load timeout/error: {e}")
                
            html = page.content()
            browser.close()
            
            m = re.search(r'EAA[A-Za-z0-9_]{50,}', html)
            if m:
                user_token = m.group(0)
                PAGE_ID = os.getenv('FB_PAGE_ID', '1105214619347449')
                res = requests.get('https://graph.facebook.com/me/accounts', params={'access_token': user_token}, timeout=10)
                for p in res.json().get('data', []):
                    if p['id'] == PAGE_ID:
                        return p['access_token']
            else:
                with open("/tmp/pw_fb_error.html", "w") as f:
                    f.write(html)
    except Exception as e:
        print(f"Token fetch error: {e}")
    return None

if __name__ == "__main__":
    t = get_new_token()
    if t:
        print(f"SUCCESS:{t}")
    else:
        print("FAILED")
