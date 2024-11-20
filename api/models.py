import re
import hashlib
from time import time

from datetime import timedelta

from django.db import models
from django.conf import settings
from django.core.cache import cache
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from account.models import TimeBasedModel


class ApiKey(TimeBasedModel):

    key = models.CharField(_("API ключ"), max_length=512, unique=True)
    client_id = models.PositiveBigIntegerField(_("ID клиента"), unique=True)
    allowed_hosts = models.TextField(_("Разрешённые хосты"), help_text="Список разрешенных хостов, разделённых запятой", default="localhost")
    allowed_ips = models.TextField(_("Разрешённые ip адреса"), help_text="Список разрешенных ip адресов, разделённых запятой", blank=True, null=True)
    expires_at = models.DateTimeField(_("Дата истечения ключа"), default=now() + timedelta(days=365))

    class Meta:
        verbose_name = _("API Ключ")
        verbose_name_plural = _("API Ключи")
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"API ключ #{self.id}"

    def set_expires_at(self, expiration_time: timedelta = timedelta(days=365)) -> "ApiKey":
        self.expires_at = now() + expiration_time
        return self
    
    def is_valid(self):
        return self.is_active and now() < self.expires_at

    def is_host_allowed(self, host: str) -> bool:
        if not self.allowed_hosts or self.allowed_hosts == "*":
            return True

        if not host:
            return False

        allowed_hosts_list = self.allowed_hosts.split(",")
        for pattern in allowed_hosts_list:
            if re.match(pattern.strip(), host.strip()):
                return True

        return False

    def is_ip_allowed(self, ip: str) -> bool:
        if not self.allowed_ips or self.allowed_ips == "*":
            return True

        if not ip:
            return False

        allowed_ips_list = self.allowed_ips.split(",")
        for pattern in allowed_ips_list:
            if re.match(pattern.strip(), ip.strip()):
                return True

        return False
    
    def _set_api_key(self) -> "ApiKey":
        self.key = hashlib.sha256(f"{settings.SECRET_KEY}{time()}{self.client_id}".encode()).hexdigest()
        return self

    @classmethod
    def get_cache_key(cls, key: str) -> str:
        return f"CACHE_API_KEY_{key}"
    
    def _invalidate_cache(self) -> None:
        cache_key = self.get_cache_key(self.key)
        cache.delete(cache_key)

    def save(self, *args, update_fields=None, **kwargs) -> None:
        if self.id:
            self._invalidate_cache()

        return super().save(*args, update_fields=update_fields, **kwargs)
