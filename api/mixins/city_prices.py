class CityPricesMixin:

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault("context", {})
        kwargs["context"]["city_domain"] = getattr(self, "domain", "")
        kwargs["context"]["request"] = getattr(self, "request", "")
        return super().get_serializer(*args, **kwargs)
