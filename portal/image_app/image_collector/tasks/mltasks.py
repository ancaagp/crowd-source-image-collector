from celery import shared_task
from celery.decorators import task

from main_app.models import Project

import time
import requests

TENSORFLOW_WORKER_HOST = 'http://tfworker:4000/commands'

def execute_job_on_tensorflow_worker(job, arguments, timeout=600):
    data = {"args": arguments, "timeout": timeout}
    resp = requests.post(f"{TENSORFLOW_WORKER_HOST}/{job}", json=data)
    results = resp.json()
    print(results)
    return results['result_url'], results['status']

def follow_up_on_job(url):
    resp = requests.get(url)
    resp = resp.json()
    print(resp)
    if 'status' in resp:
        return resp['status'], -1
    else:
        return resp['error'], resp['returncode']

@task(name="train_model_task")
def train_model_task(project_id):
    project = Project.objects.get(id=project_id)
    status = 'Training'
    try:
        url, status = execute_job_on_tensorflow_worker('python', ['train_model.py', str(project_id)])
        if status != 'running':
            status = 'Error'
        
        return_code = -1
        while return_code == -1:
            time.sleep(1)
            status, return_code = follow_up_on_job(url)
            print("status is: " + status)

        status = 'Error' if return_code == 1 else 'Training Completed'

    except Exception as err:
        print("Error: {0}".format(err))
        status = 'Error'

    print(f'FINISHED TASK. Status {status}')
    project.model_status = status
    project.save()
    return True

@task(name="predict_model_task")
def predict_model_task(project_id, test_image, test_id):
    status = 'Running'
    try:
        url, status = execute_job_on_tensorflow_worker('python', ['predict_model.py', str(project_id), test_image, str(test_id)])
        if status != 'running':
            status = 'Error'
        
        return_code = -1
        while return_code == -1:
            time.sleep(1)
            status, return_code = follow_up_on_job(url)
            print("status is: " + status)

        status = 'Error' if return_code == 1 else 'Task Completed'

    except Exception as err:
        print("Error: {0}".format(err))
        status = 'Error'

    print(f'FINISHED TASK. Status {status}')
    return True