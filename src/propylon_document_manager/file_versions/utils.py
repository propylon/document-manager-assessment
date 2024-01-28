from django.contrib.auth.decorators import login_required
from rest_framework import status
from rest_framework.response import Response

from .api.serializers import FileVersionSerializer
from .models import File, FileVersion


@login_required
def get_file(request, file_url, version=None):
    try:
        # Check if the file exists
        file = File.objects.get(url=file_url)

        # Get the requested version of the file, or the latest version if no version is provided
        if version is not None:
            file_version = FileVersion.objects.get(file=file, version=version)
        else:
            file_version = FileVersion.objects.filter(file=file).latest('uploaded_at')

        # Check if the user is either the creator or has permission to access the file version
        if file_version.user != request.user and request.user not in file_version.read_users.all():
            return Response(
                {'detail': 'You do not have permission to access this file.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Return the file content
        # return HttpResponse(file_version.content, content_type='application/octet-stream')
        serializer = FileVersionSerializer(file_version)
        return Response(serializer.data)

    except File.DoesNotExist:
        return Response({'detail': 'File not found.'}, status=status.HTTP_404_NOT_FOUND)
    except FileVersion.DoesNotExist:
        return Response({'detail': 'No versions of this file found.'}, status=status.HTTP_404_NOT_FOUND)


@login_required
def upload_file(request, file_url):
    try:
        # Check if the file exists
        file = File.objects.get(url=file_url)

        # Check if the user has permission to upload a new version of the file
        if file.user != request.user and request.user not in file.write_users.all():
            return Response(
                {'detail': 'You do not have permission to upload a new version of this file.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Create a new version of the file
        new_version_number = file.versions.count() + 1
        new_file_version = FileVersion.objects.create(
            file=file,
            version=new_version_number,
            content=request.FILES['file'],
            user=request.user
        )
        new_file_version.read_users.add(file.user, request.user)

        serializer = FileVersionSerializer(new_file_version)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except File.DoesNotExist:
        return Response({'detail': 'File not found.'}, status=status.HTTP_404_NOT_FOUND)


@login_required
def delete_file(request, file_url):
    try:
        file = File.objects.get(url=file_url)
        if file.user != request.user:
            return Response(
                {'detail': 'You do not have permission to delete this file.'},
                status=status.HTTP_403_FORBIDDEN
            )
        file.delete()
        return Response({'detail': 'File deleted.'}, status=status.HTTP_204_NO_CONTENT)

    except File.DoesNotExist:
        return Response({'detail': 'File not found.'}, status=status.HTTP_404_NOT_FOUND)


@login_required
def delete_file_version(request, file_url, version):
    try:
        file = File.objects.get(url=file_url)
        file_version = FileVersion.objects.get(file=file, version=version)
        if file_version.user != request.user:
            return Response(
                {'detail': 'You do not have permission to delete this file version.'},
                status=status.HTTP_403_FORBIDDEN
            )
        file_version.delete()
        return Response({'detail': 'File version deleted.'}, status=status.HTTP_204_NO_CONTENT)

    except File.DoesNotExist:
        return Response({'detail': 'File not found.'}, status=status.HTTP_404_NOT_FOUND)
    except FileVersion.DoesNotExist:
        return Response({'detail': 'File version not found.'}, status=status.HTTP_404_NOT_FOUND)
