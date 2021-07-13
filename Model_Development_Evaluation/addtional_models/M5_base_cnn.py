import os, logging
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras import layers, models

logging.basicConfig(level=logging.INFO, filename='/home/scratch/lfeng/machine_learning/m5_base_cnn.log')
logging.info("[INFO] Reading pergrid_base csv...")

pergrid_base_path = '/home/scratch/lfeng/machine_learning/pergrid_base.csv'
pergrid_base_df = pd.read_csv(pergrid_base_path, sep=",")
df = pergrid_base_df.dropna()
df.set_index('grid_id', inplace=True)
logging.info("[INFO] pergrid_base csv shape: {}".format(df.shape))

inputPath = '/home/scratch/lfeng/machine_learning/nlcd_jpg'
images = []

logging.info("[START] Reading jpg image for each grid")

for i in df.index.values:
    imagePath = os.path.sep.join([inputPath, "nlcd_{}.jpg".format(i)])

    if not os.path.isfile(imagePath):
        print("{} does not exist".format(imagePath))
    else:
        image = tf.io.read_file(imagePath)
        image = tf.image.decode_jpeg(image, channels=3)
        image = tf.image.convert_image_dtype(image, tf.float32)
        image = tf.image.resize(image, [667, 667])
        images.append(image.numpy())
logging.info("[END] Reading jpg image for each grid")

# images = np.array(images) / 255.0
images = np.array(images)

split = train_test_split(df, images, test_size=0.2, random_state=42)
(trainAttrX, testAttrX, trainImagesX, testImagesX) = split
trainY = trainAttrX["tsr"]
testY = testAttrX["tsr"]

# ### Create the convolutional base
logging.info("[START] Constructing CNN Architecture")

inputShape = trainImagesX[0].shape
model = models.Sequential()
model.add(layers.Conv2D(filters=32, kernel_size=(5, 5), activation='relu', input_shape=inputShape))
model.add(layers.Conv2D(filters=64, kernel_size=(5, 5), strides=(2, 2), activation='relu'))
model.add(layers.Conv2D(filters=128, kernel_size=(5, 5), strides=(2, 2), activation='relu'))

# add dense layer to transform convolutional layer in 3d to 1d
model.add(layers.Flatten())
model.add(layers.Dense(1, activation='linear'))

logging.info("[END] Constructing CNN Architecture")
logging.info("[INFO] CNN Model Summary: \n %s", model.summary())
logging.info("[INFO] testImagesX type: \n %s", type(testImagesX))
logging.info("[INFO] testImagesX shape: \n %s", testImagesX.shape)

model.compile(optimizer='adam', loss='mse', metrics=['mae'])
logging.info("[START] CNN Training...")
history = model.fit(trainImagesX, np.array(trainY), epochs=3, validation_data=(testImagesX, np.array(testY)))
logging.info("[END] CNN Training...")

tf_history = pd.DataFrame(
    {'loss': history.history['loss'],
     'mae': history.history['mae'],
     'val_loss': history.history['val_loss'],
     'val_mae': history.history['val_mae']})

tf_history.to_csv('/home/scratch/lfeng/machine_learning/m5_base_cnn_tf_history.csv')
test_mse, test_mae = model.evaluate(testImagesX,  np.array(testY), verbose=2)
logging.info("Test MSE: {}\n Test MAE: {}".format(test_mse, test_mae))
logging.info("[END] CNN trained and tested.")

logging.info("[INFO] Predicting TSR for all grid.")
y_pred = model.predict(images).flatten()
pergrid_base_predicted = pd.DataFrame(
    {'grid_id': df.index.values,
     'tsr': df['tsr'],
     'tsr_predicted': y_pred})
pergrid_base_predicted.to_csv('/home/scratch/lfeng/machine_learning/pergrid_base_predicted.csv')