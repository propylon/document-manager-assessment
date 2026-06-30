from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("file_versions", "0004_fileversion_unique_version_constraints"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="fileversion",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name="file_versions",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RemoveConstraint(
            model_name="fileversion",
            name="uniq_fileversion_url_path_version",
        ),
        migrations.RemoveConstraint(
            model_name="fileversion",
            name="uniq_fileversion_name_version_no_url",
        ),
        migrations.AddConstraint(
            model_name="fileversion",
            constraint=models.UniqueConstraint(
                condition=(~models.Q(url_path="") & models.Q(owner__isnull=False)),
                fields=("owner", "url_path", "version_number"),
                name="uniq_fileversion_owner_url_path_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="fileversion",
            constraint=models.UniqueConstraint(
                condition=(models.Q(url_path="") & models.Q(owner__isnull=False)),
                fields=("owner", "file_name", "version_number"),
                name="uniq_fileversion_owner_name_version_no_url",
            ),
        ),
    ]
