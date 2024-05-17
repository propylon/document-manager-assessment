from django.conf import settings
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

# API URLS
urlpatterns = [
    # API base url
    path("api/", include("propylon_document_manager.site.api_router")),
    # DRF auth token
    path("api-auth/", include("rest_framework.urls")),
    path("auth-token/", obtain_auth_token),
    path('accounts/', include('allauth.urls')),
]
# import pdb; pdb.set_trace()
if settings.DEBUG:
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
