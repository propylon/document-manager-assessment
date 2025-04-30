from propylon_document_manager.file_versions.models import FileVersion, Document, User

from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from .factories import UserFactory, DocumentFactory, FileVersionFactory


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
        response = self.client.post("/api/document", {"content": file}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("responseCode", response.data)
        self.assertEqual(response.data["responseCode"], 200)

    def test_create_file_version_duplicate(self):
        # Test duplicate file upload
        file = SimpleUploadedFile("test_file.txt", b"Test content")
        self.client.post("/api/document", {"content": file}, format="multipart")
        file.seek(0)
        response = self.client.post("/api/document", {"content": file}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("responseCode", response.data)
        self.assertEqual(response.data["responseCode"], 301)

    def test_create_file_next_version(self):
        # Test duplicate file upload
        file = SimpleUploadedFile("test_file.txt", b"Test content")
        self.client.post("/api/document", {"content": file}, format="multipart")

        file = SimpleUploadedFile("test_file.txt", b"Test content Revised")

        response = self.client.post("/api/document", {"content": file}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("responseCode", response.data)
        self.assertEqual(response.data["revisionNumber"], 1)
        self.assertEqual(response.data["responseCode"], 200)


class DocumentViewSetTestCase(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

        # Create a test document and file version
        self.document = DocumentFactory(owner=self.user)
        self.file_version = FileVersionFactory(document=self.document, owner=self.user)

    def test_document_version_count_success(self):
        # Test successful file upload
        file = SimpleUploadedFile("new_file.txt", b"New file content")
        self.client.post("/api/document", {"content": file}, format="multipart")
        file = SimpleUploadedFile("new_file.txt", b"New file content Revised 2")
        self.client.post("/api/document", {"content": file}, format="multipart")

        response = self.client.get("/api/file", {})
        self.assertIn("responseCode", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data'][0]["fileVersionCount"], 2)
        self.assertEqual(response.data['data'][0]["latestVersionNumber"], 1)

