import os

from rest_framework import serializers

from ..models import FileVersion


class FileVersionSerializer(serializers.ModelSerializer):
    # Serializer for upload + metadata responses; version/content hash stay server-controlled.
    file = serializers.FileField(write_only=True)
    file_name = serializers.CharField(required=False, allow_blank=True)
    url_path = serializers.CharField(required=False, allow_blank=True, default="")
    file_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FileVersion
        fields = ["id", "file", "file_name", "url_path", "content_hash", "version_number", "content_type", "file_size", "file_url", "uploaded_at"]
        read_only_fields = ["id", "content_hash", "version_number", "content_type", "file_size", "file_url", "uploaded_at"]
        validators = []

    # get_file_url method to return the absolute URL of the uploaded file
    def get_file_url(self, obj):
        request = self.context.get("request")
        if request is not None and obj.file:
            return request.build_absolute_uri(obj.file.url)
        if obj.file:
            return obj.file.url
        return None

    # create method to handle file upload and versioning logic
    def create(self, validated_data):
        # Normalize URL path and infer file_name when caller omits it.
        uploaded_file = validated_data.pop("file")
        owner = validated_data.pop("owner", None)
        url_path = validated_data.pop("url_path", "") or ""
        url_path = url_path.strip("/")
        file_name = validated_data.pop("file_name", None) or os.path.basename(url_path) or uploaded_file.name
        file_version = FileVersion(
            owner=owner,
            url_path=url_path,
            file=uploaded_file,
            file_name=file_name,
            content_type=getattr(uploaded_file, "content_type", None) or "application/octet-stream",
            file_size=uploaded_file.size,
        )
        file_version.save()
        return file_version
