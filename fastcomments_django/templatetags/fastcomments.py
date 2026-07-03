"""Template tags that embed the FastComments widgets.

Load with ``{% load fastcomments %}``. Each tag is an inclusion tag rendering
``fastcomments/widget.html`` (the Django analog of the Laravel Blade
components). SSO for the current user is injected automatically for the widgets
that support it.
"""

import secrets
from typing import Any

from django import template

from .. import widgets as W
from ..api import get_manager

register = template.Library()


def _current_user(context: Any, explicit: Any) -> Any:
    """Resolve the user: explicit kwarg, else the authenticated request user."""
    if explicit is not None:
        return explicit
    request = context.get("request")
    if request is not None:
        user = getattr(request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False):
            return user
    return None


def _build(
    context: Any,
    spec: W.WidgetSpec,
    kwargs: dict[str, Any],
    user: Any,
    extra: dict[str, Any] | None,
    target: str | None = None,
) -> dict[str, Any]:
    manager = get_manager()

    overrides: dict[str, Any] = {}
    for snake, camel in spec.kwarg_map:
        value = kwargs.get(snake)
        if value is not None:
            overrides[camel] = value
    # Advanced escape hatch: pass any additional camelCase config keys directly.
    for key, value in (extra or {}).items():
        if value is not None:
            overrides[key] = value

    config = manager.widget_config(overrides)

    if spec.takes_sso:
        sso = manager.sso().for_widget(user)
        if sso:
            # secure -> {"sso": {...}}; simple -> {"simpleSSO": {...}, "loginURL": ...}
            config.update(sso)

    container_id = spec.id_prefix + secrets.token_hex(8)
    return {
        "container_id": container_id,
        "config_id": container_id + "-config",
        "meta_id": container_id + "-meta",
        "mount_type": spec.mount_type,
        "container_tag": spec.container_tag,
        "widget_config": config,
        # Mount metadata, emitted as a second json_script so URLs/selectors are
        # XSS-safe without escapejs mangling (which escapes hyphens).
        "mount_meta": {
            "src": manager.cdn_host() + spec.script_path,
            "name": spec.constructor,
            "mount": spec.mount_type,
            "target": target,
            "containerId": container_id,
            "useCallback": spec.use_callback,
        },
    }


@register.inclusion_tag("fastcomments/widget.html", takes_context=True)
def fastcomments(
    context: Any,
    url_id: Any = None,
    url: Any = None,
    readonly: Any = None,
    locale: Any = None,
    has_dark_background: Any = None,
    default_sort_direction: Any = None,
    user: Any = None,
    **extra: Any,
) -> dict[str, Any]:
    kwargs = {
        "url_id": url_id,
        "url": url,
        "readonly": readonly,
        "locale": locale,
        "has_dark_background": has_dark_background,
        "default_sort_direction": default_sort_direction,
    }
    return _build(context, W.WIDGETS["comments"], kwargs, _current_user(context, user), extra)


@register.inclusion_tag("fastcomments/widget.html", takes_context=True)
def fastcomments_live_chat(
    context: Any,
    url_id: Any = None,
    url: Any = None,
    readonly: Any = None,
    locale: Any = None,
    has_dark_background: Any = None,
    default_sort_direction: Any = None,
    user: Any = None,
    **extra: Any,
) -> dict[str, Any]:
    kwargs = {
        "url_id": url_id,
        "url": url,
        "readonly": readonly,
        "locale": locale,
        "has_dark_background": has_dark_background,
        "default_sort_direction": default_sort_direction,
    }
    return _build(context, W.WIDGETS["live_chat"], kwargs, _current_user(context, user), extra)


@register.inclusion_tag("fastcomments/widget.html", takes_context=True)
def fastcomments_comment_count(
    context: Any,
    url_id: Any = None,
    number_only: Any = None,
    is_live: Any = None,
    has_dark_background: Any = None,
    **extra: Any,
) -> dict[str, Any]:
    kwargs = {
        "url_id": url_id,
        "number_only": number_only,
        "is_live": is_live,
        "has_dark_background": has_dark_background,
    }
    return _build(context, W.WIDGETS["comment_count"], kwargs, None, extra)


@register.inclusion_tag("fastcomments/widget.html", takes_context=True)
def fastcomments_comment_count_bulk(context: Any, **extra: Any) -> dict[str, Any]:
    return _build(context, W.WIDGETS["comment_count_bulk"], {}, None, extra)


@register.inclusion_tag("fastcomments/count_marker.html")
def fastcomments_count_marker(url_id: Any = None, url: Any = None) -> dict[str, Any]:
    """Emit a marker span that {% fastcomments_comment_count_bulk %} fills in."""
    return {"url_id": url_id or url}


@register.inclusion_tag("fastcomments/widget.html", takes_context=True)
def fastcomments_collab_chat(
    context: Any,
    target: str,
    url_id: Any = None,
    url: Any = None,
    readonly: Any = None,
    locale: Any = None,
    has_dark_background: Any = None,
    default_sort_direction: Any = None,
    user: Any = None,
    **extra: Any,
) -> dict[str, Any]:
    kwargs = {
        "url_id": url_id,
        "url": url,
        "readonly": readonly,
        "locale": locale,
        "has_dark_background": has_dark_background,
        "default_sort_direction": default_sort_direction,
    }
    return _build(context, W.WIDGETS["collab_chat"], kwargs, _current_user(context, user), extra, target=target)


@register.inclusion_tag("fastcomments/widget.html", takes_context=True)
def fastcomments_image_chat(
    context: Any,
    target: str,
    url_id: Any = None,
    url: Any = None,
    readonly: Any = None,
    locale: Any = None,
    has_dark_background: Any = None,
    default_sort_direction: Any = None,
    chat_square_percentage: Any = None,
    user: Any = None,
    **extra: Any,
) -> dict[str, Any]:
    kwargs = {
        "url_id": url_id,
        "url": url,
        "readonly": readonly,
        "locale": locale,
        "has_dark_background": has_dark_background,
        "default_sort_direction": default_sort_direction,
        "chat_square_percentage": chat_square_percentage,
    }
    return _build(context, W.WIDGETS["image_chat"], kwargs, _current_user(context, user), extra, target=target)


@register.inclusion_tag("fastcomments/widget.html", takes_context=True)
def fastcomments_recent_comments(
    context: Any, url_id: Any = None, count: Any = None, has_dark_background: Any = None, **extra: Any
) -> dict[str, Any]:
    kwargs = {"url_id": url_id, "count": count, "has_dark_background": has_dark_background}
    return _build(context, W.WIDGETS["recent_comments"], kwargs, None, extra)


@register.inclusion_tag("fastcomments/widget.html", takes_context=True)
def fastcomments_recent_discussions(
    context: Any, count: Any = None, has_dark_background: Any = None, **extra: Any
) -> dict[str, Any]:
    kwargs = {"count": count, "has_dark_background": has_dark_background}
    return _build(context, W.WIDGETS["recent_discussions"], kwargs, None, extra)


@register.inclusion_tag("fastcomments/widget.html", takes_context=True)
def fastcomments_reviews_summary(
    context: Any, url_id: Any = None, has_dark_background: Any = None, **extra: Any
) -> dict[str, Any]:
    kwargs = {"url_id": url_id, "has_dark_background": has_dark_background}
    return _build(context, W.WIDGETS["reviews_summary"], kwargs, None, extra)


@register.inclusion_tag("fastcomments/widget.html", takes_context=True)
def fastcomments_top_pages(context: Any, has_dark_background: Any = None, **extra: Any) -> dict[str, Any]:
    kwargs = {"has_dark_background": has_dark_background}
    return _build(context, W.WIDGETS["top_pages"], kwargs, None, extra)


@register.inclusion_tag("fastcomments/widget.html", takes_context=True)
def fastcomments_user_activity(
    context: Any, user_id: Any, locale: Any = None, has_dark_background: Any = None, user: Any = None, **extra: Any
) -> dict[str, Any]:
    kwargs = {"user_id": user_id, "locale": locale, "has_dark_background": has_dark_background}
    return _build(context, W.WIDGETS["user_activity"], kwargs, _current_user(context, user), extra)
