import hashlib
from django.db import transaction
from rest_framework import serializers
from ..models import Document, FileVersion


class FileVersionSerializer(serializers.ModelSerializer):
    url_path = serializers.CharField(write_only=True, required=False)
    file_name = serializers.CharField(required=False)
    document_path = serializers.CharField(source="document.url_path", read_only=True)

    class Meta:
        model = FileVersion
        fields = [
            "id",
            "document",
            "file_name",
            "version_number",
            "file",
            "content_hash",
            "created_at",
            "url_path",
            "document_path",
        ]
        read_only_fields = [
            "id",
            "document",
            "version_number",
            "content_hash",
            "created_at",
            "document_path",
        ]

    def create(self, validated_data):
        url_path = validated_data.pop("url_path", None)
        uploaded_file = validated_data.get("file")
        user = self.context["request"].user

        # Determine url_path: use provided value or fall back to file name
        if not url_path and uploaded_file:
            url_path = uploaded_file.name
        if not url_path:
            raise serializers.ValidationError({"url_path": "url_path or file is required."})

        with transaction.atomic():
            # Get or create the Document for this user + url_path
            document, _ = Document.objects.get_or_create(
                user=user,
                url_path=url_path,
            )

            # Determine next version number (0-indexed) with lock to prevent race condition
            latest_version = (
                document.versions.select_for_update()
                .order_by("-version_number")
                .first()
            )
            next_version = (latest_version.version_number + 1) if latest_version else 0

            # Compute SHA-256 content hash
            content_hash = None
            if uploaded_file:
                sha256 = hashlib.sha256()
                for chunk in uploaded_file.chunks():
                    sha256.update(chunk)
                content_hash = sha256.hexdigest()
                uploaded_file.seek(0)  # reset file pointer after reading

            # Use original filename if file_name not explicitly provided
            if not validated_data.get("file_name") and uploaded_file:
                validated_data["file_name"] = uploaded_file.name

            validated_data["document"] = document
            validated_data["version_number"] = next_version
            validated_data["content_hash"] = content_hash

            return super().create(validated_data)
