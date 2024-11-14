from django.conf import settings
from crm_integration.factories import BaseFactory


class CRMFactory(BaseFactory):
    @classmethod
    def get_crm_adapter(cls, crm_name: str = None):
        path_to_crm_class = settings.CRM_ADAPTERS[crm_name]
        return cls.import_class(path_to_crm_class)
