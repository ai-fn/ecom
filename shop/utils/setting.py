from datetime import timedelta
from shop.models import Setting, SettingChoices
from django.core.cache import cache


def get_base_domain() -> str | None:
    cache_key = "SETTING_BASE_DOMAIN_CACHE"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    else:
        if base_domain_setting := Setting.objects.filter(predefined_key=SettingChoices.BASE_DOMAIN).first():
            data = getattr(base_domain_setting, "value_string")
            cache.set(cache_key, data, timeout=timedelta(days=1).seconds)
            return data

    return None
