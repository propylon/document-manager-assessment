from django.conf import settings
from django.urls import include, path, re_path

from rest_framework.routers import DefaultRouter, SimpleRouter

from propylon_document_manager.file_versions.api.views import FileVersionViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

file_version_list = FileVersionViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

# This regular expression pattern (?P<filename>[\w./-]+) allows characters a-z, A-Z, 0-9, _, ., /, and - in the filename.
urlpatterns = [
    path('', include(router.urls)),
    re_path(r'file_versions/(?P<filename>[\w./-]+)/$', file_version_list, name='file_version-list'),
]
