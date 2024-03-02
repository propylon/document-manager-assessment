from rest_framework.routers import DefaultRouter

from .views import FileVersionSpecificViewSet, FileVersionViewSet

router = DefaultRouter()

router.register("all", FileVersionViewSet, basename="file_version_all")
router.register("specific", FileVersionSpecificViewSet, basename="file_version_specific")

urlpatterns = [] + router.urls
