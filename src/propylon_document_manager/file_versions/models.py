from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage
from django.db import models

from .validators import file_url

fs = FileSystemStorage(location=settings.MEDIA_ROOT)
UserModel = get_user_model()


class File(models.Model):
    """
    File model for Propylon Document Manager.

    Attributes:
        url (str): URL of the file.
        file_name (str): Name of the file.
        user (User): User who owns this file.
        write_users (list(User)): Users who can write to this file.
    """
    url = models.CharField(max_length=255, unique=True, validators=[file_url])
    file_name = models.CharField(max_length=255)
    user = models.ForeignKey(UserModel, related_name='owned_files', on_delete=models.CASCADE)
    write_users = models.ManyToManyField(UserModel, related_name='write_files')


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
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    read_users = models.ManyToManyField(UserModel, related_name='read_file_versions')
