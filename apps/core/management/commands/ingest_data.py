from django.core.management.base import BaseCommand
from apps.core.tasks import ingest_all_data


class Command(BaseCommand):
    help = 'Trigger background data ingestion from Excel files'

    def handle(self, *args, **options):
        result = ingest_all_data.delay()
        self.stdout.write(
            self.style.SUCCESS(
                f'Data ingestion triggered. Task ID: {result.id}'
            )
        )
