"""Manual browser smoke test for the FastComments Django showcase.

Drives a real Chromium via Playwright: signs in as a pre-seeded demo user, then
confirms the comment widget authenticates that identity (Secure SSO) and that a
comment can be posted. This is a manual e2e (it needs a real tenant + network to
fastcomments.com), not part of the unit suite.

Usage:
    pip install playwright && playwright install chromium
    export FASTCOMMENTS_TENANT_ID=... FASTCOMMENTS_API_KEY=...
    python manage.py migrate
    python manage.py runserver 127.0.0.1:8150 &
    python browser_smoke.py
"""
import sys
import time

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8150"


def main():
    marker = f"django-browser-smoke-{int(time.time())}"
    text = f"Secure SSO browser smoke test. Marker {marker}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        # en-US avoids a headless C.UTF-8 locale breaking Intl inside the widget.
        ctx = browser.new_context(locale="en-US", viewport={"width": 1280, "height": 1500})
        page = ctx.new_page()

        # Sign in as a pre-seeded demo user; lands on the comment widget page.
        page.goto(BASE + "/signin/", wait_until="networkidle", timeout=60000)
        page.get_by_role("button", name="Sign in as User One").click()
        page.wait_for_load_state("networkidle", timeout=60000)
        assert "/w/comments/" in page.url, "did not land on the comments page"
        assert page.get_by_text("VIP User").count() > 0, "rail did not show the signed-in user"

        # The comment widget renders in a fastcomments.com/embed iframe.
        page.wait_for_timeout(5000)
        frame = [f for f in page.frames if "fastcomments.com/embed" in f.url and "django-demo%22" in f.url][0]
        frame.wait_for_selector("textarea.comment-input", timeout=30000)
        assert frame.get_by_text("User One").count() > 0, "Secure SSO user not shown in widget"

        frame.fill("textarea.comment-input", text)
        frame.get_by_text("Submit Reply", exact=False).first.click()
        frame.wait_for_selector(f"text={marker}", timeout=30000)

        print("PASS: signed in as User One, widget authenticated via Secure SSO, comment posted:", marker)
        ctx.close()
        browser.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print("FAIL:", exc)
        sys.exit(1)
