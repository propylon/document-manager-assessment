from rest_framework import serializers

from ..models import FileVersion


class FileVersionSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    file_name = serializers.CharField(required=False, allow_blank=True)
    file_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FileVersion
        fields = ["id", "file", "file_name", "version_number", "content_type", "file_size", "file_url", "uploaded_at"]
        read_only_fields = ["id", "version_number", "content_type", "file_size", "file_url", "uploaded_at"]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if request is not None and obj.file:
            return request.build_absolute_uri(obj.file.url)
        if obj.file:
            return obj.file.url
        return None

    def create(self, validated_data):
        uploaded_file = validated_data.pop("file")
        file_name = validated_data.pop("file_name", None) or uploaded_file.name
        existing_versions = FileVersion.objects.filter(file_name=file_name).count()
        file_version = FileVersion(
            file=uploaded_file,
            file_name=file_name,
            version_number=existing_versions + 1,
            content_type=getattr(uploaded_file, "content_type", None) or "application/octet-stream",
            file_size=uploaded_file.size,
        )
        file_version.save()
        return file_version
