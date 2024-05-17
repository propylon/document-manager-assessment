from typing_extensions import ReadOnly
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models import CharField, EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


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
    objects = CustomUserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})


class FileVersion(models.Model):
    file_name = models.fields.CharField(max_length=512)
    version_number = models.fields.PositiveIntegerField(default=1)
    # user = models.ForeignKey('auth.User', related_name='files', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='files', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('file_name', 'version_number', 'author')
        ordering = ['-version_number']

    def save(self, *args, **kwargs):
        # import pdb; pdb.set_trace()
        if self.pk is None:  # Check if new object
            existing = FileVersion.objects.filter(author=self.author, file_name=self.file_name).order_by('-version_number').first()
            if existing:
                self.version_number = existing.version_number + 1
        super().save(*args, **kwargs)
