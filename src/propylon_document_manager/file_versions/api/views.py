import hashlib

from django.db import transaction
from django.db.models import OuterRef, Subquery
from django.http import FileResponse
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from ..models import Document, FileVersion
from .serializers import FileVersionSerializer

MAX_UPLOAD_SIZE_BYTES = 100 * 1024 * 1024


class FileVersionPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class FileVersionViewSet(CreateModelMixin, RetrieveModelMixin, ListModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = FileVersionSerializer
    lookup_field = "id"
    pagination_class = FileVersionPagination

    def get_queryset(self):
        """Only return file versions belonging to the authenticated user."""
        queryset = FileVersion.objects.filter(document__user=self.request.user)

        # Filter by document if parameter is provided
        document_id = self.request.query_params.get("document")
        if document_id is not None:
            queryset = queryset.filter(document_id=document_id)

        # Filter to only return the latest version of each document if requested
        latest = self.request.query_params.get("latest")
        if latest == "true" or latest == "1":
            latest_version_subquery = FileVersion.objects.filter(
                document=OuterRef("document")
            ).order_by("-version_number").values("id")[:1]
            queryset = queryset.filter(id__in=Subquery(latest_version_subquery))

        return queryset

    def paginate_queryset(self, queryset):
        # Disable pagination if we are querying versions of a specific document
        # or if no_pagination is explicitly requested
        if (
            self.request.query_params.get("document") is not None
            or self.request.query_params.get("no_pagination") == "true"
        ):
            return None
        return super().paginate_queryset(queryset)

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

    def delete(self, request, url_path):
        """Delete an entire document and all its versions."""
        document = get_object_or_404(
            Document,
            user=request.user,
            url_path=url_path,
        )
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)