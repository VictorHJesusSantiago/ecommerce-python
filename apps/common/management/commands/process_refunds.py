from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run process_refunds'

    def handle(self, *args, **options):
        self.stdout.write('Running process_refunds...')
