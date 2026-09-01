from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run import_data'

    def handle(self, *args, **options):
        self.stdout.write('Running import_data...')
