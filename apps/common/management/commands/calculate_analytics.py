from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run calculate_analytics'

    def handle(self, *args, **options):
        self.stdout.write('Running calculate_analytics...')
