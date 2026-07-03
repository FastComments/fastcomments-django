"""Tests for the Django SSOManager (delegates signing to the SDK)."""

import base64
import hashlib
import hmac
import json
from types import SimpleNamespace

from django.test import override_settings

from fastcomments_django.api import get_manager

SECRET = "unit-secret"


def _user(**kwargs):
    return SimpleNamespace(**kwargs)


@override_settings(FASTCOMMENTS={"TENANT_ID": "demo", "API_KEY": SECRET, "SSO": {"ENABLED": False}})
def test_disabled_returns_none():
    user = _user(id=1, email="a@b.com", username="u")
    assert get_manager().sso().for_widget(user) is None


@override_settings(
    FASTCOMMENTS={
        "TENANT_ID": "demo",
        "API_KEY": SECRET,
        "SSO": {"ENABLED": True, "MODE": "secure", "LOGIN_URL": "/login", "LOGOUT_URL": "/logout"},
    }
)
def test_secure_no_user_only_urls():
    result = get_manager().sso().for_widget(None)
    assert result == {"sso": {"loginURL": "/login", "logoutURL": "/logout"}}


@override_settings(
    FASTCOMMENTS={
        "TENANT_ID": "demo",
        "API_KEY": SECRET,
        "SSO": {"ENABLED": True, "MODE": "secure", "LOGIN_URL": "/login", "LOGOUT_URL": "/logout"},
    }
)
def test_secure_with_user_signs_correctly():
    user = _user(id=42, email="a@b.com", username="alice")
    sso = get_manager().sso().for_widget(user)["sso"]

    assert set(sso) >= {"userDataJSONBase64", "verificationHash", "timestamp", "loginURL", "logoutURL"}
    assert sso["timestamp"] >= 10**12  # milliseconds

    decoded = json.loads(base64.b64decode(sso["userDataJSONBase64"]))
    assert decoded["id"] == "42"  # stringified
    assert decoded["username"] == "alice"

    expected = hmac.new(
        SECRET.encode("utf-8"),
        (str(sso["timestamp"]) + sso["userDataJSONBase64"]).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    assert sso["verificationHash"] == expected


@override_settings(
    FASTCOMMENTS={
        "TENANT_ID": "demo",
        "API_KEY": SECRET,
        "SSO": {"ENABLED": True, "MODE": "simple", "LOGIN_URL": "/login", "LOGOUT_URL": "/logout"},
    }
)
def test_simple_with_user():
    user = _user(id=1, email="a@b.com", username="bob")
    result = get_manager().sso().for_widget(user)
    assert result["loginURL"] == "/login"
    assert result["simpleSSO"]["username"] == "bob"
    assert "userDataJSONBase64" not in result


@override_settings(
    FASTCOMMENTS={
        "TENANT_ID": "demo",
        "API_KEY": SECRET,
        "SSO": {"ENABLED": True, "MODE": "secure"},
    }
)
def test_login_logout_reverse_fallback():
    # No LOGIN_URL/LOGOUT_URL set -> falls back to reverse("login"/"logout").
    sso = get_manager().sso().for_widget(None)["sso"]
    assert sso["loginURL"] == "/login/"
    assert sso["logoutURL"] == "/logout/"


@override_settings(
    FASTCOMMENTS={
        "TENANT_ID": "demo",
        "API_KEY": SECRET,
        "SSO": {"ENABLED": True, "MODE": "secure"},
    }
)
def test_token_for_returns_signed_json():
    user = _user(id=7, email="a@b.com", username="u")
    parsed = json.loads(get_manager().sso().token_for(user))
    assert "userDataJSONBase64" in parsed
    assert json.loads(base64.b64decode(parsed["userDataJSONBase64"]))["id"] == "7"
