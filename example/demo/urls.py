from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("w/<slug:key>/", views.widget, name="widget"),
    # Named "login"/"logout" so the widget's Secure SSO login/logout fallback resolves.
    path("signin/", views.signin, name="login"),
    path("signout/", views.signout, name="logout"),
]
