from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from rest_framework.authtoken.views import obtain_auth_token

# API URLS
urlpatterns = [
    # API base url
    path("", RedirectView.as_view(url="/home/"), name="home"),
    path("api/", include("propylon_document_manager.site.api_router")),
    # DRF auth token
    path(
        "api-auth/logout/", RedirectView.as_view(url="/accounts/logout/")
    ),  # this is just to use django rest, but I'm using allauth
    path("api-auth/login/", RedirectView.as_view(url="/accounts/login")),
    path("api-auth/", include("rest_framework.urls")),
    path("accounts/", include("allauth.urls")),
    path("auth-token/", obtain_auth_token),
    path("home/", include("propylon_document_manager.file_versions.urls")),
]

if settings.DEBUG:
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
