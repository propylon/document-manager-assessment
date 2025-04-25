import logging
from hashlib import sha256

from django.db import transaction, IntegrityError
from django.http import FileResponse
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404

from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from ..models import FileVersion, Document, User
from .serializers import FileVersionSerializer, FileInputSerializer
from ...utils.status_code import StatusCode

logger = logging.getLogger(__name__)


class FileVersionViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all()
    lookup_field = "id"


class FileUploadViewSet(ModelViewSet):
    serializer_class = FileVersionSerializer

    def get_queryset(self):
        return FileVersion.objects.filter(owner=self.request.user).order_by('-version_number')

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
                    defaults={'owner': user}
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
        version = request.query_params.get('revision', 0)
        try:
            rev = FileVersion.objects.filter(
                document__file_name=file_name,
                version_number=version,
                owner=request.user
            ).get()

            if not rev:
                return Response(StatusCode.get_response(400))
        except (ValueError, FileVersion.DoesNotExist):
            return Response(StatusCode.get_response(400))

        return FileResponse(rev.content, as_attachment=True, filename=file_name)


class GetFileByRevisionView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    # permission_classes = []

    def get(self, request, *args, **kwargs):
        path = kwargs.get('path')
        revision_number = kwargs.get('revision_number')

        return Response(**StatusCode.get_response(200))
        # Get the document
        document = get_object_or_404(Document, path=path, owner=request.user)

        # Get the revision
        if revision_number:
            revision = get_object_or_404(Revision, document=document, revision_number=revision_number)
        else:
            revision = document.revisions.order_by('-revision_number').first()

        # Return the file as a response
        return FileResponse(revision.content, as_attachment=True, filename=document.path)
