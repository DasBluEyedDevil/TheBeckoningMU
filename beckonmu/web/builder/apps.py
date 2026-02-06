from django.apps import AppConfig


class BuilderConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "web.builder"
    label = "builder"
    verbose_name = "Web Builder"
