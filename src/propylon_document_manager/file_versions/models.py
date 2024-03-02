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


class FileVersion(models.Model):
    file_name = models.CharField(max_length=512)
    version_number = models.IntegerField(default=1)
    file_field = models.FileField(upload_to="uploads/%Y/%m/%d/")
    date = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=512)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="file_versions", blank=True, null=True)
    collaborators = models.ManyToManyField(User, related_name="collaborators", blank=True)

    def save(self, *args, **kwargs):
        existing_files = FileVersion.objects.filter(file_name=self.file_name)

        if existing_files.exists():
            latest_version = existing_files.order_by("-version_number").first()
            self.version_number = latest_version.version_number + 1

        super().save(*args, **kwargs)
