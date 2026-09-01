from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run cleanup_data'

    def handle(self, *args, **options):
        self.stdout.write('Running cleanup_data...')
