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


def test_file_versions_api_can_upload_files_to_any_url():
    client = APIClient()
    uploaded_file = SimpleUploadedFile("review.pdf", b"pdf-content", content_type="application/pdf")
    response = client.post(
        "/api/documents/reviews/review.pdf",
        {"file": uploaded_file},
        format="multipart",
    )

    assert response.status_code == 201
    assert response.data["file_name"] == "review.pdf"
    assert response.data["url_path"] == "reviews/review.pdf"
    assert response.data["version_number"] == 1
    assert response.data["content_type"] == "application/pdf"
    assert FileVersion.objects.filter(url_path="reviews/review.pdf").count() == 1


def test_file_versions_api_supports_multiple_versions_on_same_url():
    client = APIClient()
    first_file = SimpleUploadedFile("review.pdf", b"first-version", content_type="application/pdf")
    second_file = SimpleUploadedFile("review.pdf", b"second-version", content_type="application/pdf")

    first_resp = client.post(
        "/api/documents/reviews/review.pdf",
        {"file": first_file},
        format="multipart",
    )
    second_resp = client.post(
        "/api/documents/reviews/review.pdf",
        {"file": second_file},
        format="multipart",
    )

    assert first_resp.status_code == 201
    assert first_resp.data["version_number"] == 1
    assert second_resp.status_code == 201
    assert second_resp.data["version_number"] == 2
    assert FileVersion.objects.filter(url_path="reviews/review.pdf").count() == 2


def test_file_versions_api_retrieves_specific_revision_by_query_param():
    client = APIClient()
    client.post(
        "/api/documents/reviews/review.pdf",
        {"file": SimpleUploadedFile("review.pdf", b"first-version", content_type="application/pdf")},
        format="multipart",
    )
    client.post(
        "/api/documents/reviews/review.pdf",
        {"file": SimpleUploadedFile("review.pdf", b"second-version", content_type="application/pdf")},
        format="multipart",
    )

    response = client.get("/api/documents/reviews/review.pdf?revision=0")
    assert response.status_code == 200
    assert b"".join(response.streaming_content) == b"first-version"

    response = client.get("/api/documents/reviews/review.pdf?revision=1")
    assert response.status_code == 200
    assert b"".join(response.streaming_content) == b"second-version"


def test_document_metadata_endpoint_returns_json_for_latest_and_revision():
    client = APIClient()
    client.post(
        "/api/documents/reviews/review.pdf",
        {"file": SimpleUploadedFile("review.pdf", b"first-version", content_type="application/pdf")},
        format="multipart",
    )
    client.post(
        "/api/documents/reviews/review.pdf",
        {"file": SimpleUploadedFile("review.pdf", b"second-version", content_type="application/pdf")},
        format="multipart",
    )

    latest = client.get("/api/documents/reviews/review.pdf/metadata")
    assert latest.status_code == 200
    assert latest.data["url_path"] == "reviews/review.pdf"
    assert latest.data["version_number"] == 2

    revision_zero = client.get("/api/documents/reviews/review.pdf/metadata?revision=0")
    assert revision_zero.status_code == 200
    assert revision_zero.data["version_number"] == 1
