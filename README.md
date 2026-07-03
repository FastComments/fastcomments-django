# fastcomments-django

FastComments for Django: embed the FastComments widgets and sign Secure SSO
with template tags. This is the Django sibling of the
[FastComments Laravel package](https://github.com/FastComments/fastcomments-laravel).

Widget embedding and SSO signing are handled through the
[FastComments Python SDK](https://github.com/fastcomments/fastcomments-python),
so the crypto and REST calls share one source of truth.

## Requirements

- Python 3.10+
- Django 4.2, 5.0, 5.1, or 5.2
- A FastComments tenant ID (use `demo` to try it without an account)
- An API secret is required only for Secure SSO

## Installation

Install from a release tag (this project is distributed via git tags, not PyPI):

```bash
pip install "git+https://github.com/fastcomments/fastcomments-django.git@v0.1.0"
```

For server-side REST access (the `admin()` / `public_api()` helpers), add the
`api` extra, which pulls in the SDK's generated client:

```bash
pip install "fastcomments-django[api] @ git+https://github.com/fastcomments/fastcomments-django.git@v0.1.0"
```

Add the app to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "fastcomments_django",
]
```

## Quickstart

Configure your tenant in `settings.py`:

```python
import os

FASTCOMMENTS = {
    "TENANT_ID": os.environ.get("FASTCOMMENTS_TENANT_ID", "demo"),
}
```

Drop the widget into any template:

```django
{% load fastcomments %}

{% fastcomments url_id="my-page" %}
```

## Prerequisites for automatic SSO

To pass the logged-in user to the widget automatically, the tags read the
current user from the request. Make sure your project has both of these (they
are on by default in a standard Django project):

- `django.template.context_processors.request` in `TEMPLATES["OPTIONS"]["context_processors"]`
- `django.contrib.auth.middleware.AuthenticationMiddleware` in `MIDDLEWARE`

Without a request in the template context, widgets render for an anonymous
visitor. You can always pass a user explicitly: `{% fastcomments user=some_user %}`.

## Widget tags

Every widget has its own tag. All of them accept `**extra` keyword arguments,
which are merged into the widget config as-is (use camelCase keys) for anything
not covered by the named arguments below.

| Tag | Widget |
|---|---|
| `{% fastcomments %}` | Comments |
| `{% fastcomments_live_chat %}` | Live chat |
| `{% fastcomments_comment_count %}` | Comment count badge |
| `{% fastcomments_comment_count_bulk %}` + `{% fastcomments_count_marker %}` | Bulk comment counts |
| `{% fastcomments_collab_chat target="#el" %}` | Collaborative (inline) chat |
| `{% fastcomments_image_chat target="#el" %}` | Image annotation chat |
| `{% fastcomments_recent_comments %}` | Recent comments |
| `{% fastcomments_recent_discussions %}` | Recent discussions |
| `{% fastcomments_reviews_summary %}` | Reviews summary |
| `{% fastcomments_top_pages %}` | Most-discussed pages |
| `{% fastcomments_user_activity user_id="..." %}` | A user's activity feed |

Named arguments map to the widget's camelCase config keys:

| Argument | Config key | Tags |
|---|---|---|
| `url_id` | `urlId` | comments, live chat, comment count, collab/image chat, recent comments, reviews summary |
| `url` | `url` | comments, live chat, collab/image chat |
| `readonly` | `readonly` | comments, live chat, collab/image chat |
| `locale` | `locale` | comments, live chat, collab/image chat, user activity |
| `has_dark_background` | `hasDarkBackground` | all |
| `default_sort_direction` | `defaultSortDirection` | comments, live chat, collab/image chat |
| `number_only` | `numberOnly` | comment count |
| `is_live` | `isLive` | comment count |
| `count` | `count` | recent comments, recent discussions |
| `target` | (querySelector, not sent) | collab chat, image chat |
| `chat_square_percentage` | `chatSquarePercentage` | image chat |
| `user_id` | `userId` | user activity |

Examples:

```django
{% load fastcomments %}

{% fastcomments url_id="my-page" locale="en_us" default_sort_direction="MR" %}

{% fastcomments_live_chat url_id="room-1" %}

Comments: {% fastcomments_comment_count url_id="my-page" number_only=True %}

{# Collab chat attaches to an existing element on the page #}
<article id="post-body">...</article>
{% fastcomments_collab_chat target="#post-body" %}

{# Bulk counts: place markers, then one bulk loader fills them all in #}
{% for post in posts %}
    <a href="{{ post.url }}">{{ post.title }}</a>
    {% fastcomments_count_marker url_id=post.url_id %}
{% endfor %}
{% fastcomments_comment_count_bulk %}
```

## SSO (Single Sign-On)

Enable SSO and choose a mode in `settings.py`. Secure SSO signs the user
server-side with HMAC-SHA256 using your API secret and is recommended.

```python
FASTCOMMENTS = {
    "TENANT_ID": os.environ["FASTCOMMENTS_TENANT_ID"],
    "API_KEY": os.environ["FASTCOMMENTS_API_KEY"],   # your API secret; signs Secure SSO
    "SSO": {
        "ENABLED": True,
        "MODE": "secure",                            # "secure" | "simple"
        # Map FastComments fields to your user model. Values may be an attribute
        # name, a dotted path ("profile.avatar_url"), a callable(user), or None.
        "USER_MAP": {
            "id": "id",
            "email": "email",
            "username": "username",
            "avatar": None,
            "display_name": None,
            "website_url": None,
        },
        "IS_ADMIN": lambda user: user.is_staff,      # callable(user) -> bool, or dotted path
        "IS_MODERATOR": None,
        "GROUP_IDS": None,                           # callable(user) -> list, or dotted path
    },
}
```

SSO is injected automatically into `{% fastcomments %}`, `{% fastcomments_live_chat %}`,
`{% fastcomments_collab_chat %}`, `{% fastcomments_image_chat %}`, and
`{% fastcomments_user_activity %}` for the current user.

Login/logout URLs shown to signed-out visitors default to `reverse("login")` /
`reverse("logout")`; override them with `SSO["LOGIN_URL"]` / `SSO["LOGOUT_URL"]`.

### Custom mapping

Two higher-precedence options beat `USER_MAP`:

- **A method on your user model** (the Pythonic analog of an interface):

  ```python
  class User(AbstractUser):
      def to_fastcomments_user_data(self):
          return {"id": self.pk, "email": self.email, "username": self.get_username()}
  ```

- **A global mapper**, a dotted path to `callable(user) -> dict`:

  ```python
  FASTCOMMENTS = {"SSO": {"USER_MAPPER": "myapp.sso.map_user"}}
  ```

Precedence is `USER_MAPPER` > `to_fastcomments_user_data()` > `USER_MAP`.

## Server-side API access

With the `[api]` extra installed, call the FastComments REST API through the SDK,
pre-configured with your API key and region:

```python
from fastcomments_django import admin, public_api, get_manager

admin().get_comments("YOUR_TENANT_ID", ...)     # authenticated (DefaultApi)
public_api().get_comments_public(...)            # public (PublicApi)

# Generate an SSO token for API calls or client hand-off:
token = get_manager().sso().token_for(request.user)
```

## EU region

Set `REGION` to route the widgets and API to the EU:

```python
FASTCOMMENTS = {"TENANT_ID": "...", "REGION": "eu"}
```

## Customizing the embed markup

Override `fastcomments/widget.html` by placing your own copy earlier on the
template search path (a project `templates/fastcomments/widget.html`). This is
the Django analog of Laravel's `vendor:publish --tag=fastcomments-views`.

## Settings reference

| Key | Default | Description |
|---|---|---|
| `TENANT_ID` | `""` | Your FastComments tenant ID (`demo` for testing). |
| `API_KEY` | `""` | Your API secret. Signs Secure SSO and authenticates `admin()`. |
| `REGION` | `None` | `None` for US, `"eu"` for the EU region. |
| `SSO.ENABLED` | `False` | Turn SSO on. |
| `SSO.MODE` | `"secure"` | `"secure"` (HMAC) or `"simple"` (unsigned). |
| `SSO.LOGIN_URL` / `SSO.LOGOUT_URL` | `None` | Shown to signed-out visitors; default to `reverse("login"/"logout")`. |
| `SSO.USER_MAP` | id/email/username | FastComments field to user attribute/path/callable. |
| `SSO.IS_ADMIN` / `IS_MODERATOR` / `GROUP_IDS` | `None` | `callable(user)` or dotted path. |
| `SSO.USER_MAPPER` | `None` | Dotted path to `callable(user) -> dict`; highest precedence. |
| `WIDGET_DEFAULTS` | `{}` | Config merged into every widget (camelCase keys). |

## Example project

A runnable project lives in [`example/`](./example) that renders every widget,
with the comment and live-chat widgets authenticated via **Secure SSO** (it
signs in a demo user for you). From that directory:

```bash
python manage.py migrate
# Use your own tenant to see Secure SSO in action (an API secret enables it):
FASTCOMMENTS_TENANT_ID=... FASTCOMMENTS_API_KEY=... python manage.py runserver
```

Without an API secret it falls back to the public `demo` tenant (anonymous).
[`example/browser_smoke.py`](./example/browser_smoke.py) is a Playwright e2e
that loads the page in a real browser and posts a comment as the Secure-SSO
user.

## Development

```bash
pip install -e ".[dev]"
# Point at your local SDK checkout so `sso` is importable:
pip install -e ../fastcomments-python
pytest
```

## License

MIT
