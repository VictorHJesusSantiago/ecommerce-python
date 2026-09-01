from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run update_inventory'

    def handle(self, *args, **options):
        self.stdout.write('Running update_inventory...')
