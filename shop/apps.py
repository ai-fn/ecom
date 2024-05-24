from django.apps import AppConfig


class ShopConfig(AppConfig):
    name = 'shop'
    verbose_name = 'Каталог'

    def ready(self) -> None:
        import shop.signals
        
        return super().ready()