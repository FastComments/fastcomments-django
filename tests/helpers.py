"""Helpers referenced by tests via dotted-path settings."""


def map_user(user):
    """A USER_MAPPER callable referenced by dotted path in a test."""
    return {"id": "99", "email": "helper@example.com", "username": "helper"}
