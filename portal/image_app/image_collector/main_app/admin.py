from django.contrib import admin
from .models import Project, Image, ModelHistory

# Register your models here.
admin.site.register(Project)
admin.site.register(Image)
admin.site.register(ModelHistory)