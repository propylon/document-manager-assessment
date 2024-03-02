from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import FileVersionSpecificViewSet, FileVersionViewSet

router = DefaultRouter()

router.register("all", FileVersionViewSet, basename="file_version_all")
router.register("", FileVersionSpecificViewSet, basename="file_version_specific")

urlpatterns = [
    path("download/<int:pk>/", FileVersionSpecificViewSet.as_view({"get": "download"}), name="file-version-download"),
] + router.urls
