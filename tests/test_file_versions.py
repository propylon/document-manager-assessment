# from propylon_document_manager.file_versions.models import FileVersion

# def test_file_versions():
#     file_name = "new_file"
#     file_version = 1
#     FileVersion.objects.create(
#         file_name=file_name,
#         version_number=file_version
#     )
#     files = FileVersion.objects.all()
#     assert files.count() == 1
#     assert files[0].file_name == file_name
#     assert files[0].version_number == file_version

import io
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from propylon_document_manager.file_versions.models import FileVersion
from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.mark.django_db
class TestFileUploadAPI:

    def setup_method(self):
        self.client = APIClient()
        # Create two users
        from propylon_document_manager.file_versions.models import User
        self.user = User.objects.create_user(email="user1@example.com", password="password123")
        self.user2 = User.objects.create_user(email="user2@example.com", password="password123")
        self.client.force_authenticate(user=self.user)

    def test_upload_file_successfully(self):
        file_data = SimpleUploadedFile("test.pdf", b"File content here", content_type="application/pdf")
        response = self.client.post("/api/upload/", {
            'file_name': 'test.pdf',
            'file': file_data,
            'url_path': '/documents/my/test.pdf',
        }, format='multipart')

        assert response.status_code == 201
        assert response.data['file_name'] == 'test.pdf'
        assert response.data['version_number'] == 0

    def test_second_upload_increments_version(self):
        path = "/documents/my/test.pdf"

        # first
        self.client.post("/api/upload/", {
            'file_name': 'test.pdf',
            'file': SimpleUploadedFile("test.pdf", b"first", content_type="application/pdf"),
            'url_path': path,
        }, format='multipart')

        # second
        response = self.client.post("/api/upload/", {
            'file_name': 'test.pdf',
            'file': SimpleUploadedFile("test.pdf", b"second", content_type="application/pdf"),
            'url_path': path,
        }, format='multipart')

        assert response.status_code == 201
        assert response.data['version_number'] == 1

    def test_cannot_access_others_file(self):
        # User 1 uploads a file
        self.client.post("/api/upload/", {
            'file_name': 'private.pdf',
            'file': SimpleUploadedFile("private.pdf", b"secret", content_type="application/pdf"),
            'url_path': "/documents/secret/private.pdf",
        }, format='multipart')

        # User 2 tries to access it
        self.client.force_authenticate(user=self.user2)
        response = self.client.get("/api/documents/secret/private.pdf")

        assert response.status_code == 404
