import os

from django.http import FileResponse, Http404
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from ..models import FileVersion
from .serializers import FileVersionSerializer


class FileVersionViewSet(CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet):
    authentication_classes = []
    permission_classes = []
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all().order_by("-uploaded_at", "-version_number")
    lookup_field = "id"


class DocumentView(APIView):
    authentication_classes = []
    permission_classes = []
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, url_path):
        url_path = url_path.strip("/")
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"detail": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        file_name = os.path.basename(url_path) or uploaded_file.name
        file_version = FileVersion(
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
        versions = FileVersion.objects.filter(url_path=url_path).order_by("version_number")
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

        response = FileResponse(file_version.file.open("rb"), content_type=file_version.content_type or "application/octet-stream")
        response["Content-Disposition"] = f'attachment; filename="{file_version.file_name}"'
        return response
