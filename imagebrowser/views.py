import pickle
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from img_match.img_match import ImgMatch
from .models import UserTag, UploadedImage, ImageSearchResults, UserPartition, UserRating
from .serializers import UserTagSerializer, ImageSearchResultsSerializer, SettingsSerializer, \
    UserPartitionSerializer, UserRatingSerializer
from rest_framework.parsers import MultiPartParser
from .models import SimilarImage


class UserTags(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = UserTag.objects.all()

        serializer = UserTagSerializer(data, context={'request': request}, many=True)

        return Response(serializer.data)


class Settings(APIView):
    image_match = ImgMatch()

    def get(self, request):
        rating = 'safe'

        partitions = self.image_match.get_partitions()
        active_partitions = {}
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
        old_rating = UserRating.objects.get(user=request.user)
        serializer = UserRatingSerializer(old_rating, data=request.data,
                                          context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)


class UploadImage(APIView):
    parser_classes = (MultiPartParser,)
    image_match = ImgMatch()
    safety_mapping = {
        'safe': ['safe'],
        'questionable': ['safe', 'questionable'],
        'explicit': ['safe', 'questionable', 'explicit']
    }

    def post(self, request):
        file = request.data.get('file')
        partitions_selected = request.data.get('partitions', ['e621']).split(',')
        maximum_rating = request.data.get('maximum_rating', 'safe')
        # partitions = self.image_match.get_partitions()

        uploaded_img_path = "static/uploaded/" + datetime.now().isoformat() + "_" + file.name

        with open(uploaded_img_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        results, uploaded_img_features = self.image_match.search_image(uploaded_img_path, False, 0,
                                                                       20,
                                                                       partition_tags=partitions_selected)

        uploaded_img_model = UploadedImage(features=uploaded_img_features, image=uploaded_img_path)
        if request.user.is_authenticated:
            uploaded_img_model.uploader = request.user
        uploaded_img_model.save()

        sim_img_res = []

        for i in results.values():
            rating = i['data']['source_rating']
            if rating not in self.safety_mapping[maximum_rating]:
                i['thumbnail_path'] = 'static/18plus.png'
            sim_img_res.append(
                SimilarImage(data=i['data'], distance=i['distance'], id=i['id'], path=i['path'],
                             thumbnail_path=i['thumbnail_path']))

        image_search_results = ImageSearchResults(uploaded_image=uploaded_img_model,
                                                  similar_images=sim_img_res)
        results_serializer = ImageSearchResultsSerializer(image_search_results)
        return Response(results_serializer.data)


class UploadedImageSearch(APIView):
    image_match = ImgMatch()

    def get(self, request, image_id):
        pagination_from = int(request.query_params.get('pagination_from', 0))
        pagination_size = int(request.query_params.get('pagination_size', 20))
        partitions_selected = request.data.get('partitions', ['e621', 'danbooru'])

        image_data = UploadedImage.objects.get(pk=image_id)
        image_features = pickle.loads(image_data.features)
        results = self.image_match.search_by_features(image_features, False, pagination_from,
                                                      pagination_size,
                                                      partition_tags=partitions_selected)

        sim_img_res = []

        for i in results.values():
            sim_img_res.append(
                SimilarImage(data=i['data'], distance=i['distance'], id=i['id'], path=i['path'],
                             thumbnail_path=i['thumbnail_path']))

        image_search_results = ImageSearchResults(uploaded_image=image_data,
                                                  similar_images=sim_img_res)
        results_serializer = ImageSearchResultsSerializer(image_search_results)
        return Response(results_serializer.data)


class DatabaseImageSearch(APIView):
    image_match = ImgMatch()

    def get(self, request, image_id):
        pagination_from = int(request.query_params.get('pagination_from', 0))
        pagination_size = int(request.query_params.get('pagination_size', 20))
        partitions_selected = request.data.get('partitions', ['e621', 'danbooru'])

        results = self.image_match.search_by_id(int(image_id), False, pagination_from,
                                                pagination_size, partition_tags=partitions_selected)

        sim_img_res = []

        for i in results.values():
            sim_img_res.append(
                SimilarImage(data=i['data'], distance=i['distance'], id=i['id'], path=i['path'],
                             thumbnail_path=i['thumbnail_path']))

        uploaded_img_model = UploadedImage(image=sim_img_res[0].thumbnail_path)

        image_search_results = ImageSearchResults(similar_images=sim_img_res,
                                                  uploaded_image=uploaded_img_model)
        results_serializer = ImageSearchResultsSerializer(image_search_results)
        return Response(results_serializer.data)

# @api_view(['GET', 'POST'])
# def user_tags_list(request):
#     if request.method == 'GET':
#         data = UserTag.objects.all()
#
#         serializer = UserTagSerializer(data, context={'request': request}, many=True)
#
#         return Response(serializer.data)
