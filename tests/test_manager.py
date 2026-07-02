"""Tests for FastCommentsManager (hosts, widget config, API construction)."""

import pytest
from django.test import override_settings

from fastcomments_django.api import get_manager


@override_settings(FASTCOMMENTS={"TENANT_ID": "t"})
def test_us_hosts():
    manager = get_manager()
    assert manager.cdn_host() == "https://cdn.fastcomments.com"
    assert manager.api_host() == "https://fastcomments.com"


@override_settings(FASTCOMMENTS={"TENANT_ID": "t", "REGION": "eu"})
def test_eu_hosts():
    manager = get_manager()
    assert manager.cdn_host() == "https://cdn-eu.fastcomments.com"
    assert manager.api_host() == "https://eu.fastcomments.com"


@override_settings(FASTCOMMENTS={"TENANT_ID": "t", "WIDGET_DEFAULTS": {"locale": "en_us"}})
def test_widget_config_merge_us():
    cfg = get_manager().widget_config({"urlId": "p", "readonly": None})
    assert cfg["tenantId"] == "t"
    assert cfg["locale"] == "en_us"
    assert cfg["urlId"] == "p"
    assert "readonly" not in cfg  # None overrides are dropped
    assert "region" not in cfg  # US: no region key


@override_settings(FASTCOMMENTS={"TENANT_ID": "t", "REGION": "eu"})
def test_widget_config_region_and_apihost_eu():
    cfg = get_manager().widget_config({})
    assert cfg["region"] == "eu"
    assert cfg["apiHost"] == "https://eu.fastcomments.com"


@override_settings(FASTCOMMENTS={"TENANT_ID": "t", "API_KEY": "k"})
def test_admin_api_construction():
    try:
        api = get_manager().admin()
    except ImportError:
        pytest.skip("fastcomments-django[api] client extra not installed")
    assert api.__class__.__name__ == "DefaultApi"
