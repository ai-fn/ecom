from crm_integration.adapters import CRMAdapter


class CRMFactory:

    @classmethod
    def get_adapter(cls, name: str) -> CRMAdapter:
        return CRMAdapter._register_crm[name]()
