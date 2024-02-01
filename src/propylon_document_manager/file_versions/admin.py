from django.contrib import admin

# Register your models here.
from propylon_document_manager.file_versions.models import File, FileVersion

admin.site.register(File)
admin.site.register(FileVersion)
