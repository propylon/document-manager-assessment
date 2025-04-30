from collections.abc import Sequence
from typing import Any

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from factory import Faker, post_generation, SubFactory
from factory.django import DjangoModelFactory

from propylon_document_manager.file_versions.models import Document, FileVersion


class UserFactory(DjangoModelFactory):
    email = Faker("email")
    name = Faker("name")

    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):
        password = (
            extracted
            if extracted
            else Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).evaluate(None, None, extra={"locale": None})
        )
        self.set_password(password)

    class Meta:
        model = get_user_model()
        django_get_or_create = ["email"]


class DocumentFactory(DjangoModelFactory):
    class Meta:
        model = Document

    file_name = Faker("file_name")
    owner = SubFactory(UserFactory)
    latest_version_number = 1


class FileVersionFactory(DjangoModelFactory):
    class Meta:
        model = FileVersion

    document = SubFactory(DocumentFactory)
    version_number = Faker("random_int", min=1, max=100)
    owner = SubFactory(UserFactory)
    content = SimpleUploadedFile("test_file.txt", b"Test content")
