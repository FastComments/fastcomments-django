"""FastComments integration for Django.

Embed the FastComments widgets and sign Secure SSO with template tags, and make
server-side REST calls through the FastComments Python SDK.
"""

from importlib.metadata import PackageNotFoundError, version

from .api import admin, get_manager, public_api, sso_for_widget

try:
    # Single source of truth: the version declared in pyproject.toml.
    __version__ = version("fastcomments-django")
except PackageNotFoundError:  # running from a source checkout that isn't installed
    __version__ = "0.0.0"

__all__ = ["get_manager", "admin", "public_api", "sso_for_widget", "__version__"]
