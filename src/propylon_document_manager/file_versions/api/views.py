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
            try:
                file_name = view.kwargs['file']
                file = FileVersion.objects.get(file_name=file_name)
                return file.author == request.user
            except FileVersion.DoesNotExist:
                return True  # Allow creation for non-existing file

        return False


class FileVersionViewSet(CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet):
    authentication_classes = []
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all()
    lookup_field = "id"
    permission_classes = [IsAuthenticated, IsAuthor]
    filterset_fields = ['revision']
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        import pdb; pdb.set_trace()
        queryset = super().get_queryset()
        # filename = self.request.path.split('/')[-2]
        filename = self.kwargs.get('filename')
        if filename:
            queryset = queryset.filter(file_name=filename)
            revision = self.request.query_params.get('revision')
            if revision:
                queryset = queryset.filter(vrsion_number=revision)
            else:
                queryset = queryset.order_by('-version_number').first()
        return queryset

    @action(detail=False, methods=['get'])
    def latest(self, request, filename=None):
        latest_record = FileVersion.objects.filter(user=request.user, filename=filename).first()
        if not latest_record:
            return Response({"detail": "No records found"}, status=404)
        serializer = self.get_serializer(latest_record)
        return Response(serializer.data)

    def perform_create(self, serializer) -> None:
        if not serializer.validated_data.get('version_number'):
            existing = FileVersion.objects.filter(file_name=serializer.validated_data['file_name']).order_by('-version_number').first()
            if existing:
                serializer.validated_data['version_number'] = existing.version_number + 1
        # serializer.save(author=self.request.user)
        serializer.save()

    def create(self, request, *args, **kwargs):
        import pdb; pdb.set_trace()
        file = request.path.split('/')[-2]
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
        return Response(serializer.data, status=200, headers=headers)
        # Increment version if same author and title exist
        # if not serializer.instance.version:  # Check if version already set (for updates)
        #     existing = FileVersion.objects.filter(author=serializer.validated_data['author'],
        #                                        title=serializer.validated_data['title'])
        #     if existing:
        #         serializer.instance.version = existing.latest('version').version + 1
        # serializer.save()
