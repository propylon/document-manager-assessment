from collections.abc import Sequence
from typing import Any

from django.contrib.auth import get_user_model
from factory import Faker, SubFactory, post_generation
from factory.django import DjangoModelFactory

from propylon_document_manager.file_versions.models import File, FileVersion


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


class FileFactory(DjangoModelFactory):
    url = Faker("uri")
    file_name = Faker("file_name")
    user = SubFactory(UserFactory)

    class Meta:
        model = File
        django_get_or_create = ["url"]


class FileVersionFactory(DjangoModelFactory):
    version = Faker("random_int")
    content = Faker("text")
    hash = Faker("sha256")
    user = SubFactory(UserFactory)
    file = SubFactory(FileFactory)

    class Meta:
        model = FileVersion
        django_get_or_create = ["version"]
