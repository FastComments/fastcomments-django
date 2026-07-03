"""The FastComments service: hosts, widget config assembly, and API access."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .sso import SSOManager

US_CDN = "https://cdn.fastcomments.com"
EU_CDN = "https://cdn-eu.fastcomments.com"
US_API = "https://fastcomments.com"
EU_API = "https://eu.fastcomments.com"


class FastCommentsManager:
    def __init__(
        self,
        tenant_id: str,
        api_key: str,
        region: str | None,
        widget_defaults: dict[str, Any] | None,
        sso_manager: "SSOManager",
    ) -> None:
        self._tenant_id = tenant_id
        self._api_key = api_key
        self._region = region
        self._widget_defaults = widget_defaults or {}
        self._sso = sso_manager

    @property
    def tenant_id(self) -> str:
        return self._tenant_id

    @property
    def region(self) -> str | None:
        return self._region

    def sso(self) -> "SSOManager":
        return self._sso

    def _is_eu(self) -> bool:
        return (self._region or "").lower() == "eu"

    def cdn_host(self) -> str:
        return EU_CDN if self._is_eu() else US_CDN

    def api_host(self) -> str:
        return EU_API if self._is_eu() else US_API

    def widget_config(self, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
        """Assemble a widget config: defaults + tenantId + overrides (+ EU hosts)."""
        cfg = dict(self._widget_defaults)
        cfg["tenantId"] = self._tenant_id
        if overrides:
            cfg.update({k: v for k, v in overrides.items() if v is not None})
        # EU accounts route the widget's REST/WS calls to the EU region. `region`
        # drives the EmbedCore widgets; `apiHost` covers the standalone widgets
        # (comment-count-bulk, recent-*, top-pages) that read apiHost directly.
        if self._is_eu():
            cfg["region"] = "eu"  # the only region value the widget JS checks for
            cfg["apiHost"] = self.api_host()
        return cfg

    def admin(self) -> Any:
        """Return the SDK's DefaultApi (authenticated) configured for this tenant."""
        return self._build_api(authenticated=True)

    def public_api(self) -> Any:
        """Return the SDK's PublicApi (unauthenticated)."""
        return self._build_api(authenticated=False)

    def _build_api(self, authenticated: bool) -> Any:
        try:
            from client.api_client import ApiClient
            from client.configuration import Configuration

            if authenticated:
                from client.api.default_api import DefaultApi as ApiCls
            else:
                from client.api.public_api import PublicApi as ApiCls
        except ImportError as exc:  # pragma: no cover - exercised only without the extra
            raise ImportError(
                "Server-side FastComments API access requires the generated client. "
                "Install it with: pip install 'fastcomments-django[api]'"
            ) from exc

        config = Configuration(host=self.api_host())
        if authenticated and self._api_key:
            config.api_key = {"api_key": self._api_key}
        return ApiCls(ApiClient(configuration=config))
