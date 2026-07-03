from django.apps import AppConfig


class FastCommentsConfig(AppConfig):
    name = "fastcomments_django"
    verbose_name = "FastComments"

    def ready(self) -> None:
        # Import for their side effect: connecting the setting_changed receivers
        # that invalidate the cached config and manager under override_settings.
        from . import api, conf  # noqa: F401
