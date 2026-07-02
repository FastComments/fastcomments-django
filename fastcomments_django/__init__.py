"""FastComments integration for Django.

Embed the FastComments widgets and sign Secure SSO with template tags, and make
server-side REST calls through the FastComments Python SDK.
"""

__version__ = "0.1.0"

from .api import get_manager, admin, public_api, sso_for_widget

__all__ = ["get_manager", "admin", "public_api", "sso_for_widget", "__version__"]
