from django.apps import AppConfig


class ImportAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'import_app'

    def ready(self) -> None:
        from . import signals
