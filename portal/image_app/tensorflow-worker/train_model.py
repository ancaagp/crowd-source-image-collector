import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

import logging
import sys
import argh
import os
import json

S3_BUCKET = 'crowd-source-image-collector'

def copy_files_from_s3(project_id):
    files_path = f'/py/files/{project_id}/'
    os.system(f'mkdir -p {files_path}')
    os.system(f"aws s3 sync s3://{S3_BUCKET}/{project_id}/ {files_path}")
    logging.info(f'Copied files from s3 to {files_path}')
    return files_path

def train_model(project_id, train_folder, test_folder, model_path, epochs=20):

    os.system(f'mkdir -p {model_path}')

    # using MirroredStrategy to use multiple gpus for the job
    strategy = tf.distribute.MirroredStrategy()
    
    BATCH_SIZE_PER_REPLICA = 64
    BATCH_SIZE = BATCH_SIZE_PER_REPLICA * strategy.num_replicas_in_sync

    img_height = 72
    img_width = 72
    
    print(f'train folder: {train_folder}')
    print(f'test folder: {test_folder}')

    # creating training and validation sets
    train_ds = tf.keras.preprocessing.image_dataset_from_directory(
        train_folder,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=(img_height, img_width),
        batch_size=BATCH_SIZE)

    val_ds = tf.keras.preprocessing.image_dataset_from_directory(
        test_folder,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=(img_height, img_width),
        batch_size=BATCH_SIZE)

    class_names = train_ds.class_names
    num_classes = len(class_names)
    
    AUTOTUNE = tf.data.AUTOTUNE
    # optmization
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    with strategy.scope():

        data_augmentation = keras.Sequential(
            [
                layers.experimental.preprocessing.RandomFlip("horizontal", input_shape=(img_height, img_width,3)),
                layers.experimental.preprocessing.RandomRotation(0.1),
                layers.experimental.preprocessing.RandomZoom(0.1),
            ]
        )

        # creating model config
        model = Sequential([
            data_augmentation,
            layers.experimental.preprocessing.Rescaling(1./255, input_shape=(img_height, img_width, 3)),
            layers.Conv2D(16, 3, padding='same', activation='relu'),
            layers.MaxPooling2D(),
            layers.Conv2D(32, 3, padding='same', activation='relu'),
            layers.MaxPooling2D(),
            layers.Conv2D(64, 3, padding='same', activation='relu'),
            layers.MaxPooling2D(),
            layers.Dropout(0.2),
            layers.Flatten(),
            layers.Dense(128, activation='relu'),
            layers.Dense(num_classes)
        ])

        model.compile(optimizer='adam',
            loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            metrics=['accuracy'])

        model.summary()

        # training the model
        history = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=epochs
        )

        # saving model
        model.save(model_path, save_format='tf')

        save_class_names(class_names, project_id)

        logging.info('Model trained')

def upload_model_to_s3(model_path, project):
    os.system(f'aws s3 sync {model_path} s3://{S3_BUCKET}/results/{project}/')

def save_class_names(class_names, project):
    with open(f'./files/model/{project}/classes.json', 'w') as f:
        f.write(json.dumps(class_names))

@argh.arg('project', help='Project id')
def main(project):
    files_path = copy_files_from_s3(project)
    model_path = f'./files/model/{project}/'
    train_model(project, files_path, files_path, model_path)
    upload_model_to_s3(model_path, project)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s: %(levelname)s: %(name)s: %(message)s",
                        stream=sys.stdout)
    parser = argh.dispatch_command(main)