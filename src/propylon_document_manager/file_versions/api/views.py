from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.parsers import FormParser, MultiPartParser
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
