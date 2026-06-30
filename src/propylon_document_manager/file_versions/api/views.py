import os

from django.http import FileResponse, Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from ..models import FileVersion
from .serializers import FileVersionSerializer


class FileVersionViewSet(CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet):
    # Generic file-version API: authenticated users can only list/retrieve their own records.
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.none()
    lookup_field = "id"

    def get_queryset(self):
        return FileVersion.objects.filter(owner=self.request.user).order_by("-uploaded_at", "-version_number")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class DocumentView(APIView):
    # URL-addressed upload/retrieval endpoint with revision support.
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, url_path):
        url_path = url_path.strip("/")
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"detail": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        file_name = os.path.basename(url_path) or uploaded_file.name
        file_version = FileVersion(
            owner=request.user,
            url_path=url_path,
            file=uploaded_file,
            file_name=file_name,
            content_type=getattr(uploaded_file, "content_type", None) or "application/octet-stream",
            file_size=uploaded_file.size,
        )
        file_version.save()

        serializer = FileVersionSerializer(file_version, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, url_path):
        url_path = url_path.strip("/")
        versions = FileVersion.objects.filter(owner=request.user, url_path=url_path).order_by("version_number")
        if not versions.exists():
            raise Http404("Document not found.")

        revision = request.query_params.get("revision")
        if revision is not None:
            try:
                revision_index = int(revision)
            except ValueError:
                return Response({"detail": "Invalid revision."}, status=status.HTTP_400_BAD_REQUEST)

            if revision_index < 0 or revision_index >= versions.count():
                raise Http404("Revision not found.")
            file_version = versions[revision_index]
        else:
            file_version = versions.last()

        if not file_version.file:
            raise Http404("File not found.")

        return FileResponse(
            file_version.file.open("rb"),
            content_type=file_version.content_type or "application/octet-stream",
            as_attachment=True,
            filename=file_version.file_name,
        )


class DocumentMetadataView(APIView):
    # Metadata-only representation for latest or specific revision.
    permission_classes = [IsAuthenticated]

    def get(self, request, url_path):
        url_path = url_path.strip("/")
        versions = FileVersion.objects.filter(owner=request.user, url_path=url_path).order_by("version_number")
        if not versions.exists():
            raise Http404("Document not found.")

        revision = request.query_params.get("revision")
        if revision is not None:
            try:
                revision_index = int(revision)
            except ValueError:
                return Response({"detail": "Invalid revision."}, status=status.HTTP_400_BAD_REQUEST)

            if revision_index < 0 or revision_index >= versions.count():
                raise Http404("Revision not found.")
            file_version = versions[revision_index]
        else:
            file_version = versions.last()

        serializer = FileVersionSerializer(file_version, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CASDocumentView(APIView):
    # Content-addressable retrieval by SHA-256 hash, scoped to the requesting owner.
    permission_classes = [IsAuthenticated]

    def get(self, request, content_hash):
        file_version = (
            FileVersion.objects.filter(owner=request.user, content_hash=content_hash)
            .order_by("-uploaded_at", "-version_number")
            .first()
        )
        if file_version is None:
            raise Http404("Document not found.")
        if not file_version.file:
            raise Http404("File not found.")

        return FileResponse(
            file_version.file.open("rb"),
            content_type=file_version.content_type or "application/octet-stream",
            as_attachment=True,
            filename=file_version.file_name,
        )
