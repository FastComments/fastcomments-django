"""Settings for the FastComments Django example project.

Set FASTCOMMENTS_TENANT_ID (and optionally FASTCOMMENTS_API_KEY to enable SSO)
in the environment. Defaults to the public "demo" tenant, which works without
an account.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "example-insecure-key-do-not-use-in-production"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "fastcomments_django",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]

ROOT_URLCONF = "demo.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # Required so the widget tags can read the current user.
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
            ],
        },
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

STATIC_URL = "static/"
USE_TZ = True

# --- FastComments configuration ---------------------------------------------
FASTCOMMENTS = {
    "TENANT_ID": os.environ.get("FASTCOMMENTS_TENANT_ID", "demo"),
    "API_KEY": os.environ.get("FASTCOMMENTS_API_KEY", ""),
    "REGION": os.environ.get("FASTCOMMENTS_REGION") or None,
    "SSO": {
        # SSO is enabled automatically once an API key (secret) is provided.
        "ENABLED": bool(os.environ.get("FASTCOMMENTS_API_KEY")),
        "MODE": "secure",
    },
}
