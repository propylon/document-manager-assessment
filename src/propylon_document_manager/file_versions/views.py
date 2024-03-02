from django.db.models import Q
from django.http import FileResponse, HttpResponse, HttpResponseForbidden
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import FileVersion
from .serializers import FileVersionSerializer


class FileVersionViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet, CreateModelMixin, DestroyModelMixin):
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all()
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user

        queryset = super().get_queryset().filter(Q(owner=user) | Q(collaborators__in=[user]))

        return queryset

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class FileVersionSpecificViewSet(FileVersionViewSet):
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all()
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        url_filter = self.request.query_params.get("url")
        version_number = self.request.query_params.get("version_number")

        queryset = super().get_queryset().filter(Q(owner=user) | Q(collaborators__in=[user]))

        if url_filter:
            queryset = queryset.filter(url=url_filter)

        if version_number:
            queryset = queryset.filter(version_number=version_number)

        return queryset

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        file_version = self.get_object()
        print(file_version, file_version.file_field.path)
        file_path = file_version.file_field.path

        user = request.user
        if user == file_version.owner or user in file_version.collaborators.all():
            file_path = file_version.file_field.path
            try:
                with open(file_path, "rb") as file:
                    return FileResponse(open(file_path, "rb"), as_attachment=True, filename=file_version.file_name)
            except FileNotFoundError:
                return HttpResponse(status=404)
        else:
            return HttpResponseForbidden("You are not authorized to download this file.")
