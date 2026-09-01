from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run seed_data'

    def handle(self, *args, **options):
        self.stdout.write('Running seed_data...')
