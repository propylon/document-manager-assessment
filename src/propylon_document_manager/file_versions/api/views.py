from django.http import FileResponse
from django.shortcuts import get_object_or_404

from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet

from ..models import FileVersion
from .serializers import FileVersionSerializer


class FileVersionViewSet(CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = FileVersionSerializer
    lookup_field = "id"

    def get_queryset(self):
        """Only return file versions belonging to the authenticated user."""
        return FileVersion.objects.filter(document__user=self.request.user)

    @action(detail=True, methods=["get"])
    def download(self, request, id=None):
        """Download the file associated with a specific FileVersion."""
        file_version = self.get_object()
        return FileResponse(
            file_version.file.open(),
            as_attachment=True,
            filename=file_version.file_name,
        )

    @action(detail=False, methods=["get"], url_path=r"cas/(?P<content_hash>[a-f0-9]{64})")
    def cas_retrieve(self, request, content_hash=None):
        """Retrieve a file by its SHA-256 content hash (Content Addressable Storage)."""
        file_version = get_object_or_404(
            FileVersion,
            content_hash=content_hash,
            document__user=request.user,
        )
        return FileResponse(
            file_version.file.open(),
            as_attachment=True,
            filename=file_version.file_name,
        )
