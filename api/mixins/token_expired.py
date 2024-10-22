import time
from typing import Any, Dict

from django.conf import settings


class TokenExpiredTimeMixin:

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)
        data = self._set_time_fields(data)
        return data

    @staticmethod
    def _set_time_fields(data: dict) -> dict:
        data["access_expired_at"] = (
            time.time() + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
        )
        data["refresh_expired_at"] = (
            time.time() + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
        )
        return data
