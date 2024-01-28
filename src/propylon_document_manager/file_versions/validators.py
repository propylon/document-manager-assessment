import re

from django.core.exceptions import ValidationError


def file_url(file_path: str):
    """
    Validate url for a file, which must start with '/' and end with a file name and its extension.

    Examples:
        - /myurl/testurl.pdf
        - /myurl/testurl.txt
        - /myurl/testurl.doc

    Args:
        file_path (str): url for a file

    Raises:
        ValidationError: if file_path does not match the pattern
    """
    pattern = r'^/[\w-]+(/[\w-]+)*\.\w+$'
    message = (
        '''Invalid file URL, please try again.''' \
        '''It must start with \'/\' and end with file name and its extension (any)'''
    )
    if not re.match(pattern, file_path):
        raise ValidationError(message)
