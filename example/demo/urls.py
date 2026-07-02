from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path


def home(request):
    return render(request, "home.html", {"page_url_id": "django-demo"})


urlpatterns = [
    path("", home, name="home"),
    # Named so the widget's SSO login/logout fallback resolves.
    path("login/", lambda request: HttpResponse("This is where your login page would be."), name="login"),
    path("logout/", lambda request: HttpResponse("This is where your logout would happen."), name="logout"),
]
