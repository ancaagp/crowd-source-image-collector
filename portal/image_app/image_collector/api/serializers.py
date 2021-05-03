from rest_framework import serializers 
from main_app.models import Project, Image

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta():
        model = Image
        fields = '__all__'