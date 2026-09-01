from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run restore_database'

    def handle(self, *args, **options):
        self.stdout.write('Running restore_database...')
