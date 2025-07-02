from rest_framework import serializers

from ..models import FileVersion


class FileVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileVersion
        fields = "__all__"


class UploadFileVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileVersion
        fields = ['id', 'file_name', 'file', 'url_path', 'version_number', 'uploaded_at', 'content_hash']
        read_only_fields = ['version_number', 'uploaded_at', 'content_hash']

    def create(self, validated_data):
        user = self.context['request'].user
        url_path = validated_data['url_path']

        # Auto increment version
        latest_version = (
            FileVersion.objects.filter(url_path=url_path, uploaded_by=user)
                .order_by('-version_number')
                .first()
        )
        next_version = (latest_version.version_number + 1) if latest_version else 0
        validated_data['version_number'] = next_version
        validated_data['uploaded_by'] = user
        return super().create(validated_data)
