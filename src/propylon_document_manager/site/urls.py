from django.conf import settings
from django.urls import include, path, re_path
# from rest_framework.authtoken.views import obtain_auth_token

from propylon_document_manager.file_versions.api.views import FileView
from propylon_document_manager.users.views import UserLogin, UserLogout, UserRegister, UserView

# API URLS
urlpatterns = [
    # API base url
    path("api/", include("propylon_document_manager.site.api_router")),
    # DRF auth token
    # path("api-auth/", include("rest_framework.urls")),
    # path("auth-token/", obtain_auth_token),
    re_path(r'^files/(?P<file_path>.+)$', FileView.as_view()),
    path('register/', UserRegister.as_view(), name='register'),
    path('login/', UserLogin.as_view(), name='login'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('user/', UserView.as_view(), name='user'),
]

if settings.DEBUG:
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
