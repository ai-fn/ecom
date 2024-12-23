from django.apps import AppConfig


class CrmIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crm_integration'

    def ready(self) -> None:
        import crm_integration.adapters
