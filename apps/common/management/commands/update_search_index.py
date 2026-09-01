from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run update_search_index'

    def handle(self, *args, **options):
        self.stdout.write('Running update_search_index...')
