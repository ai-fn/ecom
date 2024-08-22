class ActiveAdminMixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if hasattr(self.model, "is_active"):
            for field in ("list_filter", "list_display"):
                value = getattr(self, field, tuple())
                if "is_active" not in value:
                    setattr(self, field, (*value, "is_active"))
