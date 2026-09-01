from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run send_notifications'

    def handle(self, *args, **options):
        self.stdout.write('Running send_notifications...')
