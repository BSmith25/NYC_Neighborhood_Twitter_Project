# Based on code from https://gist.github.com/ugis22?page=6 https://towardsdatascience.com/how-to-build-a-postgresql-database-to-store-tweets-1be9c1d48c7
# And https://shuzhanfan.github.io/2018/03/twitter-streaming-collection/
# in anaconda: Active code page 1252
# in CMD postgres SET CLIENT_ENCODING TO 'utf8'

import psycopg2
import tweepy 
import json

#Importing postgres credentials
from postgres_credentials_ex import *

#Importing twitter credentials
from twitter_credentials_ex import *

def create_tweets_table():
	"""	
	This function open a connection with an already created database and creates a new table to
	store tweets related to a subject specified by the user
	"""
	
	#Connect to Twitter Database created in Postgres
	conn_twitter = psycopg2.connect(dbname=dbnametwitter, user=usertwitter, password=passwordtwitter, host=hosttwitter, port=porttwitter)
	
	#Create a cursor to perform database operations
	cursor_twitter = conn_twitter.cursor()
	
	#with the cursor now, create the tweet table for tweets from NYC    
	query_create = "CREATE TABLE IF NOT EXISTS NYC_tweets (id SERIAL, lat varchar(20) default NULL, lon varchar(20) default NULL, created_at timestamp, tweet text NOT NULL, user_name text, retweetcount int, Neighborhood text default NULL, PRIMARY KEY(id));" 
	cursor_twitter.execute(query_create)
	
	#Commit changes
	conn_twitter.commit()
	
	#Close cursor and the connection
	cursor_twitter.close()
	conn_twitter.close()
	return
	
def autorize_twitter_api():
	"""
	This function gets the consumer key, consumer secret key, access token 
	and access token secret given by the app created in your Twitter account
	and authenticate them with Tweepy.
	"""
	#Get access and costumer key and tokens
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	
	return auth

class MyStreamListener(tweepy.StreamListener):
	
	def on_connect(self):
		
		print('......Connected to Twitter Streaming API...... \n')

	def on_data(self, raw_data):
	
		try:
		
			data = json.loads(raw_data)            
			
			if data['coordinates']:           # only collect geo-tagged tweets
			
				#Obtain all the variables to store in each column
				created_at = data['created_at']
				tweet = data['text']
				user_name = data['user']['screen_name']
				retweetcount = data['retweet_count']
				lat = data['coordinates']['coordinates'][1]
				lon = data['coordinates']['coordinates'][0]
		
				#Store them in the corresponding table in the database
				store_tweets_in_table(lat, lon, created_at, tweet, user_name, retweetcount)        
			
		except Exception as e:
			print(e)
    
	def on_error(self, status_code):
		if status_code == 420:
			#returning False in on_error disconnects the stream
			return False

def store_tweets_in_table(lat, lon, created_at, tweet, user_name, retweetcount):
	"""
	This function open a connection with an already created database and inserts into corresponding table 
	tweets related to the selected topic
	"""
	
	#Connect to Twitter Database created in Postgres
	conn_twitter = psycopg2.connect(dbname=dbnametwitter, user=usertwitter, password=passwordtwitter, host=hosttwitter, port=porttwitter)
	
	#Create a cursor to perform database operations
	cursor_twitter = conn_twitter.cursor()

	#with the cursor now, insert tweet into table    
	cursor_twitter.execute("INSERT INTO NYC_tweets (lat, lon, created_at, tweet, user_name, retweetcount) VALUES (%s, %s, %s, %s, %s, %s);", (lat, lon, created_at, tweet, user_name, retweetcount))
	
	#Commit changes
	conn_twitter.commit()
	
	#Close cursor and the connection
	cursor_twitter.close()
	conn_twitter.close()
	return


if __name__ == "__main__": 
	#Creates the table for storing the tweets
	create_tweets_table()
	
	#Connect to the streaming twitter API
	api = tweepy.API(wait_on_rate_limit_notify=True)
	
	#Stream the tweets
	streamer = tweepy.Stream(auth=autorize_twitter_api(), listener=MyStreamListener(api=api))
	streamer.filter(languages=["en"], locations=[-74.25889,40.47722,-73.7,40.91611])
