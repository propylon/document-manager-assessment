from rest_framework import serializers

from ..models import FileVersion, User

class FileVersionSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FileVersion
        fields = "__all__"
        read_only_fields = ('user', 'version_number', 'uploaded_at')
        extra_kwargs = {
            'file': {'required': True},
            'custom_path': {'required': False},
            'version_number': {'read_only': True},  # <--- Explicitly read-only
        }

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def create(self, validated_data):
        # Set the user from the request context
        user = self.context['request'].user
        validated_data['user'] = user
        # version_number will auto-increment in model's save()
        return super().create(validated_data)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("email", "password", "name")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            name=validated_data.get("name", ""),
        )
        return user
