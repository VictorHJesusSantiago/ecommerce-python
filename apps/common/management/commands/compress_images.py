from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run compress_images'

    def handle(self, *args, **options):
        self.stdout.write('Running compress_images...')
