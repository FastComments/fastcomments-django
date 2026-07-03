"""Pre-seeded demo users, mirroring the FastComments SSO reference demos.

These are shown on the sign-in page so you can sign in as any of them and watch
the widgets authenticate that identity via Secure SSO. Do NOT put private
information in the FastComments id.
"""

from typing import Any

from .avatar_utils import data_uri

DEMO_USERS: list[dict[str, Any]] = [
    {
        "username": "user-1",
        "email": "user-1@somewhere.com",
        "display_name": "User One",
        "avatar": data_uri("user-1"),
        "label": "VIP User",
        "is_admin": True,
    },
    {
        "username": "user-2",
        "email": "user-2@somewhere.com",
        "display_name": "User Two",
        "avatar": data_uri("user-2"),
        "label": "Member",
        "is_admin": False,
    },
    {
        "username": "user-3",
        "email": "user-3@somewhere.com",
        "display_name": "User Three",
        "avatar": data_uri("user-3"),
        "label": "Member",
        "is_admin": False,
    },
]

BY_USERNAME: dict[str, dict[str, Any]] = {u["username"]: u for u in DEMO_USERS}
