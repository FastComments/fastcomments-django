"""Registry of the embeddable FastComments widgets.

Each ``WidgetSpec`` maps a template tag to its CDN script, global constructor,
mount archetype, and the snake_case tag kwargs it forwards (as camelCase) into
the widget config. Verified against fastcomments/public/js/*.min.js.
"""

from dataclasses import dataclass, field

# Mount archetypes:
#   container -> window.NAME(el, config) onto a div/span we render.
#   selector  -> window.NAME(document.querySelector(target), config); no container.
#   bulk      -> window.NAME(config) with no element; scans marker spans on the page.
MOUNT_CONTAINER = "container"
MOUNT_SELECTOR = "selector"
MOUNT_BULK = "bulk"


@dataclass(frozen=True)
class WidgetSpec:
    name: str
    script_path: str
    constructor: str
    mount_type: str = MOUNT_CONTAINER
    container_tag: str = "div"
    id_prefix: str = "fc-"
    takes_sso: bool = False
    use_callback: bool = False
    # snake_case tag kwarg -> camelCase widget-config key
    kwarg_map: tuple[tuple[str, str], ...] = field(default_factory=tuple)


# Config kwargs shared by the EmbedCore comment-style widgets.
_COMMENT_KWARGS = (
    ("url_id", "urlId"),
    ("url", "url"),
    ("readonly", "readonly"),
    ("locale", "locale"),
    ("has_dark_background", "hasDarkBackground"),
    ("default_sort_direction", "defaultSortDirection"),
)

WIDGETS: dict[str, WidgetSpec] = {
    "comments": WidgetSpec(
        name="comments",
        script_path="/js/embed-v2.min.js",
        constructor="FastCommentsUI",
        id_prefix="fc-",
        takes_sso=True,
        kwarg_map=_COMMENT_KWARGS,
    ),
    "live_chat": WidgetSpec(
        name="live_chat",
        script_path="/js/embed-live-chat.min.js",
        constructor="FastCommentsLiveChat",
        id_prefix="fc-live-chat-",
        takes_sso=True,
        kwarg_map=_COMMENT_KWARGS,
    ),
    "comment_count": WidgetSpec(
        name="comment_count",
        script_path="/js/widget-comment-count.min.js",
        constructor="FastCommentsCommentCount",
        container_tag="span",
        id_prefix="fc-count-",
        kwarg_map=(
            ("url_id", "urlId"),
            ("number_only", "numberOnly"),
            ("is_live", "isLive"),
            ("has_dark_background", "hasDarkBackground"),
        ),
    ),
    "comment_count_bulk": WidgetSpec(
        name="comment_count_bulk",
        script_path="/js/widget-comment-count-bulk.min.js",
        constructor="FastCommentsCommentCountBulk",
        mount_type=MOUNT_BULK,
        id_prefix="fc-count-bulk-",
    ),
    "collab_chat": WidgetSpec(
        name="collab_chat",
        script_path="/js/embed-collab-chat.min.js",
        constructor="FastCommentsCollabChat",
        mount_type=MOUNT_SELECTOR,
        id_prefix="fc-collab-chat-",
        takes_sso=True,
        kwarg_map=_COMMENT_KWARGS,
    ),
    "image_chat": WidgetSpec(
        name="image_chat",
        script_path="/js/embed-image-chat.min.js",
        constructor="FastCommentsImageChat",
        mount_type=MOUNT_SELECTOR,
        id_prefix="fc-image-chat-",
        takes_sso=True,
        kwarg_map=_COMMENT_KWARGS + (("chat_square_percentage", "chatSquarePercentage"),),
    ),
    "recent_comments": WidgetSpec(
        name="recent_comments",
        script_path="/js/widget-recent-comments-v2.min.js",
        constructor="FastCommentsRecentCommentsV2",
        id_prefix="fc-recent-comments-",
        kwarg_map=(
            ("url_id", "urlId"),
            ("count", "count"),
            ("has_dark_background", "hasDarkBackground"),
        ),
    ),
    "recent_discussions": WidgetSpec(
        name="recent_discussions",
        script_path="/js/widget-recent-discussions-v2.min.js",
        constructor="FastCommentsRecentDiscussionsV2",
        id_prefix="fc-recent-discussions-",
        kwarg_map=(
            ("count", "count"),
            ("has_dark_background", "hasDarkBackground"),
        ),
    ),
    "reviews_summary": WidgetSpec(
        name="reviews_summary",
        script_path="/js/embed-reviews-summary.min.js",
        constructor="FastCommentsReviewsSummaryWidget",
        id_prefix="fc-rs-",
        kwarg_map=(
            ("url_id", "urlId"),
            ("has_dark_background", "hasDarkBackground"),
        ),
    ),
    "top_pages": WidgetSpec(
        name="top_pages",
        script_path="/js/widget-top-pages-v2.min.js",
        constructor="FastCommentsTopPagesV2",
        id_prefix="fc-top-pages-",
        kwarg_map=(("has_dark_background", "hasDarkBackground"),),
    ),
    "user_activity": WidgetSpec(
        name="user_activity",
        script_path="/js/embed-user-activity.min.js",
        constructor="FastCommentsUserActivity",
        id_prefix="fc-activity-",
        takes_sso=True,
        use_callback=True,
        kwarg_map=(
            ("user_id", "userId"),
            ("locale", "locale"),
            ("has_dark_background", "hasDarkBackground"),
        ),
    ),
}
