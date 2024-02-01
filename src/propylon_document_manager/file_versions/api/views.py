from rest_framework.views import APIView

from .view_helpers import delete_file, delete_file_version, get_file, upload_file


class FileView(APIView):
    """
    API endpoint that allows files to be viewed or edited.
    """
    def get(self, request, file_url, format=None):
        version = request.query_params.get("version")
        return get_file(request, file_url, version)

    def post(self, request, file_url, format=None):
        return upload_file(request, file_url)

    def delete(self, request, file_url, format=None):
        version = request.query_params.get("version")

        if version:
            return delete_file_version(request, file_url, version)

        return delete_file(request, file_url)
