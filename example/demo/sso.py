"""Demo SSO mapper + seeding.

`map_user` is wired into the plugin via FASTCOMMENTS["SSO"]["USER_MAPPER"]. It
turns the signed-in Django user into the FastComments identity fields, pulling
the display name / avatar / admin flag from the pre-seeded demo user record.
"""

from typing import Any

from django.contrib.auth import get_user_model

from .demo_users import BY_USERNAME, DEMO_USERS


def map_user(user: Any) -> dict[str, Any]:
    profile: dict[str, Any] = BY_USERNAME.get(user.username) or {}
    return {
        # The FastComments id is the stable handle, never anything private.
        "id": user.username,
        "email": user.email,
        "username": user.username,
        "display_name": profile.get("display_name"),
        "avatar": profile.get("avatar"),
        "is_admin": profile.get("is_admin", False),
    }


def ensure_demo_users() -> None:
    """Create the demo users on first use (lazy; never at import time)."""
    User = get_user_model()
    for profile in DEMO_USERS:
        User.objects.get_or_create(
            username=profile["username"],
            defaults={
                "email": profile["email"],
                "first_name": profile["display_name"],
                "is_staff": profile["is_admin"],
            },
        )
