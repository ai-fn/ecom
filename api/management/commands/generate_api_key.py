
from api.models import ApiKey

from django.core.management import BaseCommand
from django.core.management.base import CommandParser


class Command(BaseCommand):
    help = 'Создает новый API ключ'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--client-id', type=str, help='Идентификатор клиента')

    def handle(self, *args, **kwargs):
        client_id_value = kwargs['client_id']

        api_key = ApiKey(client_id=client_id_value)
        api_key._set_api_key()
        api_key.save()

        self.stdout.write(self.style.SUCCESS(f'API ключ #{api_key.id} успешно создан для клиента "{client_id_value}".'))
