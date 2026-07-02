"""Named login/logout routes so SSO's reverse() fallback resolves in tests."""

from django.http import HttpResponse
from django.urls import path

urlpatterns = [
    path("login/", lambda request: HttpResponse("login"), name="login"),
    path("logout/", lambda request: HttpResponse("logout"), name="logout"),
]
