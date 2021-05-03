from django.db import models

# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=20, default='')
    description = models.TextField(max_length=250, default='')
    labels = models.CharField(max_length=200, default='', help_text='Comma separated list. Eg: class1,class2,class3')
    budget = models.IntegerField()
    images_per_class = models.IntegerField()
    model_status = models.CharField(max_length=20, default='Not Trained')
    
    def __str__(self):
        return self.name


class Image(models.Model):
    label = models.CharField(max_length=200, default='',null=True)
    description = models.CharField(max_length=200, default='',null=True)
    image = models.ImageField(upload_to='images', blank=False, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True)
    # foreign key to Project
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)

class ModelHistory(models.Model):
    score = models.FloatField(default=0.0)
    predicted_label = models.CharField(max_length=200, default='',null=True)
    image = models.ImageField(upload_to='images', blank=False, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True)
    # foreign key to Project
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
