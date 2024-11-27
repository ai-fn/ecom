import subprocess
from django.core.management import BaseCommand
from django.core.management.base import CommandError


class Command(BaseCommand):
    """
    Django management команда для автоматической перестройки индексов Elasticsearch без интерактивного подтверждения.

    Использует команду `search_index --rebuild` для удаления и пересоздания индексов.
    """

    help = 'Rebuild Elasticsearch indexes without interactive confirmation'

    def handle(self, *args, **options):
        """
        Выполняет перестройку индексов Elasticsearch.

        :param args: Дополнительные позиционные аргументы.
        :param options: Дополнительные именованные аргументы.
        :raises CommandError: В случае ошибки выполнения команды `search_index --rebuild`.
        """

        try:
            # Запускает команду `search_index --rebuild` в дочернем процессе и передает подтверждение 'y'.
            result = subprocess.run(
                ['python', 'manage.py', 'search_index', '--rebuild'],
                input='y', text=True, capture_output=True, check=True
            )
            self.stdout.write(self.style.SUCCESS('Successfully rebuilt Elasticsearch indexes'))
            self.stdout.write(result.stdout)
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"Error rebuilding Elasticsearch indexes: {e.stderr}"))
            raise CommandError(f"Error rebuilding Elasticsearch indexes: {e.stderr}")
