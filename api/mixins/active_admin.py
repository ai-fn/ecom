class ActiveAdminMixin:
    """
    Mixin для добавления поля `is_active` в `list_filter` и `list_display` администратора,
    если модель содержит это поле.
    """

    def __init__(self, *args, **kwargs) -> None:
        """
        Инициализация миксина.

        Если у модели есть поле `is_active`, оно автоматически добавляется
        в `list_filter` и `list_display`.

        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        """

        super().__init__(*args, **kwargs)
        if hasattr(self.model, "is_active"):
            for field in ("list_filter", "list_display"):
                value = getattr(self, field, tuple())
                if "is_active" not in value:
                    setattr(self, field, (*value, "is_active"))
