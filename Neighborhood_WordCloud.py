# This program creates a wordcloud of tweets from the 10 neighborhoods with the most tweets
# Methods adapted from https://github.com/ugis22/analysing_twitter/blob/master/Jupyter%20Notebook%20files/Analysis%20of%20Twitter.ipynb
# need to pip install wordcloud, nltk.download('stopwords')


#Module to handle regular expressions
import re

#Import pandas to handle data
import pandas as pd


#import libraries for accessing the database
import psycopg2
from sqlalchemy import create_engine
from postgres_credentials import *

#import libraries for visualization
import matplotlib.pyplot as plt
from wordcloud import WordCloud


#Import nltk to check english lexicon
import nltk
from nltk.corpus import stopwords

#Querying the database
def query_database(nb):
	engine = create_engine("postgresql+psycopg2://%s:%s@%s:%s/%s" %(usertwitter, passwordtwitter, hosttwitter, porttwitter, dbnametwitter))
	table = pd.read_sql_query("""SELECT tweet FROM NYC_tweets WHERE neighborhood = '%s';""" %(nb,),con=engine)
	return table

#preprocess text in tweets by removing links, @UserNames, blank spaces, etc.
def preprocessing_text(table):
	#put everythin in lowercase
	table['tweet'] = table['tweet'].str.lower()
#	#Replace rt indicating that was a retweet
#	table['tweet'] = table['tweet'].str.replace('rt', '')
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

def stop_words(table):
	#We need to remove the stop words, including NYC specific stopwords
	stop_words_list = stopwords.words('english')
	stop_words_list_nyc = ["follow us","n't","want work","getrepost","re","latest","hiring","looking","amp","newyorkcity","posted","post","click","photo","repost","click","link","click link","newyork","new york","new york city","city","ny","nyc","new","york","job","bio","apply"]
	stop_words_list = stop_words_list + stop_words_list_nyc
	table['tweet'] = table['tweet'].str.lower()
	table['tweet'] = table['tweet'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop_words_list)]))
	return table


def cleaning_table(table):
	#This function will process all the required cleaning for the text in our tweets
	table = preprocessing_text(table)
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

#Close cursor and the connection
cursor.close()
conn.close()
	

