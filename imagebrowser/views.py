import pickle
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from img_match.img_match import ImgMatch
from .models import UserTag, UploadedImage, ImageSearchResults, UserPartition
from .serializers import UserTagSerializer, ImageSearchResultsSerializer
from rest_framework.parsers import MultiPartParser
from .models import SimilarImage


class UserTags(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = UserTag.objects.all()

        serializer = UserTagSerializer(data, context={'request': request}, many=True)

        return Response(serializer.data)


class Partitions(APIView):
    image_match = ImgMatch()

    def get(self, request):
        partitions = self.image_match.get_partitions()

        if request.user.is_authenticated:
            user_partitions = UserPartition.objects.get(user=request.user)
            return user_partitions
        return partitions


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

        results, uploaded_img_features = self.image_match.search_image(uploaded_img_path, False, 0, 20, partition_tags=partitions_selected)

        uploaded_img_model = UploadedImage(features=uploaded_img_features, image=uploaded_img_path)
        if request.user.is_authenticated:
            uploaded_img_model.uploader = request.user
        uploaded_img_model.save()

        sim_img_res = []

        for i in results.values():
            rating = i['data']['source_rating']
            if rating not in self.safety_mapping[maximum_rating]:
                i['thumbnail_path'] = 'static/18plus.png'
            sim_img_res.append(SimilarImage(data=i['data'], distance=i['distance'], id=i['id'], path=i['path'], thumbnail_path=i['thumbnail_path']))

        image_search_results = ImageSearchResults(uploaded_image=uploaded_img_model, similar_images=sim_img_res)
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
        results = self.image_match.search_by_features(image_features, False, pagination_from, pagination_size, partition_tags=partitions_selected)

        sim_img_res = []

        for i in results.values():
            sim_img_res.append(SimilarImage(data=i['data'], distance=i['distance'], id=i['id'], path=i['path'], thumbnail_path=i['thumbnail_path']))

        image_search_results = ImageSearchResults(uploaded_image=image_data, similar_images=sim_img_res)
        results_serializer = ImageSearchResultsSerializer(image_search_results)
        return Response(results_serializer.data)


class DatabaseImageSearch(APIView):
    image_match = ImgMatch()

    def get(self, request, image_id):
        pagination_from = int(request.query_params.get('pagination_from', 0))
        pagination_size = int(request.query_params.get('pagination_size', 20))
        partitions_selected = request.data.get('partitions', ['e621', 'danbooru'])

        results = self.image_match.search_by_id(int(image_id), False, pagination_from, pagination_size, partition_tags=partitions_selected)

        sim_img_res = []

        for i in results.values():
            sim_img_res.append(SimilarImage(data=i['data'], distance=i['distance'], id=i['id'], path=i['path'], thumbnail_path=i['thumbnail_path']))

        uploaded_img_model = UploadedImage(image=sim_img_res[0].thumbnail_path)

        image_search_results = ImageSearchResults(similar_images=sim_img_res, uploaded_image=uploaded_img_model)
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
