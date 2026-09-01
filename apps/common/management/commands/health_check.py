from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run health_check'

    def handle(self, *args, **options):
        self.stdout.write('Running health_check...')
