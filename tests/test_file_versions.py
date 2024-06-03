from propylon_document_manager.file_versions.models import FileVersion
from django.contrib.auth import get_user_model

def test_file_versions():
    file_name = "new_file"
    file_version = 1
    user1 = get_user_model().objects.create_user(name="test1", email="test1@test.com")
    FileVersion.objects.create(
        file_name=file_name,
        version_number=file_version,
        author=user1
    )
    files = FileVersion.objects.all()
    assert files.count() == 1
    assert files[0].file_name == file_name
    assert files[0].version_number == file_version
