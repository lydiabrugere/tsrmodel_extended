import os, logging
import pandas as pd

from sklearn.model_selection import train_test_split
import tensorflow as tf

from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout, Flatten,Conv2D, MaxPooling2D
from keras.layers.normalization import BatchNormalization
import numpy as np

logging.basicConfig(level=logging.INFO, filename='/home/scratch/lfeng/machine_learning/m5_base_AlexNet.log')
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

inputShape = trainImagesX[0].shape

logging.info("[START] Constructing AlexNet Architecture")
"""
Define Alexnet architecture
"""
# (3) Create a sequential model
model = Sequential()

# 1st Convolutional Layer
model.add(Conv2D(filters=96, input_shape=inputShape, kernel_size=(11,11), strides=(4,4), padding='valid'))
model.add(Activation('relu'))
# Pooling
model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2), padding='valid'))
# Batch Normalisation before passing it to the next layer
model.add(BatchNormalization())

# 2nd Convolutional Layer
model.add(Conv2D(filters=256, kernel_size=(11,11), strides=(1,1), padding='valid'))
model.add(Activation('relu'))
# Pooling
model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2), padding='valid'))
# Batch Normalisation
model.add(BatchNormalization())

# 3rd Convolutional Layer
model.add(Conv2D(filters=384, kernel_size=(3,3), strides=(1,1), padding='valid'))
model.add(Activation('relu'))
# Batch Normalisation
model.add(BatchNormalization())

# 4th Convolutional Layer
model.add(Conv2D(filters=384, kernel_size=(3,3), strides=(1,1), padding='valid'))
model.add(Activation('relu'))
# Batch Normalisation
model.add(BatchNormalization())

# 5th Convolutional Layer
model.add(Conv2D(filters=256, kernel_size=(3,3), strides=(1,1), padding='valid'))
model.add(Activation('relu'))
# Pooling
model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2), padding='valid'))
# Batch Normalisation
model.add(BatchNormalization())

# Passing it to a dense layer
model.add(Flatten())
# 1st Dense Layer
model.add(Dense(4096, input_shape=(224*224*3,)))
model.add(Activation('relu'))
# Add Dropout to prevent overfitting
model.add(Dropout(0.4))
# Batch Normalisation
model.add(BatchNormalization())

# 2nd Dense Layer
model.add(Dense(4096))
model.add(Activation('relu'))
# Add Dropout
model.add(Dropout(0.4))
# Batch Normalisation
model.add(BatchNormalization())

# 3rd Dense Layer
model.add(Dense(1000))
model.add(Activation('relu'))
# Add Dropout
model.add(Dropout(0.4))
# Batch Normalisation
model.add(BatchNormalization())

# Output Layer
model.add(Flatten())
model.add(Activation('linear'))

logging.info("[END] Constructing AlexNet Architecture")
logging.info("[INFO] AlexNet Model Summary: \n %s", model.summary())
logging.info("[INFO] testImagesX type: \n %s", type(testImagesX))
logging.info("[INFO] testImagesX shape: \n %s", testImagesX.shape)

model.compile(optimizer='adam', loss='mse', metrics=['mae'])
logging.info("[START] AlexNet Training...")
history = model.fit(trainImagesX, np.array(trainY), epochs=3, validation_data=(testImagesX, np.array(testY)))
logging.info("[END] AlexNet Training...")

tf_history = pd.DataFrame(
    {'loss': history.history['loss'],
     'mae': history.history['mae'],
     'val_loss': history.history['val_loss'],
     'val_mae': history.history['val_mae']})

tf_history.to_csv('/home/scratch/lfeng/machine_learning/m5_base_alexnet_tf_history.csv')
test_mse, test_mae = model.evaluate(testImagesX,  np.array(testY), verbose=2)
logging.info("Test MSE: {}\n Test MAE: {}".format(test_mse, test_mae))
logging.info("[END] AlexNet trained and tested.")

logging.info("[INFO] Predicting TSR for all grid.")
y_pred = model.predict(images).flatten()
pergrid_base_predicted = pd.DataFrame(
    {'grid_id': df.index.values,
     'tsr': df['tsr'],
     'tsr_predicted': y_pred})
pergrid_base_predicted.to_csv('/home/scratch/lfeng/machine_learning/pergrid_base_alexnet_predicted.csv')