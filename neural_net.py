# This script fits a neural network to occurrences of words in tweets to categorize them by neighborhood
# the code was loosely based on: https://github.com/ugis22/analysing_twitter/blob/master/Jupyter%20Notebook%20files/Analysis%20of%20Twitter.ipynb


#import libraries for accessing the database
import psycopg2
from postgres_credentials import *

#import libraries for plotting
import matplotlib.pyplot as plt

#Import pandas and numpy to handle data
import pandas as pd
import numpy as np

#import libraries for ML
import keras

import sklearn
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

#Import all libraries for creating a deep neural network
#Sequential is the standard type of neural network with stackable layers
from keras.models import Sequential

#Dense: Standard layers with every node connected
from keras.layers import Dense, Dropout, Activation;

# querying the database for tweets from a neighborhood
def query_database():
	cursor.execute("SELECT * FROM tweet_words;")
	tweet_list=cursor.fetchall()
	return tweet_list
	
#Split Data into training and test dataset, X's are all word occurences, Y's are neighborhoods
def splitting(tweet_list):
	neighborhoods=[data[2] for data in tweet_list]
	word_counts=[data[3:19] for data in tweet_list]
	X_train, X_test, Y_train, Y_test = train_test_split(word_counts, neighborhoods, test_size=0.2, shuffle=True)
	return X_train, X_test, Y_train, Y_test
	
#Create a Neural Network
#Create the model
def train(X_train, Y_train, features, shuffle, drop, layer1, layer2, epoch, lr, epsilon, validation):
	model_nn = Sequential()
	model_nn.add(Dense(layer1, input_shape=(features,), activation='relu'))
	model_nn.add(Dropout(drop))
	model_nn.add(Dense(layer2, activation='relu'))
	model_nn.add(Dropout(drop))
	model_nn.add(Dense(layer3, activation='relu'))
	model_nn.add(Dropout(drop))
	model_nn.add(Dense(10, activation='softmax'))

	optimizer = keras.optimizers.Adam(lr=lr, beta_1=0.9, beta_2=0.999, epsilon=epsilon, decay=0.0, amsgrad=False)
	model_nn.compile(loss='sparse_categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
	history=model_nn.fit(np.array(X_train), Y_train, batch_size=32, epochs=epoch, verbose=1, validation_split=validation, shuffle=shuffle)
    
	# Plot training & validation accuracy values
	plt.plot(history.history['acc'])
	plt.plot(history.history['val_acc'])
	plt.title('Model accuracy')
	plt.ylabel('Accuracy')
	plt.xlabel('Epoch')
	plt.legend(['Train', 'Validate'], loc='upper left')
	plt.show()

	# Plot training & validation loss values
	plt.plot(history.history['loss'])
	plt.plot(history.history['val_loss'])
	plt.title('Model loss')
	plt.ylabel('Loss')
	plt.xlabel('Epoch')
	plt.legend(['Train', 'Validate'], loc='upper left')
	plt.show()
	
	return model_nn

def test(X_test, model_nn):
    prediction = model_nn.predict(X_test)
    return prediction
	
''' Main Function Here '''
#Connect to the Twitter Database created in Postgres
conn = psycopg2.connect(dbname=dbnametwitter, user=usertwitter, password=passwordtwitter, host=hosttwitter, port=porttwitter)
print("connecting")

#Create a cursor to perform database operations and get the data from the tweet count table
cursor = conn.cursor()
tweet_list=query_database()

#Close cursor and the connection
cursor.close()
conn.close()

#split the data into trainng and testing
X_train, X_test, Y_train, Y_test = splitting(tweet_list)

# create a neural network
features = 16
shuffle = True
drop = 0.2
layer1 = 80
layer2 = 40
layer3 = 20
epoch = 100
lr = 0.001
epsilon = 10e-3
validation = 0.25
model = train(X_train, Y_train, features, shuffle, drop, layer1, layer2, epoch, lr, epsilon, validation)







