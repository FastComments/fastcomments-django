from django.contrib.auth import get_user_model, login
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path


def home(request):
    # Example convenience: sign in a demo user so the widgets render with
    # Secure SSO. A real app performs its own authentication here; whoever
    # request.user is, the plugin signs their identity server-side.
    if not request.user.is_authenticated:
        User = get_user_model()
        user, _ = User.objects.get_or_create(
            username="demo_user",
            defaults={"email": "demo_user@example.com", "first_name": "Demo"},
        )
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return render(request, "home.html", {"page_url_id": "django-demo"})


urlpatterns = [
    path("", home, name="home"),
    # Named so the widget's Secure SSO login/logout fallback resolves.
    path("login/", lambda request: HttpResponse("This is where your login page would be."), name="login"),
    path("logout/", lambda request: HttpResponse("This is where your logout would happen."), name="logout"),
]
