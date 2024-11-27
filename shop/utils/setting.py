from datetime import timedelta
from django.core.cache import cache


def get_base_domain() -> str | None:
    """
    Получает базовый домен из настроек приложения. Результат кэшируется на 1 день.

    :return: Базовый домен, если найден, иначе None.
    """
    from shop.models import Setting, SettingChoices

    cache_key = "SETTING_BASE_DOMAIN_CACHE"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    base_domain_setting = Setting.objects.filter(
        predefined_key=SettingChoices.BASE_DOMAIN
    ).first()
    if base_domain_setting:
        data = getattr(base_domain_setting, "value_string")
        cache.set(cache_key, data, timeout=timedelta(days=1).seconds)
        return data

    return None


def get_shop_name() -> str | None:
    """
    Получает имя магазина из настроек приложения. Результат кэшируется на 1 день.

    :return: Имя магазина, если найдено, иначе None.
    """
    from shop.models import Setting, SettingChoices

    cache_key = "SETTING_SHOP_NAME_CACHE"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    shop_name_setting = Setting.objects.filter(
        predefined_key=SettingChoices.SHOP_NAME
    ).first()
    if shop_name_setting:
        data = getattr(shop_name_setting, "value_string")
        cache.set(cache_key, data, timeout=timedelta(days=1).seconds)
        return data

    return None
