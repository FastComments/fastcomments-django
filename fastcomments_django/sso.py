"""SSO for Django: map the current user, then delegate signing to the SDK.

The crypto lives in the FastComments Python SDK (``sso`` package). This module
only turns a Django user into the FastComments field dict and assembles the
widget ``sso`` / ``simpleSSO`` config, mirroring the Laravel package's
SSOUserMapper + SSOManager split.
"""

from importlib import import_module
from typing import Any

from django.urls import NoReverseMatch, reverse

# The signer from the FastComments Python SDK (a hard dependency). This is the
# top-level `sso` package installed by fastcomments-python, not this module.
from sso import FastCommentsSSO, SecureSSOUserData, SimpleSSOUserData


def _import_dotted(path: str) -> Any:
    module_path, _, attr = path.rpartition(".")
    if not module_path:
        raise ImportError(f"'{path}' is not a dotted path to a callable")
    return getattr(import_module(module_path), attr)


def _resolve(obj: Any, path: str) -> Any:
    """Walk a dotted attribute/dict path; call the final value if it's callable."""
    value = obj
    for part in path.split("."):
        if value is None:
            return None
        if isinstance(value, dict):
            value = value.get(part)
        else:
            value = getattr(value, part, None)
    if callable(value):
        value = value()
    return value


def _try_reverse(name: str) -> str | None:
    try:
        return reverse(name)
    except NoReverseMatch:
        return None


class SSOUserMapper:
    """Turn a Django user into the FastComments user field dict.

    Precedence: global USER_MAPPER, then a duck-typed
    ``user.to_fastcomments_user_data()`` method, then the USER_MAP config.
    """

    def __init__(
        self,
        user_map: dict[str, Any] | None = None,
        is_admin: Any = None,
        is_moderator: Any = None,
        group_ids: Any = None,
        user_mapper: Any = None,
    ) -> None:
        self.user_map = user_map or {}
        self.is_admin = is_admin
        self.is_moderator = is_moderator
        self.group_ids = group_ids
        self.user_mapper = user_mapper

    def map(self, user: Any) -> dict[str, Any]:
        if self.user_mapper is not None:
            fn = self.user_mapper if callable(self.user_mapper) else _import_dotted(self.user_mapper)
            return self._normalize(fn(user) or {})

        method = getattr(user, "to_fastcomments_user_data", None)
        if callable(method):
            return self._normalize(method() or {})

        data: dict[str, Any] = {}
        for fc_field, source in self.user_map.items():
            if source is None:
                continue
            data[fc_field] = self._apply(user, source)
        for fc_field, source in (
            ("is_admin", self.is_admin),
            ("is_moderator", self.is_moderator),
            ("group_ids", self.group_ids),
        ):
            if source is not None:
                data[fc_field] = self._apply(user, source)
        return self._normalize(data)

    def _apply(self, user: Any, source: Any) -> Any:
        if callable(source):
            return source(user)
        if isinstance(source, str):
            return _resolve(user, source)
        return source

    def _normalize(self, data: dict[str, Any]) -> dict[str, Any]:
        result = {k: v for k, v in data.items() if v is not None}
        if "id" in result:
            result["id"] = str(result["id"])
        return result


def _secure_user_data(mapped: dict[str, Any]) -> Any:
    return SecureSSOUserData(
        id=mapped.get("id"),
        email=mapped.get("email"),
        username=mapped.get("username"),
        avatar=mapped.get("avatar"),
        display_name=mapped.get("display_name"),
        website_url=mapped.get("website_url"),
        group_ids=mapped.get("group_ids"),
        is_admin=mapped.get("is_admin"),
        is_moderator=mapped.get("is_moderator"),
    )


def _simple_user_data(mapped: dict[str, Any]) -> Any:
    return SimpleSSOUserData(
        username=mapped.get("username"),
        email=mapped.get("email"),
        avatar=mapped.get("avatar"),
        website_url=mapped.get("website_url"),
        display_name=mapped.get("display_name"),
    )


class SSOManager:
    """Assemble the widget SSO config for the current user."""

    def __init__(
        self,
        mapper: SSOUserMapper,
        api_key: str,
        enabled: bool,
        mode: str,
        login_url: str | None,
        logout_url: str | None,
    ) -> None:
        self.mapper = mapper
        self.api_key = api_key
        self.enabled = enabled
        self.mode = mode
        self.login_url = login_url
        self.logout_url = logout_url

    def is_enabled(self) -> bool:
        return bool(self.enabled)

    def _urls(self) -> tuple[str | None, str | None]:
        login = self.login_url if self.login_url is not None else _try_reverse("login")
        logout = self.logout_url if self.logout_url is not None else _try_reverse("logout")
        return login, logout

    def for_widget(self, user: Any = None) -> dict[str, Any] | None:
        """Return the config fragment to merge into a widget config, or None."""
        if not self.enabled:
            return None
        if self.mode == "simple":
            return self._simple(user)
        return self._secure(user)

    def _secure(self, user: Any) -> dict[str, Any]:
        login, logout = self._urls()
        sso: dict[str, Any] = {}
        if user is not None:
            payload = FastCommentsSSO.new_secure(
                self.api_key, _secure_user_data(self.mapper.map(user))
            ).secure_sso_payload
            sso.update(payload.to_widget_dict())
        if login is not None:
            sso["loginURL"] = login
        if logout is not None:
            sso["logoutURL"] = logout
        return {"sso": sso}

    def _simple(self, user: Any) -> dict[str, Any]:
        login, logout = self._urls()
        result: dict[str, Any] = {}
        if login is not None:
            result["loginURL"] = login
        if logout is not None:
            result["logoutURL"] = logout
        if user is not None:
            result["simpleSSO"] = _simple_user_data(self.mapper.map(user)).to_dict()
        return result

    def token_for(self, user: Any) -> str:
        """Return the signed SSO token JSON string (parity with Laravel tokenFor)."""
        mapped = self.mapper.map(user)
        if self.mode == "simple":
            return FastCommentsSSO.new_simple(_simple_user_data(mapped)).create_token()
        return FastCommentsSSO.new_secure(self.api_key, _secure_user_data(mapped)).create_token()
