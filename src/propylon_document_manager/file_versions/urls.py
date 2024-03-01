from django.urls import path
from . import views

urlpatterns = [
    path('', views.FileVersionViewSet.as_view({'get': 'list'}), name='index'),
]