from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run check_stock_levels'

    def handle(self, *args, **options):
        self.stdout.write('Running check_stock_levels...')
