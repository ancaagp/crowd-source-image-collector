from .models import Project, Image, ModelHistory
from .forms import ProjectForm, ModelHistoryForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from tasks.mltasks import train_model_task, predict_model_task

from api.amazon.s3_helper import upload_file

from image_collector.settings import MEDIA_ROOT

S3_BUCKET = 'crowd-source-image-collector'

# Create your views here.
@login_required
def home(request):
  projects = Project.objects.all()
  return render(request, 'projects/index.html', {'projects': projects })

def about(request):
  return render(request, 'about.html')

@login_required
def projects(request):
	projects = Project.objects.all()
	return render(request, 'projects/index.html', {'projects': projects })

@login_required
def projects_detail(request, project_id):
	project = Project.objects.get(id=project_id)
	images = Image.objects.filter(project=project_id)
	tests = ModelHistory.objects.filter(project=project_id)
	return render(request, 'projects/detail.html', { 
		'project': project, 
		'images': images,
		'tests' : tests 
	})

@login_required
def projects_edit(request, project_id):
	project = Project.objects.get(id=project_id)
	project_form = ProjectForm(instance=project)
	return render(request, 'projects/edit.html', { 'project_form': project_form, 'project': project })

@login_required
def projects_delete(request, project_id):
	project = Project.objects.get(id=project_id)
	project.delete()
	return redirect('/projects/')

@login_required
def new_project(request):
	project_form = ProjectForm()
	return render(request, 'projects/new.html', { 'project_form': project_form })

@login_required
def edit_project(request, project_id):
	project = Project.objects.get(id=project_id)
	form = ProjectForm(request.POST, instance=project)
	if form.is_valid():
		new_project = form.save(commit=False)
		new_project.save()
	return redirect('/projects/')

@login_required
def add_project(request):
	form = ProjectForm(request.POST)
	if form.is_valid():
		new_project = form.save(commit=False)
		new_project.save()
	return redirect('/projects/')

@login_required
def train_model(request, project_id):
	project = Project.objects.get(id=project_id)
	train_model_task.delay(project_id)
	project.model_status = 'Training'
	project.save()
	return redirect(f'/projects/{project_id}')

def save_file(file_object):
	file_name = file_object.name
	print("file_name", file_name)
	print("content_type", file_object.content_type)
	print("size", file_object.size)
	file_path = MEDIA_ROOT + "/" + file_name
	with open(file_path, 'wb+') as f:
		for chunk in file_object.chunks():
			f.write(chunk) 
	return file_path

@login_required
def test_model(request, project_id):
	project = Project.objects.get(id=project_id)
	if request.method == 'POST':
		form = ModelHistoryForm(request.POST, request.FILES)
		if form.is_valid():
			new_model_hist = form.save()
			
			# upload to s3
			try:
				file_path = new_model_hist.image.path
				file_name = file_path.split('/')[-1] 
				s3_path = f'predict/{project_id}/{file_name}'
				upload_file(new_model_hist.image.path, S3_BUCKET, s3_path)
			except Exception as e:
				print("Error uploading to s3: " + str(e))
			print(new_model_hist.image.path)
			file_name = new_model_hist.image.path.split('/')[-1]
			predict_model_task.delay(project_id, file_name, new_model_hist.id)

			return redirect(f'/projects/{project_id}')
	else:
		form = ModelHistoryForm()
	return render(request, 'projects/test_model.html', {
		'model_history_form': form,
		'project': project
	})

def test_model_old(request, project_id):
	project = Project.objects.get(id=project_id)
	if request.method == 'POST':
		try:
			print(request.POST)
			print(request.FILES)
			file_object = request.FILES['image']
			print(file_object)
			file_path = save_file(file_object)

			new_model_hist = ModelHistory.objects.create(**{'project': project, 'image': file_path})
			new_model_hist.save()
			
			print(f'image path: {file_path}')

			# upload to s3
			try:
				s3_path = f'results/{project_id}/'
				upload_file(new_model_hist.image.path, S3_BUCKET, s3_path)
			except Exception as e:
				print("Error uploading to s3: " + str(e))

			file_name = file_path.split('/')[-1]
			predict_model_task.delay(project_id, file_name, new_model_hist.id)

			return redirect(f'/projects/{project_id}')
		except Exception as e:
			print("Error saving the test file: " + str(e))
			raise e
	model_history_form = ModelHistoryForm()
	return render(request, 'projects/test_model.html', { 'project': project, 'model_history_form': model_history_form })
