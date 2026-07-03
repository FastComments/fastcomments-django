"""Tests for the FastComments template tags and widget.html rendering."""

import json
import re
from types import SimpleNamespace

from django.template import Context, Template
from django.test import RequestFactory, override_settings


def render(tpl_str, context=None):
    return Template("{% load fastcomments %}" + tpl_str).render(Context(context or {}))


def config_from(html):
    """Parse the json_script payload the widget mounts with."""
    match = re.search(r'type="application/json">(.*?)</script>', html, re.S)
    assert match, "no json_script block found"
    return json.loads(match.group(1))


def _request_with_user(**user_kwargs):
    request = RequestFactory().get("/")
    request.user = SimpleNamespace(is_authenticated=True, **user_kwargs)
    return request


@override_settings(FASTCOMMENTS={"TENANT_ID": "demo"})
def test_comments_basic():
    html = render("{% fastcomments url_id='my-page' locale='en_us' %}")
    assert 'id="fc-' in html
    assert "https://cdn.fastcomments.com/js/embed-v2.min.js" in html
    assert "FastCommentsUI" in html
    cfg = config_from(html)
    assert cfg["tenantId"] == "demo"
    assert cfg["urlId"] == "my-page"
    assert cfg["locale"] == "en_us"


@override_settings(FASTCOMMENTS={"TENANT_ID": "demo", "REGION": "eu"})
def test_eu_cdn_swap():
    html = render("{% fastcomments url_id='p' %}")
    assert "https://cdn-eu.fastcomments.com/js/embed-v2.min.js" in html
    assert config_from(html)["region"] == "eu"


@override_settings(FASTCOMMENTS={"TENANT_ID": "demo"})
def test_live_chat():
    html = render("{% fastcomments_live_chat url_id='room' %}")
    assert "embed-live-chat.min.js" in html
    assert "FastCommentsLiveChat" in html


@override_settings(FASTCOMMENTS={"TENANT_ID": "demo"})
def test_comment_count_is_span():
    html = render("{% fastcomments_comment_count url_id='p' number_only=True %}")
    assert '<span id="fc-count-' in html
    assert "widget-comment-count.min.js" in html
    assert config_from(html)["numberOnly"] is True


@override_settings(FASTCOMMENTS={"TENANT_ID": "demo"})
def test_bulk_emits_no_container():
    html = render("{% fastcomments_comment_count_bulk %}")
    assert "widget-comment-count-bulk.min.js" in html
    assert '<div id="fc-count-bulk-' not in html  # bulk emits no container element


@override_settings(FASTCOMMENTS={"TENANT_ID": "demo"})
def test_count_marker():
    html = render("{% fastcomments_count_marker url_id='p1' %}")
    assert 'class="fast-comments-count"' in html
    assert 'data-fast-comments-url-id="p1"' in html


@override_settings(FASTCOMMENTS={"TENANT_ID": "demo"})
def test_collab_chat_selector_strips_target():
    html = render("{% fastcomments_collab_chat target='#discussion' %}")
    assert "embed-collab-chat.min.js" in html
    assert "#discussion" in html  # used as the querySelector target
    assert "target" not in config_from(html)  # never in the widget config


@override_settings(FASTCOMMENTS={"TENANT_ID": "demo"})
def test_user_activity_callback():
    html = render("{% fastcomments_user_activity user_id='u1' %}")
    assert "embed-user-activity.min.js" in html
    assert '"useCallback": true' in html
    assert config_from(html)["userId"] == "u1"


@override_settings(FASTCOMMENTS={"TENANT_ID": "demo"})
def test_recent_and_top_widgets():
    assert "widget-recent-comments-v2.min.js" in render("{% fastcomments_recent_comments %}")
    assert "widget-recent-discussions-v2.min.js" in render("{% fastcomments_recent_discussions %}")
    assert "embed-reviews-summary.min.js" in render("{% fastcomments_reviews_summary %}")
    assert "widget-top-pages-v2.min.js" in render("{% fastcomments_top_pages %}")


@override_settings(
    FASTCOMMENTS={
        "TENANT_ID": "demo",
        "API_KEY": "sekret",
        "SSO": {"ENABLED": True, "MODE": "secure", "LOGIN_URL": "/login"},
    }
)
def test_sso_injected_for_authenticated_user():
    request = _request_with_user(id=5, email="a@b.com", username="alice")
    html = render("{% fastcomments url_id='p' %}", {"request": request})
    cfg = config_from(html)
    assert "sso" in cfg
    assert "userDataJSONBase64" in cfg["sso"]
    assert cfg["sso"]["loginURL"] == "/login"


@override_settings(
    FASTCOMMENTS={
        "TENANT_ID": "demo",
        "API_KEY": "sekret",
        "SSO": {"ENABLED": True, "MODE": "secure", "LOGIN_URL": "/login"},
    }
)
def test_anonymous_user_gets_login_only():
    html = render("{% fastcomments url_id='p' %}")  # no request -> anonymous
    cfg = config_from(html)
    # loginURL is explicit; logoutURL falls back to reverse("logout"). No user data.
    assert cfg["sso"] == {"loginURL": "/login", "logoutURL": "/logout/"}


@override_settings(FASTCOMMENTS={"TENANT_ID": "demo"})
def test_config_json_is_xss_escaped():
    html = render("{% fastcomments url_id='</script><b>xss' %}")
    # json_script escapes <, >, & so the raw closing tag cannot break out.
    assert "</script><b>xss" not in html
    # ...but the decoded value round-trips intact.
    assert config_from(html)["urlId"] == "</script><b>xss"
