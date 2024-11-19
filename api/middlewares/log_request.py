import os

from django.conf import settings
from loguru import logger
from django.utils.timezone import now


class LogRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        log_path = os.path.join(settings.BASE_DIR, "logs", "request_logs.log")
        logger.add(log_path, rotation="500 MB", level="INFO", format="{time} {level} {message}")

    def __call__(self, request):
        exclude_logs_paths = (
            "/metrics",
        )
        if request.path in exclude_logs_paths:
            return self.get_response(request)

        ip = self.get_client_ip(request)
        timestamp = now().strftime('%Y-%m-%d %H:%M:%S')

        response = self.get_response(request)

        logger.info(f'{timestamp} | {ip} | {request.path} | {response.status_code}')

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
