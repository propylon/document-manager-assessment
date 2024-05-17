from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import FileVersion


User = get_user_model()

class FileVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileVersion
        read_only_fields = ['version_number', 'author']
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):

    files = serializers.PrimaryKeyRelatedField(many=True, queryset=FileVersion.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'files']
