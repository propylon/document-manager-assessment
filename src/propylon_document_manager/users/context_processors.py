from django.conf import settings

def allauth_settings(request):
    return {'allauth_settings': settings.AUTHENTICATION_BACKENDS}
