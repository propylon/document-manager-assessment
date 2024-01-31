from django.contrib import admin

# Register your models here.
from propylon_document_manager.users.models import AppUser

admin.site.register(AppUser)
