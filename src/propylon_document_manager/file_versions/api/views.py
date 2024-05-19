import logging

from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin,
    ListModelMixin
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from ..models import FileVersion
from .permissions import IsAuthor
from .serializers import FileVersionSerializer

logger = logging.getLogger(__name__)


class FileVersionViewSet(CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet):
    authentication_classes = []
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all()
    lookup_field = "id"
    # permission_classes = [IsAuthenticated]
    permission_classes = [IsAuthenticated, IsAuthor]
    # permission_classes = [IsAuthor]
    filterset_fields = ['version_number']

    def get_queryset(self):
        """
        Return query object
        """
        # import pdb; pdb.set_trace()
        filename = self.kwargs.get('filename')
        return FileVersion.objects.filter(author=self.request.user, file_name=filename)

    def perform_create(self, serializer):
        """
        Override perform_create method
        """
        # import pdb; pdb.set_trace()
        filename = self.kwargs.get('filename')
        latest_record = FileVersion.objects.filter(author=self.request.user, file_name=filename).order_by('-version_number').first()
        if latest_record:
            logger.info(f"Latest revision {latest_record.version_number}")
            new_revision = latest_record.version_number + 1
        else:
            # import pdb; pdb.set_trace()
            logger.info(f"New record {filename}")
            new_revision = 1
        serializer.save(author=self.request.user, file_name=filename, version_number=new_revision)

    def create(self, request, *args, **kwargs):
        """
        Override create method
        """
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
        """
        Override list method to return latest or specific versioned file
        """
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
            # Read blob from S3,
            # f"{request.user.id}-{filename}-{revord.version_number}"
            # append to the serialized data
            serializer = self.get_serializer(record)
            return Response(serializer.data)

        return Response({"detail": "No records found"}, status=404)
