from django.forms import ModelForm
from .models import Project, ModelHistory

class ProjectForm(ModelForm):
  class Meta:
    model = Project
    fields = ['name', 'description', 'labels', 'images_per_class', 'budget']


class ModelHistoryForm(ModelForm):
  class Meta:
    model = ModelHistory
    fields = ['image']