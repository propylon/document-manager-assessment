from django.contrib.auth.models import AbstractUser
import hashlib
from django.conf import settings
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
    # Owner-scoped document version record supporting URL-based storage and CAS lookup.
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="file_versions", null=True, blank=True)
    url_path = models.CharField(max_length=1024, blank=True, default="", db_index=True)
    file = models.FileField(upload_to="uploads/%Y/%m/%d", blank=True, null=True)
    content_hash = models.CharField(max_length=64, blank=True, default="", db_index=True)
    file_name = models.CharField(max_length=512)
    version_number = models.PositiveIntegerField(default=1)
    content_type = models.CharField(max_length=255, blank=True, default="")
    file_size = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at", "-version_number"]
        constraints = [
            # Prevent duplicate version numbers for the same owner+URL.
            models.UniqueConstraint(
                fields=["owner", "url_path", "version_number"],
                condition=~Q(url_path="") & Q(owner__isnull=False),
                name="uniq_fileversion_owner_url_path_version",
            ),
            # Fallback constraint when URL is blank and versioning is by file_name.
            models.UniqueConstraint(
                fields=["owner", "file_name", "version_number"],
                condition=Q(url_path="") & Q(owner__isnull=False),
                name="uniq_fileversion_owner_name_version_no_url",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            save_result = super().save(*args, **kwargs)
            if self.file and not self.content_hash:
                self.content_hash = self._calculate_content_hash()
                FileVersion.objects.filter(pk=self.pk).update(content_hash=self.content_hash)
            return save_result

        # Assign versions transactionally to avoid collisions under concurrent uploads.
        for _ in range(3):
            try:
                with transaction.atomic():
                    base_qs = FileVersion.objects.select_for_update()
                    if self.owner_id is not None:
                        base_qs = base_qs.filter(owner_id=self.owner_id)
                    else:
                        base_qs = base_qs.filter(owner__isnull=True)

                    if self.url_path:
                        latest_version = (
                            base_qs.filter(url_path=self.url_path)
                            .order_by("-version_number")
                            .first()
                        )
                    else:
                        latest_version = (
                            base_qs.filter(url_path="", file_name=self.file_name)
                            .order_by("-version_number")
                            .first()
                        )
                    self.version_number = (latest_version.version_number if latest_version else 0) + 1
                    save_result = super().save(*args, **kwargs)
                    if self.file and not self.content_hash:
                        self.content_hash = self._calculate_content_hash()
                        FileVersion.objects.filter(pk=self.pk).update(content_hash=self.content_hash)
                    return save_result
            except IntegrityError:
                continue
        raise IntegrityError("Could not assign a unique version_number after retries.")

    def _calculate_content_hash(self) -> str:
        # SHA-256 digest is used by the content-addressable retrieval endpoint.
        hasher = hashlib.sha256()
        with self.file.open("rb") as file_handle:
            for chunk in iter(lambda: file_handle.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def __str__(self) -> str:
        return self.file_name or self.file.name or "Untitled file"
