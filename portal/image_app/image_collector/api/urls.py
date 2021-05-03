from django.conf.urls import url
from django.urls import path, include
from . import views

urlpatterns = [
    path('projects', views.projects, name='projects'),
    path('images', views.ImageApiView.as_view(), name='images'),
    path('images/<int:project_id>', views.ImageApiView.as_view(), name='images'),
    path('tests', views.ModelHistoryView.as_view(), name='tests')
]