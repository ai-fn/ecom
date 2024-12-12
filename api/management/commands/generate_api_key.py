
from api.models import ApiKey

from django.core.management import BaseCommand
from django.core.management.base import CommandParser


class Command(BaseCommand):
    help = 'Создает новый API ключ'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--client-id', type=str, help='Идентификатор клиента', required=True)
        parser.add_argument('--api-key', type=str, help='API ключ', required=True)

    def handle(self, *args, **kwargs):
        client_id_value = kwargs['client_id']
        raw_api_key = kwargs['api_key']

        if not raw_api_key:
            raise ValueError(f"'api_key' value must be not null.")

        api_key = ApiKey(client_id=client_id_value)
        api_key.set_api_key(raw_api_key)
        api_key.save()

        self.stdout.write(self.style.SUCCESS(f'API ключ #{api_key.id} успешно создан для клиента "{client_id_value}".'))
