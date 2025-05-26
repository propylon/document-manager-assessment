from rest_framework import generics, permissions
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated

from ..models import FileVersion, User
from .serializers import FileVersionSerializer, RegisterSerializer
from rest_framework import filters

# File versioning API
class FileVersionViewSet(CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = FileVersionSerializer
    permission_classes = [IsAuthenticated]  # Only logged-in users can upload/list
    queryset = FileVersion.objects.all()
    lookup_field = "id"
    filter_backends = [filters.SearchFilter]
    search_fields = ['file_name', 'version_number']

    def get_queryset(self):
        user = self.request.user
        queryset = FileVersion.objects.filter(user=user).order_by("-uploaded_at")
        version = self.request.query_params.get("version")
        filename = self.request.query_params.get("filename")
        if version is not None and version.isdigit():
            queryset = queryset.filter(version_number=int(version))
        if filename:
            queryset = queryset.filter(file_name__icontains=filename)
        return queryset

    def perform_create(self, serializer):
        # Save the user as the owner of the file version
        serializer.save(user=self.request.user)

# User registration API
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
