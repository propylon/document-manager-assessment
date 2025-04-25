from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from propylon_document_manager.file_versions.api.views import FileVersionViewSet, FileUploadViewSet

if settings.DEBUG:
    router = DefaultRouter(trailing_slash=False)
else:
    router = SimpleRouter(trailing_slash=False)

router.register("file_versions", FileVersionViewSet, basename='file')
router.register("document", FileUploadViewSet, basename="document")


app_name = "api"
urlpatterns = router.urls
