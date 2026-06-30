from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from propylon_document_manager.file_versions.models import FileVersion
from .factories import UserFactory


def _auth_client(email: str) -> APIClient:
    user = UserFactory(email=email)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_file_versions(user):
    file_name = "new_file"
    file_version = 1
    FileVersion.objects.create(owner=user, file_name=file_name, version_number=file_version)
    files = FileVersion.objects.all()
    assert files.count() == 1
    assert files[0].file_name == file_name
    assert files[0].version_number == file_version


def test_file_versions_api_can_upload_files():
    client = _auth_client("user1@example.com")
    uploaded_file = SimpleUploadedFile("notes.txt", b"hello world", content_type="text/plain")

    response = client.post("/api/file_versions/", {"file": uploaded_file}, format="multipart")

    assert response.status_code == 201
    assert response.data["file_name"] == "notes.txt"
    assert response.data["content_type"] == "text/plain"
    assert response.data["version_number"] == 1
    assert FileVersion.objects.count() == 1


def test_file_versions_api_can_upload_files_to_any_url():
    client = _auth_client("user2@example.com")
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
    client = _auth_client("user3@example.com")
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
    client = _auth_client("user4@example.com")
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
    client = _auth_client("user5@example.com")
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


def test_endpoints_require_authentication():
    client = APIClient()
    response = client.post(
        "/api/documents/reviews/review.pdf",
        {"file": SimpleUploadedFile("review.pdf", b"content", content_type="application/pdf")},
        format="multipart",
    )
    assert response.status_code in (401, 403)

    response = client.get("/api/documents/reviews/review.pdf")
    assert response.status_code in (401, 403)

    response = client.get("/api/documents/reviews/review.pdf/metadata")
    assert response.status_code in (401, 403)

    response = client.get("/api/file_versions/")
    assert response.status_code in (401, 403)


def test_users_cannot_access_files_uploaded_by_others():
    owner_client = _auth_client("owner@example.com")
    owner_client.post(
        "/api/documents/reviews/review.pdf",
        {"file": SimpleUploadedFile("review.pdf", b"owner-data", content_type="application/pdf")},
        format="multipart",
    )

    other_client = _auth_client("other@example.com")
    response = other_client.get("/api/documents/reviews/review.pdf")
    assert response.status_code == 404

    metadata_response = other_client.get("/api/documents/reviews/review.pdf/metadata")
    assert metadata_response.status_code == 404

    list_response = other_client.get("/api/file_versions/")
    assert list_response.status_code == 200
    assert list_response.data == []


def test_different_users_can_use_same_url_with_independent_versioning():
    first_user = _auth_client("first@example.com")
    second_user = _auth_client("second@example.com")

    first_upload = first_user.post(
        "/api/documents/reviews/review.pdf",
        {"file": SimpleUploadedFile("review.pdf", b"first-user-v1", content_type="application/pdf")},
        format="multipart",
    )
    second_upload = second_user.post(
        "/api/documents/reviews/review.pdf",
        {"file": SimpleUploadedFile("review.pdf", b"second-user-v1", content_type="application/pdf")},
        format="multipart",
    )

    assert first_upload.status_code == 201
    assert second_upload.status_code == 201
    assert first_upload.data["version_number"] == 1
    assert second_upload.data["version_number"] == 1


def test_cas_endpoint_returns_file_for_owner_by_hash():
    client = _auth_client("cas-owner@example.com")
    upload = client.post(
        "/api/documents/reviews/review.pdf",
        {"file": SimpleUploadedFile("review.pdf", b"cas-data", content_type="application/pdf")},
        format="multipart",
    )

    assert upload.status_code == 201
    content_hash = upload.data["content_hash"]
    assert content_hash

    response = client.get(f"/api/cas/{content_hash}")
    assert response.status_code == 200
    assert b"".join(response.streaming_content) == b"cas-data"


def test_cas_endpoint_enforces_auth_and_owner_isolation():
    owner_client = _auth_client("cas-owner-2@example.com")
    upload = owner_client.post(
        "/api/documents/reviews/review.pdf",
        {"file": SimpleUploadedFile("review.pdf", b"secret-cas-data", content_type="application/pdf")},
        format="multipart",
    )
    content_hash = upload.data["content_hash"]

    unauth_client = APIClient()
    unauth_response = unauth_client.get(f"/api/cas/{content_hash}")
    assert unauth_response.status_code in (401, 403)

    other_client = _auth_client("cas-other@example.com")
    other_response = other_client.get(f"/api/cas/{content_hash}")
    assert other_response.status_code == 404
