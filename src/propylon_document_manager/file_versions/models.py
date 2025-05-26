from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models import CharField, EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    """Manager for custom user model with email as username."""

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    """
    Custom user model for Propylon Document Manager with email as username.
    """
    username = None  # remove username field
    first_name = None
    last_name = None

    name = CharField(_("Name of User"), blank=True, max_length=255)
    email = EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()  # Use the custom user manager

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view."""
        return reverse("users:detail", kwargs={"pk": self.id})

    def __str__(self):
        return self.email

def user_file_path(instance, filename):
    """
    Returns the custom path provided by user for file storage inside MEDIA_ROOT.
    Sanitizes input to avoid dangerous paths.
    """
    if instance.custom_path:
        safe_path = instance.custom_path.lstrip('/\\')
        return safe_path
    # fallback: store in user folder
    return f'user_{instance.user.id}/{filename}'

class FileVersion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="file_versions")
    file_name = models.CharField(max_length=512)
    custom_path = models.CharField(
        max_length=1024, blank=True, null=True,
        help_text="Custom relative path (e.g., reports/2024/myfile.pdf). Will store at MEDIA_ROOT/<custom_path>"
    )
    file = models.FileField(upload_to=user_file_path, blank=True, null=True)
    version_number = models.IntegerField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.version_number is None:
            last_version = FileVersion.objects.filter(
                user=self.user, file_name=self.file_name
            ).order_by("-version_number").first()
            self.version_number = 0 if not last_version else last_version.version_number + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.file_name} (v{self.version_number})"
