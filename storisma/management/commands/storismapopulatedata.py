from django.core.management.base import BaseCommand
from storisma.models import populate_models_from_data


class Command(BaseCommand):
    help = 'Populate StorismaCategory model with data from data.py'

    def handle(self, *args, **options):
        populate_models_from_data()
        self.stdout.write(self.style.SUCCESS('StorismaCategory model populated successfully'))