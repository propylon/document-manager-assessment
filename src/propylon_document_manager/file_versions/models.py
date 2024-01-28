from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models import CharField, EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for Propylon Document Manager.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})


fs = FileSystemStorage(location=settings.MEDIA_ROOT)


class File(models.Model):
    """
    File model for Propylon Document Manager.

    Attributes:
        url (str): URL of the file.
        file_name (str): Name of the file.
        user (User): User who owns this file.
        write_users (list(User)): Users who can write to this file.
    """
    url = models.CharField(max_length=255, unique=True)
    file_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, related_name='owned_files', on_delete=models.CASCADE)
    write_users = models.ManyToManyField(User, related_name='write_files')


class FileVersion(models.Model):
    """
    File version model for Propylon Document Manager.

    Attributes:
        file (File): File that this version belongs to.
        version (int): Version number of this file.
        content (FileField): File content.
        hash (str): Hash of the file, used to check if the file is corrupt.
        uploaded_at (datetime): Datetime when the file was uploaded.
        user (User): User who uploaded this file.
        read_users (list(User)): Users who can read this file.
    """
    file = models.ForeignKey(File, related_name='versions', on_delete=models.CASCADE)
    version = models.IntegerField()
    content = models.FileField(storage=fs)
    hash = models.CharField(max_length=255, unique=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_users = models.ManyToManyField(User, related_name='read_file_versions')
