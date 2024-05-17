from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from propylon_document_manager.file_versions.api.views import FileVersionViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register(r'file_versions/(?P<filename>[^/.]+)', FileVersionViewSet, basename="file_version")


app_name = "api"
import pdb; pdb.set_trace()
urlpatterns = router.urls
