from django.contrib.auth.models import AbstractUser
from django.db import IntegrityError, models, transaction
from django.db.models import CharField, EmailField
from django.db.models import Q
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
    url_path = models.CharField(max_length=1024, blank=True, default="", db_index=True)
    file = models.FileField(upload_to="uploads/%Y/%m/%d", blank=True, null=True)
    file_name = models.CharField(max_length=512)
    version_number = models.PositiveIntegerField(default=1)
    content_type = models.CharField(max_length=255, blank=True, default="")
    file_size = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at", "-version_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["url_path", "version_number"],
                condition=~Q(url_path=""),
                name="uniq_fileversion_url_path_version",
            ),
            models.UniqueConstraint(
                fields=["file_name", "version_number"],
                condition=Q(url_path=""),
                name="uniq_fileversion_name_version_no_url",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            return super().save(*args, **kwargs)

        for _ in range(3):
            try:
                with transaction.atomic():
                    if self.url_path:
                        latest_version = (
                            FileVersion.objects.select_for_update()
                            .filter(url_path=self.url_path)
                            .order_by("-version_number")
                            .first()
                        )
                    else:
                        latest_version = (
                            FileVersion.objects.select_for_update()
                            .filter(url_path="", file_name=self.file_name)
                            .order_by("-version_number")
                            .first()
                        )
                    self.version_number = (latest_version.version_number if latest_version else 0) + 1
                    return super().save(*args, **kwargs)
            except IntegrityError:
                continue
        raise IntegrityError("Could not assign a unique version_number after retries.")

    def __str__(self) -> str:
        return self.file_name or self.file.name or "Untitled file"
