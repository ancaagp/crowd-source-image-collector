from django.shortcuts import render

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from main_app.models import Project, Image, ModelHistory
from api.serializers import ProjectSerializer, ImageSerializer

from api.amazon.s3_helper import upload_file

from django.conf import settings
from django.conf.urls.static import static

import shutil
import os
import os.path 

S3_BUCKET = 'crowd-source-image-collector'

def move_file_proper_folder(filepath, label, project_id):
    
    filename = filepath.split("/")[-1]
    original_filepath = f'{settings.MEDIA_ROOT}/{filename}'

    project_path = f'{settings.MEDIA_ROOT}/{project_id}'
    if not os.path.isdir(project_path):
        os.mkdir(project_path)

    label_path = f'{project_path}/{label}'
    if not os.path.isdir(label_path):
        os.mkdir(label_path)

    new_filepath = f'{label_path}/{filename}'

    shutil.move(original_filepath, new_filepath)
    return new_filepath

def upload_file_to_s3(filename, label, project_id):
    file_path = os.path.abspath(f'/image_collector/{filename}')
    file_name = file_path.split('/')[-1]
    s3_object_path = f'{project_id}/{label}/{file_name}'
    upload_file(file_path, S3_BUCKET, s3_object_path)

@api_view(['GET'])
def projects(request):
    if request.method == 'GET':
        projects = Project.objects.all()
        projects_serializer = ProjectSerializer(projects, many=True)
        return JsonResponse(projects_serializer.data, safe=False)
        # 'safe=False' for objects serialization


class ModelHistoryView(APIView):
    """
    A view that can accept POST requests with JSON content.
    """
    parser_classes = [JSONParser]

    def post(self, request, format=None):

        model_hist_id = request.data['test_id']
        score = request.data['score']
        predicted_label = request.data['label']
        project_id = request.data['project_id']
        
        project = Project.objects.get(id=project_id)

        model_hist = ModelHistory.objects.get(id=model_hist_id)

        model_hist.score = score
        model_hist.predicted_label = predicted_label
        model_hist.project = project
        model_hist.save()

        return Response({'success': True})

class ImageApiView(APIView):
    # MultiPartParser AND FormParser
    # https://www.django-rest-framework.org/api-guide/parsers/#multipartparser
    # "You will typically want to use both FormParser and MultiPartParser
    # together in order to fully support HTML form data."
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        file_serializer = ImageSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()

            image_path = file_serializer.data['image']
            project = file_serializer.data['project']
            label = file_serializer.data['label']
            
            # upload file to s3
            upload_file_to_s3(image_path, label, project)

            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, project_id):
        images = Image.objects.filter(project=project_id)
        images_serializer = ImageSerializer(images, many=True)
        return JsonResponse(images_serializer.data, safe=False)
