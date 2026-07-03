"""Module-level facade over a memoized FastCommentsManager.

Python doesn't need Laravel-style facades; a module with a memoized singleton
is the idiomatic equivalent. The manager is rebuilt whenever ``FASTCOMMENTS``
changes (e.g. under ``override_settings`` in tests).
"""

from typing import Any

from django.core.signals import setting_changed
from django.dispatch import receiver

from . import conf
from .manager import FastCommentsManager
from .sso import SSOManager, SSOUserMapper

_manager: FastCommentsManager | None = None


def get_manager() -> FastCommentsManager:
    global _manager
    if _manager is None:
        c = conf.get_config()
        sso_cfg = c["SSO"]
        mapper = SSOUserMapper(
            user_map=sso_cfg["USER_MAP"],
            is_admin=sso_cfg["IS_ADMIN"],
            is_moderator=sso_cfg["IS_MODERATOR"],
            group_ids=sso_cfg["GROUP_IDS"],
            user_mapper=sso_cfg["USER_MAPPER"],
        )
        sso_manager = SSOManager(
            mapper=mapper,
            api_key=c["API_KEY"],
            enabled=sso_cfg["ENABLED"],
            mode=sso_cfg["MODE"],
            login_url=sso_cfg["LOGIN_URL"],
            logout_url=sso_cfg["LOGOUT_URL"],
        )
        _manager = FastCommentsManager(
            tenant_id=c["TENANT_ID"],
            api_key=c["API_KEY"],
            region=c["REGION"],
            widget_defaults=c["WIDGET_DEFAULTS"],
            sso_manager=sso_manager,
        )
    return _manager


def reset_manager() -> None:
    global _manager
    _manager = None


def admin() -> Any:
    return get_manager().admin()


def public_api() -> Any:
    return get_manager().public_api()


def sso_for_widget(user: Any = None) -> dict[str, Any] | None:
    return get_manager().sso().for_widget(user)


@receiver(setting_changed)
def _on_setting_changed(sender: object, setting: str, **kwargs: Any) -> None:
    if setting == "FASTCOMMENTS":
        reset_manager()
