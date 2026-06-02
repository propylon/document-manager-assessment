import hashlib
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from propylon_document_manager.file_versions.models import FileVersion, Document, User

file_versions_data = [
    ("bill_document", 0, "Dummy content for bill_document - Draft 1"),
    ("bill_document", 1, "Dummy content for bill_document - Draft 2 (amended)"),
    ("bill_document", 2, "Dummy content for bill_document - Final version"),
    ("amendment_document", 0, "Dummy content for amendment_document - Draft 1"),
    ("amendment_document", 1, "Dummy content for amendment_document - Approved revision"),
    ("act_document", 0, "Dummy content for act_document - Published version"),
]

class Command(BaseCommand):
    help = "Load basic file version fixtures"

    def handle(self, *args, **options):
        # 1. Get or create a fixture user
        user, created = User.objects.get_or_create(
            email="fixture@example.com",
            defaults={"name": "Fixture User"},
        )
        if created:
            user.set_password("fixture123")
            user.save()
            self.stdout.write("Created fixture user: fixture@example.com / fixture123")

        # 2. Create documents and file versions
        created_count = 0
        for file_name, version, content_str in file_versions_data:
            url_path = f"documents/{file_name}.txt"
            document, _ = Document.objects.get_or_create(
                user=user,
                url_path=url_path
            )

            content = content_str.encode('utf-8')
            content_hash = hashlib.sha256(content).hexdigest()

            file_version, fv_created = FileVersion.objects.get_or_create(
                document=document,
                version_number=version,
                defaults={
                    "file_name": f"{file_name}.txt",
                    "content_hash": content_hash,
                }
            )
            if fv_created:
                file_version.file.save(f"{file_name}.txt", ContentFile(content))
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS('Successfully created %s new file versions' % created_count)
        )
