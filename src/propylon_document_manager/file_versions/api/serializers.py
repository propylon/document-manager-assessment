from rest_framework import serializers

from ..models import FileVersion, Document


class FileVersionSerializer(serializers.ModelSerializer):
    content = serializers.FileField(required=True)
    file_name = serializers.CharField(read_only=True)  # Dynamic field
    full_path = serializers.CharField(read_only=True)  # Dynamic field

    # def to_internal_value(self, data):
    #     data = super().to_internal_value(data)
    #     data.pop('content', None)  # Remove the 'file' field if it exists
    #     return data
    class Meta:
        model = FileVersion
        fields = "__all__"
        read_only_fields = ['id', 'document', 'version_number', 'hash', 'created_at', 'owner']


class FileVersionResponseSerializer(serializers.BaseSerializer):
    responseCode = serializers.IntegerField()
    responseMessage = serializers.CharField()
    filePath = serializers.URLField()
    revisionNumber = serializers.IntegerField()


class DocumentSerializer(serializers.ModelSerializer):
    file_version_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields = ['id', 'file_name', 'path', 'owner', 'latest_version_number', 'created_at', 'modified_at']

    # def validate_file(self, value):
    #     # Add custom validation logic if needed
    #     if value.size > 10 * 1024 * 1024:  # Example: Limit file size to 10MB
    #         raise serializers.ValidationError("File size exceeds the 10MB limit.")
    #     return value
