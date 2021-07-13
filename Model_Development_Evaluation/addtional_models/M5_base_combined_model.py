import os, logging
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
from sklearn.preprocessing import MinMaxScaler

import tensorflow as tf
from keras.models import Sequential
from keras.layers.normalization import BatchNormalization
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras.layers.core import Activation
from keras.layers.core import Dense
from keras.layers import Flatten
from keras.layers import Input
from keras.models import Model
from keras.optimizers import Adam
from keras.layers import concatenate
from keras.layers.core import Dropout


def load_tsr_attributes(var_csv_path):
    pergrid_base_df = pd.read_csv(var_csv_path, sep=",")
    df = pergrid_base_df.dropna()
    df.set_index('grid_id', inplace=True)
    return df


def process_tsr_attributes(df, trainAttr, testAttr):
    # initialize the column names of the continuous data
    continuous = ['fa', 'aet', 'ai', 'art', 'ewd', 'map', 'mat', 'mpdq', 'mtcq', 'pet', 'psn', 'ra', 'rmap', 'rmat', 'tsn', 'mfdf', 'alt', 'mtwq']

    # performin min-max scaling each continuous feature column to the range [0, 1]
    cs = MinMaxScaler()
    trainContinuous = cs.fit_transform(trainAttr[continuous])
    testContinuous = cs.transform(testAttr[continuous])

    # one-hot encode the zip code categorical data (by definition of
    # one-hot encoding, all output features are now in the range [0, 1])
    zipBinarizer = LabelBinarizer().fit(df["hydrogroup"])
    trainCategorical = zipBinarizer.transform(trainAttr["hydrogroup"])
    testCategorical = zipBinarizer.transform(testAttr["hydrogroup"])

    # construct training and testing data points by concatenating
    # the categorical features with the continuous features
    trainX = np.hstack([trainCategorical, trainContinuous])
    testX = np.hstack([testCategorical, testContinuous])

    return trainX, testX


def load_tsr_images(attr_df, imageFolder):

    images = []
    logging.info("[START] Reading jpg image for each grid")
    for i in attr_df.index.values:
        imagePath = os.path.sep.join([imageFolder, "nlcd_{}.jpg".format(i)])

        if not os.path.isfile(imagePath):
            print("{} does not exist".format(imagePath))
        else:
            image = tf.io.read_file(imagePath)
            image = tf.image.decode_jpeg(image, channels=3)
            image = tf.image.convert_image_dtype(image, tf.float32)
            image = tf.image.resize(image, [667, 667])
            images.append(image.numpy())
    logging.info("[END] Reading jpg image for each grid")

    # logging.info("[START] Resizing jpg image for each grid")
    # images = np.array(images) / 255.0
    # logging.info("[END] Resizing jpg image for each grid")

    return np.array(images)


def create_grnn():

    return

def create_mlp(dim):
    mlp_model = Sequential()
    mlp_model.add(Dense(512, input_dim=dim, activation="relu"))
    mlp_model.add(Dense(4, activation="relu"))

    return mlp_model


def create_cnn(width, height, depth, filters=(16, 32, 64), regress=False):
    # initialize the input shape and channel dimension, assuming TensorFlow/channels-last ordering
    chanDim = -1

    # define the model input
    inputs = Input(shape=(height, width, depth))

    # loop over the number of filters
    for (i, f) in enumerate(filters):
        # if this is the first CONV layer then set the input appropriately
        if i == 0:
            x = inputs

        # CONV => RELU => BN => POOL
        x = Conv2D(filters=f, kernel_size=(7, 7), padding="same")(x)
        x = Activation("relu")(x)
        x = BatchNormalization(axis=chanDim)(x)
        x = Dropout(0.5)(x)
        x = MaxPooling2D(pool_size=(2, 2), strides=2, padding='same')(x)

    # flatten output from CONV as input to FNN, then FC => RELU => BN => DROPOUT
    x = Flatten()(x)
    x = Dense(8)(x)
    x = Activation("relu")(x)
    x = BatchNormalization(axis=chanDim)(x)
    x = Dropout(0.5)(x)

    # apply another FC layer, this one to match the number of nodes coming out of the MLP
    x = Dense(4)(x)
    x = Activation("relu")(x)

    # check to see if the regression node should be added
    if regress:
        x = Dense(1, activation="linear")(x)

    # construct the CNN
    cnn_model = Model(inputs, x)

    return cnn_model


# logging.basicConfig(level=logging.INFO, filename='/home/scratch/lfeng/machine_learning/m5_base_combined_model.log')
# logging.info("[INFO] Reading pergrid_base csv...")

# pergrid_base_path = '/home/scratch/lfeng/machine_learning/pergrid_base.csv'
# imageDir = '/home/scratch/lfeng/machine_learning/nlcd_jpg'
pergrid_base_path = '/Users/lianfeng/Document/species_richness_sdm/src/notebooks/machine_learning/manuscript1/pergrid_base1.csv'
imageDir = '/Users/lianfeng/Document/species_richness_sdm/src/notebooks/machine_learning/nlcd_jpg'

df = load_tsr_attributes(pergrid_base_path)
images = load_tsr_images(df, imageDir)

split = train_test_split(df, images, test_size=0.2, random_state=42)
(trainAttrX, testAttrX, trainImagesX, testImagesX) = split
# maxTSR = trainAttrX["tsr"].max()
trainY = trainAttrX["tsr"]
testY = testAttrX["tsr"]
trainAttrX, testAttrX = process_tsr_attributes(df, trainAttrX, testAttrX)
AttrX = np.concatenate((testAttrX, trainAttrX), axis=0)

# ### Create the convolutional base
logging.info("[INFO] Constructing Combined Model Architecture")

# create the input to the final set of layers as the *output* of both MLP and CNN
mlp = create_mlp(trainAttrX.shape[1])
cnn = create_cnn(667, 667, 3, regress=False)
combinedInput = concatenate([mlp.output, cnn.output])

# final FC layer head will have two dense layers, the final one being the regression head
x = Dense(4, activation="relu")(combinedInput)
x = Dense(1, activation="linear")(x)

# the final model will accept categorical/numerical data on the MLP
# input and images on the CNN input, outputting a single value (tsr value for each grid)
model = Model(inputs=[mlp.input, cnn.input], outputs=x)

# compile the model using mean absolute percentage error as loss, to seek to minimize
# the absolute percentage difference between tsr *predictions* and the *actual tsr*
opt = Adam(lr=1e-3, decay=1e-3/200)
model.compile(loss="mean_absolute_error", optimizer=opt)

# train the model
print("[START] training model...")
model.fit([trainAttrX, trainImagesX], trainY,
          validation_data=([testAttrX, testImagesX], testY),
          epochs=100, batch_size=8)
print("[END] training model...")

logging.info("[INFO] Predicting TSR for all grid.")
y_pred = model.predict([AttrX, images]).flatten()
pergrid_base_predicted = pd.DataFrame(
    {'grid_id': df.index.values,
     'tsr': df['tsr'],
     'tsr_predicted': y_pred})

pergrid_base_predicted.to_csv('/home/scratch/lfeng/machine_learning/pergrid_base_combined_predicted_0518.csv')