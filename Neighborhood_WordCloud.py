# This program creates a wordcloud of tweets from the 10 neighborhoods with the most tweets
# Methods adapted from https://github.com/ugis22/analysing_twitter/blob/master/Jupyter%20Notebook%20files/Analysis%20of%20Twitter.ipynb
# need to pip install wordcloud, nltk.download('stopwords')


#%matplotlib notebook
#from tqdm import tqdm
#%matplotlib inline
#Module to handle regular expressions
import re
#manage files
#import os
#Library for emoji
#import emoji
#Import pandas and numpy to handle data
import pandas as pd
#import numpy as np

#import libraries for accessing the database
import psycopg2
from sqlalchemy import create_engine
from postgres_credentials import *

#import libraries for visualization
import matplotlib.pyplot as plt
#import seaborn as sns
from wordcloud import WordCloud
#from PIL import Image

#Import nltk to check english lexicon
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import (
    wordnet,
    stopwords
)

#import libraries for tokenization and ML
#import json;
#import keras;
#import keras.preprocessing.text as kpt;
#from keras.preprocessing.text import Tokenizer;

#import sklearn
#from sklearn.preprocessing import Normalizer
#from sklearn.feature_extraction.text import (
#    CountVectorizer,
#    TfidfVectorizer
#)
#from sklearn.model_selection import train_test_split
#from sklearn.metrics import accuracy_score

#Import all libraries for creating a deep neural network
#Sequential is the standard type of neural network with stackable layers
#from keras.models import (
#    Sequential,
#    model_from_json
#)
#Dense: Standard layers with every node connected, dropout: avoids overfitting
#from keras.layers import Dense, Dropout, Activation;

#To anotate database
#from pycorenlp import StanfordCoreNLP




#Querying the database
def query_database(nb):
	engine = create_engine("postgresql+psycopg2://%s:%s@%s:%s/%s" %(usertwitter, passwordtwitter, hosttwitter, porttwitter, dbnametwitter))
	table = pd.read_sql_query("""SELECT tweet FROM NYC_tweets WHERE neighborhood = '%s';""" %(nb,),con=engine)
	return table

#preprocess text in tweets by removing links, @UserNames, blank spaces, etc.
def preprocessing_text(table):
	#put everythin in lowercase
	table['tweet'] = table['tweet'].str.lower()
	#Replace rt indicating that was a retweet
	table['tweet'] = table['tweet'].str.replace('rt', '')
	#Replace occurences of mentioning @UserNames
	table['tweet'] = table['tweet'].replace(r'@\w+', '', regex=True)
	#Replace links contained in the tweet
	table['tweet'] = table['tweet'].replace(r'http\S+', '', regex=True)
	table['tweet'] = table['tweet'].replace(r'www.[^ ]+', '', regex=True)
	#remove numbers
	# table['tweet'] = table['tweet'].replace(r'[0-9]+', '', regex=True)
	#replace special characters and puntuation marks
	table['tweet'] = table['tweet'].replace(r'[!"#$%&()*+,-./:;<=>?@[\]^_`{|}~]', '', regex=True)
	return table

#Replace elongated words by identifying those repeated characters and then remove them and compare the new word with the english lexicon
def in_dict(word):
	if wordnet.synsets(word):
		#if the word is in the dictionary, we'll return True
		return True

def replace_elongated_word(word):
	regex = r'(\w*)(\w+)\2(\w*)'
	repl = r'\1\2\3'    
	if in_dict(word):
		return word
	new_word = re.sub(regex, repl, word)
	if new_word != word:
		return replace_elongated_word(new_word)
	else:
		return new_word

def detect_elongated_words(row):
	regexrep = r'(\w*)(\w+)(\2)(\w*)'
	words = [''.join(i) for i in re.findall(regexrep, row)]
	for word in words:
		if not in_dict(word):
			row = re.sub(word, replace_elongated_word(word), row)
	return row

def stop_words(table):
	#We need to remove the stop words, including NYC specific stopwords
	stop_words_list = stopwords.words('english')
	stop_words_list_nyc = ["follow us","n't","want work","getrepost","re","latest","hiring","looking","amp","newyorkcity","posted","post","click","photo","repost","click","link","click link","newyork","new york","new york city","city","ny","nyc","new","york","job","bio","apply"]
	stop_words_list = stop_words_list + stop_words_list_nyc
	table['tweet'] = table['tweet'].str.lower()
	table['tweet'] = table['tweet'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop_words_list)]))
	return table

def replace_antonyms(word):
	#We get all the lemma for the word
	for syn in wordnet.synsets(word): 
		for lemma in syn.lemmas(): 
			#if the lemma is an antonym of the word
			if lemma.antonyms(): 
				#we return the antonym
					return lemma.antonyms()[0].name()
	return word
            
def handling_negation(row):
	#Tokenize the row
	words = word_tokenize(row)
	speech_tags = ['JJ', 'JJR', 'JJS', 'NN', 'VB', 'VBD', 'VBG', 'VBN', 'VBP'] #adjectives, nouns, and verbs
	#We obtain the type of words that we have in the text, we use the pos_tag function
	tags = nltk.pos_tag(words)
	#Now we ask if we found a negation in the words
	tags_2 = ''
	if "n't" in words and "not" in words:
		tags_2 = tags[min(words.index("n't"), words.index("not")):]
		words_2 = words[min(words.index("n't"), words.index("not")):]
		words = words[:(min(words.index("n't"), words.index("not")))+1]
	elif "n't" in words:
		tags_2 = tags[words.index("n't"):]
		words_2 = words[words.index("n't"):] 
		words = words[:words.index("n't")+1]
	elif "not" in words:
		tags_2 = tags[words.index("not"):]
		words_2 = words[words.index("not"):]
		words = words[:words.index("not")+1] 

	for index, word_tag in enumerate(tags_2):
		if word_tag[1] in speech_tags:
			words = words+[replace_antonyms(word_tag[0])]+words_2[index+2:]
			break

	return ' '.join(words)

def cleaning_table(table):
	#This function will process all the required cleaning for the text in our tweets
	table = preprocessing_text(table)
	#table['tweet'] = table['tweet'].apply(lambda x: detect_elongated_words(x))
	#table['tweet'] = table['tweet'].apply(lambda x: handling_negation(x))
	table = stop_words(table)
	return table
	
def word_cloud(tweet_table,nb):

	#Now we store the tweets into a series to be able to process 
	tweets_list = pd.Series([t for t in tweet_table.tweet]).str.cat(sep=' ')  
	#We generate the wordcloud using the created series 
	wordcloud = WordCloud(width=1600, height=800,max_font_size=200).generate(tweets_list)

	#Now we plot the wordcloud
	plt.figure(figsize = (8, 8), facecolor = None) 
	plt.imshow(wordcloud, interpolation="bilinear") 
	plt.axis("off") 
	plt.title(nb, fontsize=20)
	plt.tight_layout(pad = 0) 
	plt.savefig("%s.png" %nb, format="png")
	plt.show() 


''' Main function here '''

#Connect to the Twitter Database created in Postgres
conn = psycopg2.connect(dbname=dbnametwitter, user=usertwitter, password=passwordtwitter, host=hosttwitter, port=porttwitter)
#Create a cursor to perform database operations
cursor = conn.cursor()

#Get the 10 neighborhoods with the most tweets
cursor.execute("SELECT neighborhood_name FROM Neighborhood_tweets ORDER BY tweet_count DESC LIMIT 10;")
neighborhoods = [r[0] for r in cursor.fetchall()]

# Select a neighborhood then create its word cloud
for nb in neighborhoods:
	tweet_table = query_database(nb)
	tweet_table = cleaning_table(tweet_table)
	word_cloud(tweet_table,nb)
	

