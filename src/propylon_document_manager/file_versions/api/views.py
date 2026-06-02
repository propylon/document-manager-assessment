import hashlib

from django.db import transaction
from django.http import FileResponse
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from ..models import Document, FileVersion
from .serializers import FileVersionSerializer

MAX_UPLOAD_SIZE_BYTES = 100 * 1024 * 1024


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


class DocumentStorageView(APIView):
    def get(self, request, url_path):
        """Retrieve a document by logical url_path and optional revision query parameter."""
        document = get_object_or_404(
            Document,
            user=request.user,
            url_path=url_path,
        )

        revision = request.query_params.get("revision")
        if revision is not None:
            try:
                version_number = int(revision)
            except ValueError:
                return Response(
                    {"error": "Invalid revision parameter. Must be an integer."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            file_version = get_object_or_404(
                FileVersion,
                document=document,
                version_number=version_number,
            )
        else:
            file_version = document.versions.order_by("-version_number").first()
            if not file_version:
                return Response(
                    {"error": "No versions found for this document."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return FileResponse(
            file_version.file.open(),
            as_attachment=True,
            filename=file_version.file_name,
        )

    def post(self, request, url_path):
        """Upload a new version of a document at a specific logical url_path."""
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response(
                {"error": "No file uploaded in the request field 'file'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if uploaded_file.size > MAX_UPLOAD_SIZE_BYTES:
            return Response(
                {"error": f"File too large. Maximum allowed size is {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # 1. Automatically find or create the Document record
            document, _ = Document.objects.get_or_create(
                user=request.user,
                url_path=url_path,
            )

            # 2. Determine the next version number (0-indexed)
            latest_version = (
                document.versions
                .select_for_update()
                .order_by("-version_number")
                .first()
            )
            next_version = (latest_version.version_number + 1) if latest_version else 0

            # 3. Compute SHA-256 content hash
            sha256 = hashlib.sha256()
            for chunk in uploaded_file.chunks():
                sha256.update(chunk)
            content_hash = sha256.hexdigest()

            # 4. Save FileVersion
            uploaded_file.seek(0)
            file_version = FileVersion.objects.create(
                document=document,
                version_number=next_version,
                file_name=uploaded_file.name,
                content_hash=content_hash,
            )
            file_version.file.save(uploaded_file.name, uploaded_file)

        serializer = FileVersionSerializer(file_version, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)