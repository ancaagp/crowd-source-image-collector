import numpy as np
import tensorflow as tf
import os
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

# using MirroredStrategy to use multiple gpus for the job
strategy = tf.distribute.MirroredStrategy()
print('Number of devices: {}'.format(strategy.num_replicas_in_sync))

BATCH_SIZE_PER_REPLICA = 64
BATCH_SIZE = BATCH_SIZE_PER_REPLICA * strategy.num_replicas_in_sync

img_height = 72
img_width = 72
data_folder= '/scratch/project_2000859/BDA2021/agapianc/data'
train_folder = f'{data_folder}/train'
test_folder = f'{data_folder}/test'

print(f'Using Batch size of {BATCH_SIZE}.')

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
print(f'Num classes: {num_classes}')

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

    # Define the checkpoint directory to store the checkpoints
    checkpoint_dir = f'{data_folder}/checkpoint'
    # Name of the checkpoint files
    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")

    # adding a callback to checkpoint the model during the epochs
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_prefix,
                                       save_weights_only=True)
    ]

    # training the model
    epochs=20
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=callbacks
    )

    # function used to test the accuracy of the model
    def predict(url, name):
        print(f'Trying to predict this {name}.')
        path = tf.keras.utils.get_file(name, origin=url)
        img = keras.preprocessing.image.load_img(
            path, target_size=(img_height, img_width)
        )
        img_array = keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0) # Create a batch
        predictions = model.predict(img_array)
        score = tf.nn.softmax(predictions[0])

        print(
            "This image most likely belongs to {} with a {:.2f} percent confidence."
            .format(class_names[np.argmax(score)], 100 * np.max(score))
        )
    
    # checking if the model recognizes the pizza and the apple pie
    pizza_url = 'https://wolt-menu-images-cdn.wolt.com/menu-images/55fff2c4def54a6c86e71bd8/eef56978-6c62-11eb-a5ab-92a925219794_20210210_supreme_1200x800px_wolt.jpeg'
    predict(pizza_url,'pizza')
    
    apple_pie_url = 'https://www.inspiredtaste.net/wp-content/uploads/2019/10/Homemade-Apple-Pie-Recipe-6-1200.jpg'
    predict(apple_pie_url,'apple pie')

    # saving model
    path = f'{data_folder}/saved_model'
    model.save(path, save_format='tf')