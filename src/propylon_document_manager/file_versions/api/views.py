from django.shortcuts import render

from rest_framework.filters import OrderingFilter
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin,
    ListModelMixin
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from ..models import FileVersion
from .serializers import FileVersionSerializer


class IsAuthor(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        # Allow only if the user is the files creator
        if request.method in ['POST', 'PUT']:
            # import pdb; pdb.set_trace()
            try:
                file_name = view.kwargs['filename']
                existing = FileVersion.objects.filter(author=request.user, file_name=file_name).order_by('-version_number').first()
                if not existing:
                    raise FileVersion.DoesNotExist
                return True
            except FileVersion.DoesNotExist:
                return True  # Allow creation for non-existing file

        return False


class FileVersionViewSet(CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet):
    authentication_classes = []
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all()
    lookup_field = "id"
    permission_classes = [IsAuthenticated, IsAuthor]
    filterset_fields = ['version_number']
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        # import pdb; pdb.set_trace()
        filename = self.kwargs.get('filename')
        return FileVersion.objects.filter(author=self.request.user, file_name=filename)

    def perform_create(self, serializer):
        # import pdb; pdb.set_trace()
        filename = self.kwargs.get('filename')
        latest_record = FileVersion.objects.filter(author=self.request.user, file_name=filename).order_by('-version_number').first()
        if latest_record:
            new_revision = latest_record.version_number + 1
        else:
            new_revision = 1
        serializer.save(author=self.request.user, file_name=filename, version_number=new_revision)

    def create(self, request, *args, **kwargs):
        # import pdb; pdb.set_trace()
        file = kwargs.get("filename")
        if not file:
            return Response({'error': 'file is required'}, status=400)
        data = {
            'file_name': file,
            'author': request.user
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def list(self, request, *args, **kwargs):
        # import pdb; pdb.set_trace()
        filename = self.kwargs.get('filename')
        revision = request.query_params.get('revision', None)
        if revision is None:
            latest_record = FileVersion.objects.filter(author=request.user, file_name=filename).order_by('-version_number').first()
            if latest_record:
                serializer = self.get_serializer(latest_record)
                return Response(serializer.data)
            return Response({"detail": "No records found"}, status=404)

        record = FileVersion.objects.get(author=request.user, file_name=filename, version_number=revision)
        if record:
            serializer = self.get_serializer(record)
            return Response(serializer.data)

        return Response({"detail": "No records found"}, status=404)
