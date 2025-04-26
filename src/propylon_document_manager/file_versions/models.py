from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, EmailField
from django.urls import reverse
from django.utils.timezone import now
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
    username = CharField(_("username"), max_length=150, unique=True, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})


class Document(models.Model):
    file_name = models.fields.CharField(max_length=512)
    path = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    latest_version_number = models.fields.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=now)
    modified_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.path} (Owned by {self.owner.username})"


def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    user = instance.owner.pk
    # path = instance.document.path
    ver = instance.version_number
    basename, ext = filename.rsplit('.', 1)
    return f'storage/user_{user}/{basename}_v{ver}.{ext}'


class FileVersion(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True, related_name='revisions')
    content = models.FileField(upload_to=user_directory_path, null=True)
    version_number = models.fields.PositiveIntegerField()
    hash = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('document', 'version_number')
        ordering = ['-version_number']
        indexes = [
            models.Index(fields=['hash'], name='hash_idx'),
        ]
