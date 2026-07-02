"""Unit tests for SSOUserMapper (Django user -> FastComments field dict)."""

from types import SimpleNamespace

from fastcomments_django.sso import SSOUserMapper


def test_attribute_map():
    mapper = SSOUserMapper(user_map={"id": "pk", "email": "email", "username": "name"})
    user = SimpleNamespace(pk=5, email="a@b.com", name="alice")
    assert mapper.map(user) == {"id": "5", "email": "a@b.com", "username": "alice"}


def test_dotted_path():
    mapper = SSOUserMapper(user_map={"id": "id", "avatar": "profile.avatar_url"})
    user = SimpleNamespace(id=1, profile=SimpleNamespace(avatar_url="https://x/a.png"))
    assert mapper.map(user)["avatar"] == "https://x/a.png"


def test_callable_source():
    mapper = SSOUserMapper(user_map={"id": "id", "username": lambda u: u.first + u.last})
    user = SimpleNamespace(id=1, first="a", last="b")
    assert mapper.map(user)["username"] == "ab"


def test_dotted_path_to_callable():
    mapper = SSOUserMapper(user_map={"id": "id", "username": "get_username"})
    user = SimpleNamespace(id=1, get_username=lambda: "called")
    assert mapper.map(user)["username"] == "called"


def test_duck_typed_method_takes_precedence():
    class User:
        def to_fastcomments_user_data(self):
            return {"id": "9", "email": "duck@x.com", "username": "duck"}

    mapper = SSOUserMapper(user_map={"id": "id", "email": "email", "username": "name"})
    assert mapper.map(User())["username"] == "duck"


def test_user_mapper_callable_takes_precedence_over_duck():
    class User:
        def to_fastcomments_user_data(self):
            return {"id": "1", "username": "duck"}

    mapper = SSOUserMapper(user_map={}, user_mapper=lambda u: {"id": "1", "username": "global"})
    assert mapper.map(User())["username"] == "global"


def test_user_mapper_dotted_path():
    mapper = SSOUserMapper(user_map={}, user_mapper="tests.helpers.map_user")
    assert mapper.map(SimpleNamespace())["username"] == "helper"


def test_roles_and_groups():
    mapper = SSOUserMapper(
        user_map={"id": "id"},
        is_admin=lambda u: u.staff,
        is_moderator=lambda u: False,
        group_ids=lambda u: ["g1", "g2"],
    )
    user = SimpleNamespace(id=1, staff=True)
    out = mapper.map(user)
    assert out["is_admin"] is True
    assert out["is_moderator"] is False
    assert out["group_ids"] == ["g1", "g2"]


def test_null_strip_keeps_falsey_and_stringifies_id():
    mapper = SSOUserMapper(
        user_map={"id": "id", "email": "email"},
        is_admin=lambda u: False,
        group_ids=lambda u: [],
    )
    user = SimpleNamespace(id=0, email=None)
    out = mapper.map(user)
    assert out["id"] == "0"  # 0 is stringified and kept
    assert "email" not in out  # only None is dropped
    assert out["is_admin"] is False
    assert out["group_ids"] == []
