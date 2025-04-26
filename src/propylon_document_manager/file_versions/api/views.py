import logging
from hashlib import sha256

from django.db import transaction, IntegrityError
from django.db.models import F, Value, CharField, Window, Count
from django.db.models.functions import Concat
from django.http import FileResponse
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404

from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from ..models import FileVersion, Document, User
from .serializers import FileVersionSerializer, DocumentSerializer
from ...utils.status_code import StatusCode

logger = logging.getLogger(__name__)


class FileVersionViewSet(ModelViewSet):
    serializer_class = FileVersionSerializer

    def get_queryset(self, *args, **kwargs):
        pk = self.request.query_params.get('id')
        qs = FileVersion.objects.filter(
            owner=self.request.user
        )
        if pk:
            qs = qs.filter(
                document__id=pk
            )
        return qs.order_by(
            'version_number'
        ).annotate(
            file_name=F('document__file_name'),
            full_path=Concat(Value('storage/'), F('content'), output_field=CharField())
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            res = self.upload_revision(request.user, serializer.validated_data['content'])
            return Response(res)
        return Response(StatusCode.get_response(500))

    @staticmethod
    def upload_revision(user, file):
        try:
            with transaction.atomic():
                doc, doc_created = Document.objects.get_or_create(
                    file_name=file.name,
                    owner=user
                )

                revision_no = 0 if doc_created else doc.latest_version_number + 1

                # Calculate the hash of the file
                hash_val = sha256(file.read()).hexdigest()
                file.seek(0)

                file_version, version_created = FileVersion.objects.get_or_create(
                    document=doc,
                    hash=hash_val,
                    owner=user,
                    defaults={'version_number': revision_no, 'content': file}
                )

                if not version_created:
                    return StatusCode.get_response(301)

                # Update the document's latest revision_no number if a new revision_no is created
                if version_created:
                    doc.latest_version_number = revision_no
                    doc.path = file_version.content.name
                    doc.save()

        except IntegrityError as e:
            logger.error(f"Integrity error occurred: {e}")
            return StatusCode.get_response(301)

        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            return StatusCode.get_response(500)  # Internal server error

        return StatusCode.get_response(200) | {'revisionNumber': revision_no, 'filePath': doc.path}

    @action(
        detail=False,
        methods=['get'],
        url_path=r'(?P<file_name>[^/]+)'
    )
    def get_document_revision(self, request, file_name):
        version = request.query_params.get('revision')
        try:
            qs = FileVersion.objects.filter(
                document__file_name=file_name,
                owner=request.user
            ).order_by(
                '-version_number'
            )
            if version:
                qs = qs.filter(version_number=version)

            rev = qs[:1].get()
            if not rev:
                return Response(StatusCode.get_response(400))
        except (ValueError, FileVersion.DoesNotExist):
            return Response(StatusCode.get_response(400))

        return FileResponse(rev.content, as_attachment=True, filename=file_name)


class DocumentViewSet(ModelViewSet):
    serializer_class = DocumentSerializer

    def get_queryset(self):
        return Document.objects.filter(
            owner=self.request.user
        ).values(
            'id',
            'file_name',
            'latest_version_number',
            'owner__pk'
        ).annotate(
            file_version_count=Count('revisions__id'),
        ).order_by(
            '-created_at'
        )
