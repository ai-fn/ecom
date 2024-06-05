from loguru import logger

from django.views import View

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.status import HTTP_403_FORBIDDEN


def closed_view(func):
    def inner(*args, **kwargs):
        try:
            request = None
            view_class = None
            for arg in args:
                if isinstance(arg, View):
                    view_class = arg
                if isinstance(arg, Request):
                    request = arg
                    break
            
            view_name = f"{view_class.__class__.__name__}.{func.__name__}" if view_class else func.__name__
            if request is None:
                logger.error(f"Request object not found in arguments: {args, kwargs}\nRequest for func {view_name}")
                raise ValueError("Request object not found in arguments")
        except Exception as e:
            return Response({"error": str(e)}, status=HTTP_403_FORBIDDEN)
        
        ip = request.META.get('REMOTE_ADDR')
        if ip.startswith(("192.168.", "172.16.", "10.", "172.18.")):

            logger.info(f"Closed view {view_name} requested by {ip}.")
            return func(*args, **kwargs)

        logger.info(f"Closed view {view_name} requested by {ip}.")
        return Response({"error": "Access denied"}, status=HTTP_403_FORBIDDEN) 
    return inner
