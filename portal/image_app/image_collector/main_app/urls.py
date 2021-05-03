from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('projects/', views.projects, name='projects'),
    path('projects/<int:project_id>', views.projects_detail, name='detail'),
    path('projects/edit/<int:project_id>', views.projects_edit, name='edit'),
    path('projects/delete/<int:project_id>', views.projects_delete, name='delete'),
    path('projects/add_project', views.add_project,name='add_project'),
    path('projects/edit_project/<int:project_id>', views.edit_project,name='edit_project'),
    path('projects/new', views.new_project,name='new_project'),
    path('projects/train_model/<int:project_id>', views.train_model,name='train_model'),
    path('projects/test_model/<int:project_id>', views.test_model,name='test_model')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)