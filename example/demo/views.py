"""Views for the FastComments Django showcase.

A left-rail + main-stage app (styled after the fastcomments-react showcase) with
a pre-seeded demo-user sign-in that drives Secure SSO.
"""

from typing import Any

from django.contrib.auth import get_user_model, login, logout
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from fastcomments_django import conf as fc_conf

from .demo_users import BY_USERNAME, DEMO_USERS
from .sso import ensure_demo_users

# Each widget example: nav label/hint plus its DemoChrome header + tags.
WIDGETS: list[dict[str, Any]] = [
    {
        "key": "comments",
        "label": "Live Comment Widget",
        "hint": "Full live commenting widget",
        "subtitle": "The flagship live commenting widget: replies, voting, moderation, media, and realtime sync.",
        "tags": ["urlId · django-demo"],
        "sso": True,
    },
    {
        "key": "comment-count",
        "label": "Comment Count",
        "hint": "Inline count badge",
        "subtitle": "A tiny inline badge with the number of comments on a page, for article and index lists.",
        "tags": ["urlId · django-demo"],
        "sso": False,
    },
    {
        "key": "live-chat",
        "label": "Live Chat",
        "hint": "Realtime streaming widget",
        "subtitle": "The streaming flavor of the core widget, tuned for live events and high-volume broadcasts.",
        "tags": ["Mode · streaming"],
        "sso": True,
    },
    {
        "key": "collab-chat",
        "label": "Collab Chat",
        "hint": "Text-anchored threads",
        "subtitle": "Select any text to start an inline discussion, anchored to an element via a CSS selector.",
        "tags": ["Anchor · #collab-target"],
        "sso": True,
    },
    {
        "key": "image-chat",
        "label": "Image Chat",
        "hint": "Region comments on images",
        "subtitle": "Comment on regions of an image. Attaches to an <img> element via a CSS selector.",
        "tags": ["Anchor · #image-target"],
        "sso": True,
    },
    {
        "key": "reviews-summary",
        "label": "Reviews Summary",
        "hint": "Star ratings overview",
        "subtitle": "An aggregate star-ratings overview for a page. Requires ratings questions on the tenant.",
        "tags": ["urlId · django-demo"],
        "sso": False,
    },
    {
        "key": "activity-feed",
        "label": "Activity Feed",
        "hint": "Per-user timeline",
        "subtitle": "A timeline of one user's comment activity across the site.",
        "tags": ["Per-user"],
        "sso": True,
    },
    {
        "key": "recent-comments",
        "label": "Recent Comments",
        "hint": "Newest comments site-wide",
        "subtitle": "The most recent comments across the whole site.",
        "tags": ["Site-wide"],
        "sso": False,
    },
    {
        "key": "recent-discussions",
        "label": "Recent Discussions",
        "hint": "Most active threads",
        "subtitle": "The most recently active discussion threads across the site.",
        "tags": ["Site-wide"],
        "sso": False,
    },
    {
        "key": "top-pages",
        "label": "Top Pages",
        "hint": "Most-discussed pages",
        "subtitle": "The most-discussed pages across the site, ranked by activity.",
        "tags": ["Site-wide"],
        "sso": False,
    },
]

FLOWS: list[dict[str, Any]] = [
    {"key": "secure-sso", "label": "Secure SSO", "hint": "HMAC-signed identity"},
]

REGISTRY: dict[str, dict[str, Any]] = {w["key"]: w for w in WIDGETS}
NAV_GROUPS: list[dict[str, Any]] = [
    {"num": "01", "title": "Widgets", "items": WIDGETS},
    {"num": "02", "title": "Flows", "items": FLOWS},
]


def base_context(request: HttpRequest, current_key: str) -> dict[str, Any]:
    fc = fc_conf.get_config()
    # "Configured" = a real tenant + API secret (needed for Secure SSO). Without
    # them the demo falls back to the public "demo" tenant, so we prompt for setup.
    configured = bool(fc["API_KEY"]) and fc["TENANT_ID"] != "demo"
    profile = BY_USERNAME.get(request.user.username) if request.user.is_authenticated else None
    return {
        "nav_groups": NAV_GROUPS,
        "current_key": current_key,
        "fc_user": profile,
        "configured": configured,
    }


def home(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html", {**base_context(request, "home"), "widgets": WIDGETS, "flows": FLOWS})


def widget(request: HttpRequest, key: str) -> HttpResponse:
    spec = REGISTRY.get(key)
    if spec is None:
        raise Http404("unknown widget")
    activity_user_id = request.user.username if request.user.is_authenticated else "user-1"
    return render(
        request, "widget.html", {**base_context(request, key), "w": spec, "activity_user_id": activity_user_id}
    )


def signin(request: HttpRequest) -> HttpResponse:
    ensure_demo_users()
    if request.method == "POST":
        username = request.POST.get("username")
        if username in BY_USERNAME:
            user = get_user_model().objects.get(username=username)
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            nxt = request.POST.get("next")
            return redirect(nxt) if nxt else redirect("widget", key="comments")
    return render(request, "signin.html", {**base_context(request, "secure-sso"), "demo_users": DEMO_USERS})


def signout(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("home")
