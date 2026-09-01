from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run generate_thumbnails'

    def handle(self, *args, **options):
        self.stdout.write('Running generate_thumbnails...')
