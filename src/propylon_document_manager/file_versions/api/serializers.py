from django.contrib.auth import get_user_model
from rest_framework import serializers

from propylon_document_manager.users.serializers import UserSerializer

from ..models import File, FileVersion

User = get_user_model()


class FileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    write_users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())

    class Meta:
        model = File
        fields = ['url', 'file_name', 'user', 'write_users']

    def create(self, validated_data):
        write_users = validated_data.pop('write_users')
        file = File.objects.create(**validated_data)
        file.write_users.set(write_users)
        return file

    def update(self, instance, validated_data):
        instance.url = validated_data.get('url', instance.url)
        instance.file_name = validated_data.get('file_name', instance.file_name)
        if 'write_users' in validated_data:
            instance.write_users.set(validated_data['write_users'])
        instance.save()
        return instance


class FileVersionSerializer(serializers.ModelSerializer):
    file = FileSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    read_users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())

    class Meta:
        model = FileVersion
        fields = ['file', 'version', 'content', 'hash', 'uploaded_at', 'user', 'read_users']

    def create(self, validated_data):
        read_users = validated_data.pop('read_users')
        file_version = FileVersion.objects.create(**validated_data)
        file_version.read_users.set(read_users)
        return file_version

    def update(self, instance, validated_data):
        instance.version = validated_data.get('version', instance.version)
        instance.content = validated_data.get('content', instance.content)
        instance.hash = validated_data.get('hash', instance.hash)
        if 'read_users' in validated_data:
            instance.read_users.set(validated_data['read_users'])
        instance.save()
        return instance
