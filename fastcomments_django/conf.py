"""Access to the ``FASTCOMMENTS`` settings dict, with defaults and deep-merge.

The plugin never reads ``os.environ`` itself; it reads only
``settings.FASTCOMMENTS``. Projects wire environment variables in their own
``settings.py`` (see the README).
"""

import copy
from typing import Any

from django.conf import settings
from django.core.signals import setting_changed
from django.dispatch import receiver

# Casing note: top-level and SSO keys are UPPERCASE (Django convention, like
# REST_FRAMEWORK). WIDGET_DEFAULTS values are literal widget config (camelCase,
# passed straight to the widget JS) and USER_MAP keys are FastComments logical
# field names (snake_case), matching the Laravel package.
DEFAULTS: dict[str, Any] = {
    "TENANT_ID": "",
    "API_KEY": "",
    "REGION": None,  # None => US, "eu" => EU
    "SSO": {
        "ENABLED": False,
        "MODE": "secure",  # "secure" | "simple"
        "LOGIN_URL": None,  # None => reverse("login")
        "LOGOUT_URL": None,  # None => reverse("logout")
        # Map FastComments id to a STABLE, non-enumerable value chosen up front
        # (a UUID or opaque public id) rather than the Django primary key. See
        # the README "SSO identifiers" caveat; changing it later splits history.
        "USER_MAP": {
            "id": "id",
            "email": "email",
            "username": "username",
            "avatar": None,
            "display_name": None,
            "website_url": None,
        },
        "IS_ADMIN": None,
        "IS_MODERATOR": None,
        "GROUP_IDS": None,
        "USER_MAPPER": None,
    },
    "WIDGET_DEFAULTS": {},
}

_cache: dict[str, Any] | None = None


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def get_config() -> dict[str, Any]:
    """Return the merged config (user ``FASTCOMMENTS`` over ``DEFAULTS``)."""
    global _cache
    if _cache is None:
        user_config = getattr(settings, "FASTCOMMENTS", {}) or {}
        _cache = _deep_merge(DEFAULTS, user_config)
    return _cache


def get_setting(dotted_key: str, default: Any = None) -> Any:
    """Look up a config value by dotted path, e.g. ``get_setting("SSO.MODE")``."""
    node: Any = get_config()
    for part in dotted_key.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node


def reset_cache() -> None:
    global _cache
    _cache = None


@receiver(setting_changed)
def _on_setting_changed(sender: object, setting: str, **kwargs: Any) -> None:
    if setting == "FASTCOMMENTS":
        reset_cache()
