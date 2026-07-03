"""Every widget renders correctly, and secure SSO is injected into exactly the
widgets that support it (and no others)."""

import json
import re
from types import SimpleNamespace

import pytest
from django.template import Context, Template
from django.test import RequestFactory, override_settings

SECURE_SSO_SETTINGS = {
    "TENANT_ID": "demo",
    "API_KEY": "example-secret",
    "SSO": {"ENABLED": True, "MODE": "secure", "LOGIN_URL": "/login", "LOGOUT_URL": "/logout"},
}

# (tag source, expected CDN script, expected constructor, injects secure SSO?)
WIDGETS = [
    ("{% fastcomments url_id='p' %}", "embed-v2.min.js", "FastCommentsUI", True),
    ("{% fastcomments_live_chat url_id='p' %}", "embed-live-chat.min.js", "FastCommentsLiveChat", True),
    ("{% fastcomments_collab_chat target='#a' %}", "embed-collab-chat.min.js", "FastCommentsCollabChat", True),
    ("{% fastcomments_image_chat target='#i' %}", "embed-image-chat.min.js", "FastCommentsImageChat", True),
    ("{% fastcomments_user_activity user_id='u1' %}", "embed-user-activity.min.js", "FastCommentsUserActivity", True),
    ("{% fastcomments_comment_count url_id='p' %}", "widget-comment-count.min.js", "FastCommentsCommentCount", False),
    ("{% fastcomments_comment_count_bulk %}", "widget-comment-count-bulk.min.js", "FastCommentsCommentCountBulk", False),
    ("{% fastcomments_recent_comments %}", "widget-recent-comments-v2.min.js", "FastCommentsRecentCommentsV2", False),
    ("{% fastcomments_recent_discussions %}", "widget-recent-discussions-v2.min.js", "FastCommentsRecentDiscussionsV2", False),
    ("{% fastcomments_reviews_summary %}", "embed-reviews-summary.min.js", "FastCommentsReviewsSummaryWidget", False),
    ("{% fastcomments_top_pages %}", "widget-top-pages-v2.min.js", "FastCommentsTopPagesV2", False),
]


def _render(tag_src):
    request = RequestFactory().get("/")
    request.user = SimpleNamespace(is_authenticated=True, id=5, email="a@b.com", username="alice")
    html = Template("{% load fastcomments %}" + tag_src).render(Context({"request": request}))
    blocks = [json.loads(m) for m in re.findall(r'type="application/json">(.*?)</script>', html, re.S)]
    config = next(b for b in blocks if "tenantId" in b)
    meta = next(b for b in blocks if "src" in b and "name" in b)
    return html, config, meta


@pytest.mark.parametrize("tag_src,script,constructor,takes_sso", WIDGETS)
@override_settings(FASTCOMMENTS=SECURE_SSO_SETTINGS)
def test_widget_renders_and_sso_matrix(tag_src, script, constructor, takes_sso):
    _, config, meta = _render(tag_src)

    # Correct CDN script + global constructor for this widget.
    assert meta["src"].endswith(script)
    assert meta["name"] == constructor
    assert config["tenantId"] == "demo"

    if takes_sso:
        # Secure SSO is injected: a signed payload, never a simpleSSO object.
        assert "sso" in config, f"{constructor} should receive secure SSO"
        assert "userDataJSONBase64" in config["sso"]
        assert "verificationHash" in config["sso"]
        assert "timestamp" in config["sso"]
        assert "simpleSSO" not in config
    else:
        # Non-SSO widgets carry no identity payload at all.
        assert "sso" not in config, f"{constructor} should not receive SSO"
        assert "simpleSSO" not in config


@override_settings(FASTCOMMENTS=SECURE_SSO_SETTINGS)
def test_all_eleven_widgets_covered():
    # Guard: the matrix must exercise every widget in the registry.
    from fastcomments_django import widgets as W
    tested = {c for _, _, c, _ in WIDGETS}
    registry = {spec.constructor for spec in W.WIDGETS.values()}
    assert tested == registry, f"missing from matrix: {registry - tested}"
