import pickle
from datetime import datetime, timedelta

from PIL import Image
from rest_framework.exceptions import NotFound, ValidationError, NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from tanukai.services.img_match.tanukai_img_match import TanukaiImgMatch
from .models import UserTag, UploadedImage, ImageSearchResults, UserPartition, UserRating
from .serializers import UserTagSerializer, ImageSearchResultsSerializer, SettingsSerializer, \
    UserPartitionSerializer, UserRatingSerializer, UploadedImageSerializer
from rest_framework.parsers import MultiPartParser
from .models import SimilarImage

# TODO list:
#  add typehinting
#  move some custom image processing logic (uploading, saving etc) to a new service/package
#  move common code parts (business logic, validation, getting fields/imgs)
#  somewhere into just one place


def is_image_safe(maximum_rating: str, image_rating: str) -> bool:
    safety_mapping = {
        'safe': ['safe'],
        'questionable': ['safe', 'questionable'],
        'explicit': ['safe', 'questionable', 'explicit']
    }
    return image_rating in safety_mapping[maximum_rating]


def convert_distance_to_similarity(distance: float) -> float:
    return round((1 - distance) * 100, 2)


def prepare_similar_results(results, maximum_rating):
    return_results = []

    for i in results.values():
        rating = i['data']['source_rating']
        if not is_image_safe(maximum_rating, rating):
            i['thumbnail_path'] = 'static/images/18plus.png'  # todo: store in cfg
            if 'source_description' in i['data']:
                del(i['data']['source_description'])
        return_results.append(
            SimilarImage(
                data=i['data'],
                distance=convert_distance_to_similarity(i['distance']),
                id=i['id'],
                path=i['path'],
                thumbnail_path=i['thumbnail_path']
            ))
    return return_results


class Settings(APIView):
    image_match = TanukaiImgMatch()

    def get(self, request):
        rating = 'safe'
        active_partitions = {}

        partitions = self.image_match.get_partitions()
        for index, value in partitions.items():
            active_partitions[index] = {
                'count': value,
                'active': True
            }

        if request.user.is_authenticated:
            try:
                user_partitions = UserPartition.objects.filter(user=request.user)
                user_partitions_names = [i.partition for i in user_partitions]

                for active_partition in active_partitions.keys():
                    if active_partition not in user_partitions_names:
                        active_partitions[active_partition]['active'] = False
            except UserPartition.DoesNotExist:
                pass
            try:
                rating = UserRating.objects.get(user=request.user).rating
            except UserRating.DoesNotExist:
                pass
        serializer = SettingsSerializer(data={'partitions': active_partitions, 'rating': rating})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class Partitions(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        old_partitions = UserPartition.objects.filter(user=request.user)
        serializer = UserPartitionSerializer(old_partitions, data=request.data,
                                             context={'request': request}, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)


class Rating(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            old_rating = UserRating.objects.get(user=request.user)
        except UserRating.DoesNotExist:
            old_rating = None
        serializer = UserRatingSerializer(old_rating, data=request.data,
                                          context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)


class UploadImage(APIView):
    maximum_results = 100
    parser_classes = (MultiPartParser,)
    image_match = TanukaiImgMatch()

    def post(self, request):
        pagination_from = int(request.query_params.get('pagination_from', 0))
        pagination_size = int(request.query_params.get('pagination_size', 20))
        if pagination_from < 0 or pagination_from > self.maximum_results:
            raise ValidationError(
                f'Pagination must be larger than 0 and smaller than {self.maximum_results}')
        private_image = request.data.get('private_image', '') == 'true'
        if not request.user.is_authenticated and private_image:
            raise ValidationError(f'Only registered users can upload private images.')
        default_partitions = list(self.image_match.get_partitions().keys())
        partitions_selected = request.data.get('partitions').split(',') if request.data.get('partitions') else default_partitions
        maximum_rating = request.data.get('maximum_rating', 'safe')

        uploaded_img_serializer = UploadedImageSerializer(data=request.data)
        uploaded_img_serializer.is_valid(raise_exception=True)
        validated_image = uploaded_img_serializer.validated_data.get('image')
        uploaded_image = validated_image
        image = Image.open(uploaded_image)

        results, uploaded_img_features = self.image_match.search_image(
            path=validated_image.name,  # todo: marking subimage wont work here as its a fake path
            img=image,
            mark_subimage=False,
            pagination_from=pagination_from,
            pagination_size=pagination_size,
            partition_tags=partitions_selected
        )

        if request.user.is_authenticated:
            uploaded_img_model = uploaded_img_serializer.save(
                features=uploaded_img_features,
                uploader=request.user
            )
        else:
            uploaded_img_model = uploaded_img_serializer.save(features=uploaded_img_features)

        similar_images = prepare_similar_results(results, maximum_rating)
        image_search_results = ImageSearchResults(uploaded_image=uploaded_img_model,
                                                  similar_images=similar_images)
        results_serializer = ImageSearchResultsSerializer(image_search_results)
        return Response(results_serializer.data)

    def __save_uploaded_image(self, file):
        # TODO: store path in cfg + move to services/model
        uploaded_img_path = "static/uploaded/" + datetime.now().isoformat() + "_" + file.name

        with open(uploaded_img_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return uploaded_img_path


class UploadedImageSearch(APIView):
    image_match = TanukaiImgMatch()
    maximum_results = 50

    def get(self, request: Request, image_id: str):
        pagination_from = int(request.query_params.get('pagination_from', 0))
        pagination_size = int(request.query_params.get('pagination_size', 20))
        if pagination_from < 0 or pagination_from > self.maximum_results:
            raise ValidationError(
                f'Pagination must be larger than 0 and smaller than {self.maximum_results}')
        default_partitions = list(self.image_match.get_partitions().keys())
        partitions_selected = request.query_params.get('partitions').split(',') if request.query_params.get('partitions') else default_partitions
        maximum_rating = request.query_params.get('maximum_rating', 'safe')

        # TODO: add db trigger or cron to delete old results
        maximum_created_at = datetime.now() - timedelta(minutes=30)

        try:
            image_data = UploadedImage.objects.get(pk=image_id, created_at__gt=maximum_created_at)
        except UploadedImage.DoesNotExist:
            raise NotFound('Could not find the uploaded image.')
        self.__check_image_privacy(request, image_data)
        image_features = pickle.loads(image_data.features)
        results = self.image_match.search_by_features(image_features, False, pagination_from,
                                                      pagination_size,
                                                      partition_tags=partitions_selected)

        similar_images = prepare_similar_results(results, maximum_rating)
        image_search_results = ImageSearchResults(uploaded_image=image_data,
                                                  similar_images=similar_images)
        results_serializer = ImageSearchResultsSerializer(image_search_results)
        return Response(results_serializer.data)

    def __check_image_privacy(self, request, image_data):
        if image_data.private_image:
            if not request.user.is_authenticated:
                raise NotAuthenticated('You must be logged in to view a private image.')
            if request.user != image_data.uploader:
                raise PermissionDenied('This image is private and does not belong to you.')


class DatabaseImageSearch(APIView):
    image_match = TanukaiImgMatch()
    maximum_results = 100

    def get(self, request: Request, image_id: str):
        pagination_from = int(request.query_params.get('pagination_from', 0))
        pagination_size = int(request.query_params.get('pagination_size', 20))
        if pagination_from < 0 or pagination_from > self.maximum_results:
            raise ValidationError(
                f'Pagination must be larger than 0 and smaller than {self.maximum_results}')
        default_partitions = list(self.image_match.get_partitions().keys())
        partitions_selected = request.query_params.get('partitions').split(',') if request.query_params.get('partitions') else default_partitions
        maximum_rating = request.query_params.get('maximum_rating', 'safe')

        results, query_image = self.image_match.search_by_id(int(image_id), False, pagination_from,
                                                             pagination_size,
                                                             partition_tags=partitions_selected)

        similar_images = prepare_similar_results(results, maximum_rating)
        uploaded_img_model = UploadedImage(image=query_image.get('thumbnail_path'))
        image_search_results = ImageSearchResults(similar_images=similar_images,
                                                  uploaded_image=uploaded_img_model)
        results_serializer = ImageSearchResultsSerializer(image_search_results)
        return Response(results_serializer.data)


class UserTags(APIView):
    # TODO: implement
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = UserTag.objects.all()

        serializer = UserTagSerializer(data, context={'request': request}, many=True)

        return Response(serializer.data)
