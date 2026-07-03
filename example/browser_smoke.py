"""Manual browser smoke test for the FastComments Django example.

Drives a real Chromium via Playwright to confirm the widgets render and that a
user authenticated with Secure SSO can leave a comment. This is a manual e2e
(it needs a real tenant + network to fastcomments.com), not part of the unit
suite.

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

URL = "http://127.0.0.1:8150/"


def main():
    marker = f"django-browser-smoke-{int(time.time())}"
    text = f"Secure SSO browser smoke test. Marker {marker}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        # en-US avoids a headless C.UTF-8 locale breaking Intl inside the widget.
        ctx = browser.new_context(locale="en-US", viewport={"width": 1100, "height": 1500})
        page = ctx.new_page()
        page.goto(URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(5000)

        # The comment/live-chat widgets render inside fastcomments.com/embed iframes.
        comments = [f for f in page.frames if "fastcomments.com/embed" in f.url and "django-demo%22" in f.url]
        assert comments, "comments widget iframe not found"
        frame = comments[0]

        frame.wait_for_selector("textarea.comment-input", timeout=30000)
        assert frame.get_by_text("demo_user").count() > 0, "Secure SSO user not shown"

        frame.fill("textarea.comment-input", text)
        frame.get_by_text("Submit Reply", exact=False).first.click()
        frame.wait_for_selector(f"text={marker}", timeout=30000)

        print("PASS: widgets rendered, Secure SSO user recognized, comment posted:", marker)
        ctx.close()
        browser.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print("FAIL:", exc)
        sys.exit(1)
