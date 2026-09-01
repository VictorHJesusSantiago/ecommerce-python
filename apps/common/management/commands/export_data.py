from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run export_data'

    def handle(self, *args, **options):
        self.stdout.write('Running export_data...')
