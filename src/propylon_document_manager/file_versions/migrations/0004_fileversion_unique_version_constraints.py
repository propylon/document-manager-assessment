from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("file_versions", "0003_alter_fileversion_options"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="fileversion",
            constraint=models.UniqueConstraint(
                condition=~models.Q(url_path=""),
                fields=("url_path", "version_number"),
                name="uniq_fileversion_url_path_version",
            ),
        ),
        migrations.AddConstraint(
            model_name="fileversion",
            constraint=models.UniqueConstraint(
                condition=models.Q(url_path=""),
                fields=("file_name", "version_number"),
                name="uniq_fileversion_name_version_no_url",
            ),
        ),
    ]
