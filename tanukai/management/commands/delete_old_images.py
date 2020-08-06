from datetime import timedelta, datetime
from django.core.management.base import BaseCommand
from tanukai.models import UploadedImage


class Command(BaseCommand):
    help = 'Deletes images older than 30 minutes old'

    def handle(self, *args, **options):
        # TODO: move the 30-minutes constant to a config file
        maximum_created_at = datetime.now() - timedelta(minutes=30)
        old_images = UploadedImage.objects.filter(created_at__lt=maximum_created_at)
        for image in old_images:
            if image.image:
                image.image.delete()
            image.delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {len(old_images)} images'))
