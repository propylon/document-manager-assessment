from django.test import TestCase

from propylon_document_manager.file_versions.models import File, FileVersion, User


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


class FileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(name='testuser', email='testuser@test.com')
        File.objects.create(url='/myurl/testurl.txt', file_name='testfile', user_id=1)

    def test_url_label(self):
        file = File.objects.get(id=1)
        field_label = file._meta.get_field('url').verbose_name
        self.assertEqual(field_label, 'url')

    def test_file_name_label(self):
        file = File.objects.get(id=1)
        field_label = file._meta.get_field('file_name').verbose_name
        self.assertEqual(field_label, 'file_name')


class FileVersionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(name='testuser', email='testuser@test.com')
        File.objects.create(url='/myurl/testurl.pdf', file_name='testfile', user_id=1)
        FileVersion.objects.create(version=1, content='test content', hash='123abc', user_id=1, file_id=1)

    def test_version_label(self):
        file_version = FileVersion.objects.get(id=1)
        field_label = file_version._meta.get_field('version').verbose_name
        self.assertEqual(field_label, 'version')

    def test_content_label(self):
        file_version = FileVersion.objects.get(id=1)
        field_label = file_version._meta.get_field('content').verbose_name
        self.assertEqual(field_label, 'content')
