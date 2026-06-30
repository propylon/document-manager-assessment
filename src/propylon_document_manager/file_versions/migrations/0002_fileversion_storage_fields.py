import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("file_versions", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="fileversion",
            name="url_path",
            field=models.CharField(blank=True, default="", db_index=True, max_length=1024),
        ),
        migrations.AddField(
            model_name="fileversion",
            name="content_type",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="fileversion",
            name="file",
            field=models.FileField(blank=True, null=True, upload_to="uploads/%Y/%m/%d"),
        ),
        migrations.AddField(
            model_name="fileversion",
            name="file_size",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="fileversion",
            name="uploaded_at",
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="fileversion",
            name="version_number",
            field=models.PositiveIntegerField(default=1),
        ),
    ]
