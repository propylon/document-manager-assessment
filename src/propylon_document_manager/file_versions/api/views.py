from django.shortcuts import render

from django.http import Http404, FileResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from urllib.parse import unquote
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from ..models import FileVersion, User
from .serializers import FileVersionSerializer, UploadFileVersionSerializer
from django.db.models import Q




class FileVersionViewSet(RetrieveModelMixin, ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = []
    permission_classes = []
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all()
    lookup_field = "id"


class UploadFileVersionViewSet(viewsets.ModelViewSet):
    serializer_class = UploadFileVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        # Only allow users to see their own uploads
        return FileVersion.objects.filter(uploaded_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_file_by_url(request, path):
    user = request.user
    revision = request.GET.get("revision")

    # ✅ Normalize incoming path (strip leading slashes only)
    normalized_path = unquote(path).lstrip("/")

    # Try to find matching FileVersion by normalized path
    file_versions = FileVersion.objects.filter(
        uploaded_by=user,
        # Q(uploaded_by=user) | Q(can_read_users=user),
        url_path=normalized_path
    ).order_by("-version_number")

    if not file_versions.exists():
        raise Http404("No file found at this path.")

    # Optional specific version
    if revision is not None:
        try:
            version = file_versions.filter(version_number=int(revision)).first()
            if not version:
                raise Http404("Specified revision not found.")
        except ValueError:
            raise Http404("Invalid revision number.")
    else:
        version = file_versions.first()

    return FileResponse(version.file, as_attachment=True, filename=version.file_name)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_file_by_content_hash(request, hash):
    """
    Retrieve a file by its content hash (CAS).
    """
    user = request.user
    try:
        file_version = FileVersion.objects.get(content_hash=hash, uploaded_by=user)
    except FileVersion.DoesNotExist:
        raise Http404("File not found for given hash.")

    return FileResponse(file_version.file, as_attachment=True, filename=file_version.file_name)


@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    print("in registration:::::::::::::::::::::::::::::::")
    email = request.data.get("email")
    password = request.data.get("password")
    if email and password:
        user = User.objects.create_user(email=email, password=password)
        return Response({"detail": "User created"}, status=201)
    return Response({"detail": "Missing email or password"}, status=400)
