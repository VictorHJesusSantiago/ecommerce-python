from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run backup_database'

    def handle(self, *args, **options):
        self.stdout.write('Running backup_database...')
