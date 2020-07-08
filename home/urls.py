from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from imagebrowser.views import UserTags, UploadImage, UploadedImageSearch, DatabaseImageSearch, \
    Settings, Rating, Partitions
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('api/api-auth/', csrf_exempt(include('rest_framework.urls'))),
    re_path(r'^api/rest-auth/', include('rest_auth.urls')),
    path('api/rest-auth/registration/', include('rest_auth.registration.urls')),
    path('api/admin/', admin.site.urls),
    path('api/v1/user-tags', UserTags.as_view()),
    path('api/v1/upload-image', UploadImage.as_view()),
    path('api/v1/settings', Settings.as_view()),
    path('api/v1/rating', Rating.as_view()),
    path('api/v1/partitions', Partitions.as_view()),
    re_path(r'^api/v1/uploaded-image-search/(?P<image_id>[0-9]+)$', UploadedImageSearch.as_view()),
    re_path(r'^api/v1/database-image-search/(?P<image_id>[0-9]+)$', DatabaseImageSearch.as_view()),
    re_path(r'^.*', TemplateView.as_view(template_name='base.html')),
]
