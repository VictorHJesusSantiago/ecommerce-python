from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run send_email_campaigns'

    def handle(self, *args, **options):
        self.stdout.write('Running send_email_campaigns...')
