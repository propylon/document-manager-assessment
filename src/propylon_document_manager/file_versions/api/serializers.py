from rest_framework import serializers

from ..models import FileVersion, Document


class FileVersionSerializer(serializers.ModelSerializer):
    content = serializers.FileField(required=True)

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


class FileInputSerializer(serializers.Serializer):
    file = serializers.FileField()

    # def validate_file(self, value):
    #     # Add custom validation logic if needed
    #     if value.size > 10 * 1024 * 1024:  # Example: Limit file size to 10MB
    #         raise serializers.ValidationError("File size exceeds the 10MB limit.")
    #     return value
