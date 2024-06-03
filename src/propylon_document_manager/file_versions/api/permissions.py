import logging
from rest_framework.permissions import BasePermission
from ..models import FileVersion


logger = logging.getLogger(__name__)


class IsAuthor(BasePermission):
    def has_permission(self, request, view):
        # Allow only if the user is the files creator
        if request.method in ['POST', 'PUT', 'GET', 'DELETE']:
            # import pdb; pdb.set_trace()
            try:
                file_name = view.kwargs['filename']
                existing = FileVersion.objects.filter(author=request.user, file_name=file_name).order_by('-version_number').first()
                if not existing:
                    raise FileVersion.DoesNotExist
                return True
            except FileVersion.DoesNotExist:
                return True  # Allow creation for non-existing file

        logger.warning(f"User does not have permissions {request.user.email}")
        return False
