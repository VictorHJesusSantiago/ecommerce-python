from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run generate_sitemaps'

    def handle(self, *args, **options):
        self.stdout.write('Running generate_sitemaps...')
