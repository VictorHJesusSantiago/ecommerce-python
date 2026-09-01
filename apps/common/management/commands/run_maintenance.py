from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run run_maintenance'

    def handle(self, *args, **options):
        self.stdout.write('Running run_maintenance...')
