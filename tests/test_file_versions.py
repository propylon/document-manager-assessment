from propylon_document_manager.file_versions.models import FileVersion, Document, User

from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from .factories import UserFactory, DocumentFactory, FileVersionFactory

def test_file_versions():
    file_name = "new_file"
    file_version = 1
    FileVersion.objects.create(
        file_name=file_name,
        version_number=file_version
    )
    files = FileVersion.objects.all()
    assert files.count() == 1
    assert files[0].file_name == file_name
    assert files[0].version_number == file_version


class FileVersionViewSetTestCase(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

        # Create a test document and file version
        self.document = DocumentFactory(owner=self.user)
        self.file_version = FileVersionFactory(document=self.document, owner=self.user)

    def test_create_file_version_success(self):
        # Test successful file upload
        file = SimpleUploadedFile("new_file.txt", b"New file content")
        response = self.client.post("/file-versions/", {"content": file}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("responseCode", response.data)
        self.assertEqual(response.data["responseCode"], 200)

    def test_create_file_version_duplicate(self):
        # Test duplicate file upload
        file = SimpleUploadedFile("test_file.txt", b"Test content")
        response = self.client.post("/file-versions/", {"content": file}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("responseCode", response.data)
        self.assertEqual(response.data["responseCode"], 301)
