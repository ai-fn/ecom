from api.models import ApiKey
from django.conf import settings


def send_request(func, *args, headers: dict = None, **kwargs):
    host = ",".join(settings.ALLOWED_HOSTS)

    if not headers:
        headers = dict()

    try:
        api_key = ApiKey.objects.get(client_id=456782)
    except ApiKey.DoesNotExist:
        api_key = ApiKey(client_id=456782, allowed_hosts=host)
        api_key._set_api_key()
        api_key.save()

    try:
        headers["Host"] = settings.ALLOWED_HOSTS[0]
    except IndexError:
        pass

    headers["X-Api-Key"] = api_key.key
    return func(*args, headers=headers, **kwargs)
