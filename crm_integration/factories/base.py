from importlib import import_module


class BaseFactory:
    @classmethod
    def import_class(cls, path: str) -> object:
        module_path, class_name = path.rsplit(".", 1)
        crm_module = import_module(module_path)
        class_ = getattr(crm_module, class_name)
        return class_
