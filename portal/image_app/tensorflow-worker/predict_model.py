import numpy as np
import tensorflow as tf
import os
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

import logging
import sys
import argh
import os
import json
import requests

S3_BUCKET = 'crowd-source-image-collector'

# TODO: Improve this
def download_model_from_s3(project_id):
	s3_model_path = f's3://{S3_BUCKET}/results/{project_id}/'
	local_model_path = f'./files/model/{project_id}'    
	os.system(f'mkdir -p {local_model_path}')
	os.system(f'aws s3 sync {s3_model_path} {local_model_path}')
	return local_model_path

# TODO: Improve this
def copy_file_from_s3(project_id, file):
	files_path = os.path.abspath(f'./files/{project_id}/predict/')
	os.system(f'mkdir -p {files_path}')
	os.system(f"aws s3 cp s3://{S3_BUCKET}/predict/{project_id}/{file} {files_path}")
	logging.info(f'Copied files from s3 to {files_path}')
	return f'{files_path}/{file}'

def predict(model_path, image_file):
	print(f'Trying to predict this {image_file}.')
	img_w, img_h = 72,72
	image_file = os.path.abspath(image_file)
	image = keras.preprocessing.image.load_img(image_file, target_size=(img_h, img_w))
	img_array = keras.preprocessing.image.img_to_array(image)
	img_array = tf.expand_dims(img_array, 0) # Create a batch
	model = keras.models.load_model(model_path)
	predictions = model.predict(img_array)
	score = tf.nn.softmax(predictions[0])
	class_index = np.argmax(score)
	class_names = load_class_array(model_path)
	print(
		"This image most likely belongs to {} with a {:.2f} percent confidence."
		.format(class_names[class_index], 100 * np.max(score))
	)
	return np.max(score).item(), class_names[class_index]

def load_class_array(model_path):
	with open(f'{model_path}/classes.json', 'r') as f:
		return json.loads(f.read())

def write_last_prediction(score, class_name, test_image):
	results_file = f'./files/model/{project}/result.json'
	with open(results_file, 'w') as f:
		f.write(json.dumps({
			'score': score,
			'class_name': class_name
		}))
	os.system(f'aws s3 cp {results_file} s3://{S3_BUCKET}/results/{project}/')

def update_test(score, label, test_id, project_id):
	resp = requests.post('http://app:8000/api/tests',  json={
        'test_id': int(test_id), 
        'score': score, 
        'label': label,
        'project_id': int(project_id) }
    )
	print(resp.text)

@argh.arg('project', help='Project id')
@argh.arg('test_image', help='Test image name')
@argh.arg('test_id', help='Test Id')
def main(project, test_image, test_id):
	model_path = download_model_from_s3(project)
	test_image = copy_file_from_s3(project, test_image)
	score, class_name = predict(model_path, test_image)
	update_test(score, class_name, test_id, project)

if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO,
						format="%(asctime)s: %(levelname)s: %(name)s: %(message)s",
						stream=sys.stdout)
	parser = argh.dispatch_command(main)

