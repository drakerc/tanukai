from dataclasses import dataclass
from typing import List, Optional
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from tanukai.validators import validate_max_image_size


class UserTag(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tag = models.CharField("Tag", max_length=200)
    tag_type = models.CharField('Tag type', max_length=20)


class UploadedImage(models.Model):
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    features = models.BinaryField()
    image = models.ImageField(
        upload_to='uploaded/',
        max_length=500,
        validators=[validate_max_image_size]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    private_image = models.BooleanField(default=False)


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
