import sys
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import List, Optional

import os
import requests
from PIL import Image
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.conf import settings

from tanukai.validators import validate_max_image_size


class UserTag(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tag = models.CharField("Tag", max_length=200)
    tag_type = models.CharField('Tag type', max_length=20)


class UploadedImage(models.Model):
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    features = models.BinaryField()
    image = models.ImageField(
        upload_to=settings.UPLOADS_URL,
        max_length=500,
        validators=[validate_max_image_size],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    private_image = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.image:
            return super(UploadedImage, self).save(*args, **kwargs)
        max_width = 500
        max_height = 500
        if self.image.width > max_width or self.image.width > max_height:
            if self.image.closed:
                self.image.open()
            image = Image.open(self.image)
            output = BytesIO()
            image.thumbnail((max_width, max_height), Image.ANTIALIAS)
            image = image.convert('RGB')
            image.save(output, format='JPEG', quality=90)
            self.image = InMemoryUploadedFile(
                output,
                'ImageField',
                f'{datetime.now()}_{self.image.name.split(".")[0]}.jpg',
                'image/jpeg',
                sys.getsizeof(output),
                None
            )
        super(UploadedImage, self).save(*args, **kwargs)


class URLUploadedFile(UploadedImage):
    image_url = models.CharField(max_length=1000)

    def fetch_and_save(self, *args, **kwargs):
        if self.image_url:
            response = requests.get(
                self.image_url,
                timeout=15,
                stream=True,
                headers={
                    'User-Agent': 'Tanukai.com'
                }
            )  # TODO: make sure it's an image file before requesting it
            if response.status_code != 200:
                raise ValidationError(f'Could not download the image from {self.image_url}.')
            self.image.save(
                os.path.basename(self.image_url),
                File(response.raw)
            )


class UserPartition(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    partition = models.CharField('Partition', max_length=50)


class UserRating(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    rating = models.CharField('Rating', default="safe", max_length=50)


@dataclass
class SimilarImage:
    distance: float
    id: int
    data: dict
    path: str
    thumbnail_path: str


@dataclass
class ImageSearchResults:
    similar_images: List[SimilarImage]
    uploaded_image: Optional[UploadedImage] = None


@dataclass
class Settings:
    partitions: dict
    rating: str
