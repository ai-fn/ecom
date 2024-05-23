import subprocess
from django.core.management import BaseCommand
from django.core.management.base import CommandError


class Command(BaseCommand):
    help = 'Rebuild Elasticsearch indexes without interactive confirmation'

    def handle(self, *args, **options):
        try:
            # Run the `search_index --rebuild` command in a subprocess and simulate 'yes' input
            result = subprocess.run(
                ['python', 'manage.py', 'search_index', '--rebuild'],
                input='y', text=True, capture_output=True, check=True
            )
            self.stdout.write(self.style.SUCCESS('Successfully rebuilt Elasticsearch indexes'))
            self.stdout.write(result.stdout)
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"Error rebuilding Elasticsearch indexes: {e.stderr}"))
            raise CommandError(f"Error rebuilding Elasticsearch indexes: {e.stderr}")
