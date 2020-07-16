from django.contrib.auth.models import User
from rest_framework import serializers
from tanukai.models import UserTag, UploadedImage, UserPartition, UserRating, Settings


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'email']


class UserTagSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)

    class Meta:
        model = UserTag
        fields = ('user', 'tag', 'tag_type')


class UploadedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ('pk', 'uploader', 'image', 'created_at')


class UserPartitionsSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        old_partitions = {key: value.partition for key, value in enumerate(instance)}
        new_partitions = {key: value.get('partition') for key, value in enumerate(validated_data)}

        return_data = []

        for index, old_partition in old_partitions.items():
            if old_partition not in new_partitions.values():
                instance[index].delete()
        for index, new_partition in new_partitions.items():
            if new_partition not in old_partitions.values():
                return_data.append(self.child.create(validated_data[index]))

        return return_data


class UserPartitionSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)

    class Meta:
        model = UserPartition
        fields = ('user', 'partition')
        list_serializer_class = UserPartitionsSerializer


class UserRatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)

    class Meta:
        model = UserRating
        fields = ('user', 'rating')


class SettingsSerializer(serializers.Serializer):
    partitions = serializers.DictField()
    rating = serializers.CharField()
    user = UserSerializer(required=False)

    def create(self, validated_data):
        partitions = validated_data.get('partitions')
        rating = validated_data.get('rating')
        for partition in partitions:
            UserPartition.objects.create(partition=partition, user=validated_data.get('user'))
        UserRating.objects.create(rating=rating, user=validated_data.get('user'))
        return Settings(partitions=partitions, rating=rating)


class SimilarImageDataSerializer(serializers.Serializer):
    image_path = serializers.CharField()
    source_created_at = serializers.DateTimeField()
    source_description = serializers.CharField(required=False)
    source_id = serializers.CharField()
    source_image_url = serializers.CharField()
    source_rating = serializers.CharField()
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
