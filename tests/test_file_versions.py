from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from propylon_document_manager.file_versions.models import FileVersion


def test_file_versions():
    file_name = "new_file"
    file_version = 1
    FileVersion.objects.create(file_name=file_name, version_number=file_version)
    files = FileVersion.objects.all()
    assert files.count() == 1
    assert files[0].file_name == file_name
    assert files[0].version_number == file_version


def test_file_versions_api_can_upload_files():
    client = APIClient()
    uploaded_file = SimpleUploadedFile("notes.txt", b"hello world", content_type="text/plain")

    response = client.post("/api/file_versions/", {"file": uploaded_file}, format="multipart")

    assert response.status_code == 201
    assert response.data["file_name"] == "notes.txt"
    assert response.data["content_type"] == "text/plain"
    assert FileVersion.objects.count() == 1
