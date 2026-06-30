import os

from django.contrib.auth.models import AbstractUser
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

# updated file version model to include file storage fields and required meta data for versioning and ordering of file versions
# now stores url path
class FileVersion(models.Model):
    url_path = models.CharField(max_length=1024, blank=True, default="", db_index=True)
    file = models.FileField(upload_to="uploads/%Y/%m/%d", blank=True, null=True)
    file_name = models.CharField(max_length=512)
    version_number = models.PositiveIntegerField(default=1)
    content_type = models.CharField(max_length=255, blank=True, default="")
    file_size = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # versioning logic: when a new file version is created, increment the version number based on the latest version of the same file name  
    class Meta:
        ordering = ["-uploaded_at", "-version_number"]

    # save logic to handle versioning and file storage fields
    def save(self, *args, **kwargs):
        if self._state.adding:
            if self.url_path:
                latest_version = (
                    FileVersion.objects.filter(url_path=self.url_path).order_by("-version_number").first()
                )
            else:
                latest_version = (
                    FileVersion.objects.filter(file_name=self.file_name).order_by("-version_number").first()
                )
            self.version_number = (latest_version.version_number if latest_version else 0) + 1
        super().save(*args, **kwargs)

    # string representation of the file version model
    def __str__(self) -> str:
        return self.file_name or self.file.name or "Untitled file"
