from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("file_versions", "0005_fileversion_owner_constraints"),
    ]

    operations = [
        migrations.AddField(
            model_name="fileversion",
            name="content_hash",
            field=models.CharField(blank=True, db_index=True, default="", max_length=64),
        ),
    ]
