from dataclasses import dataclass
from typing import List, Optional
from django.conf import settings
from django.db import models


class UserTag(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tag = models.CharField("Tag", max_length=200)
    tag_type = models.CharField('Tag type', max_length=20)


class UploadedImage(models.Model):
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    features = models.BinaryField()
    image = models.FilePathField(path='static/uploaded/')
    created_at = models.DateTimeField(auto_now_add=True)


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
