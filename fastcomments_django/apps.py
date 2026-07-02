from django.apps import AppConfig


class FastCommentsConfig(AppConfig):
    name = "fastcomments_django"
    verbose_name = "FastComments"

    def ready(self):
        # Import for their side effect: connecting the setting_changed receivers
        # that invalidate the cached config and manager under override_settings.
        from . import conf  # noqa: F401
        from . import api  # noqa: F401
