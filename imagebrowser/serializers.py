from rest_framework import serializers
from imagebrowser.models import UserTag, UploadedImage


class UserTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTag
        fields = ('user', 'tag', 'tag_type')


class UploadedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ('pk', 'uploader', 'image', 'created_at')


class SimilarImageDataSerializer(serializers.Serializer):
    # hash = serializers.DictField()
    image_path = serializers.CharField()
    source_created_at = serializers.DateTimeField()
    source_description = serializers.CharField(required=False)
    source_id = serializers.CharField()
    source_image_url = serializers.CharField()
    source_rating = serializers.CharField()
    # source_tags = serializers.DictField()
    source_url = serializers.CharField()
    source_website = serializers.CharField()
    timestamp = serializers.DateTimeField()


class SimilarImageSerializer(serializers.Serializer):
    distance = serializers.FloatField()
    id = serializers.FloatField()
    path = serializers.CharField()
    thumbnail_path = serializers.CharField()
    data = SimilarImageDataSerializer()


class ImageSearchResultsSerializer(serializers.Serializer):
    uploaded_image = UploadedImageSerializer(required=False)
    similar_images = SimilarImageSerializer(many=True)
