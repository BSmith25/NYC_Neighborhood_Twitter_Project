# This script counts the frequency of words in tweets from certain neighborhoods

#import libraries for accessing the database
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine
from postgres_credentials import *

#Import pandas and numpy to handle data
import pandas as pd

#Import nltk to check english lexicon
from nltk.corpus import wordnet as wn

# List of synsets and words
words = ['museum.n.01','shopping.n.01','metro.n.01','theater.n.01','park.n.02','music.n.01','library.n.05','restaurant.n.01','crime.n.01','family.n.01','traffic.n.01','beautiful.a.01','quiet.a.01','barroom.n.01','old.a.02','construction.n.07']
freq_cat = ['museum_freq', 'shopping_freq', 'subway_freq', 'theater_freq', 'park_freq' , 'music_freq', 'library_freq', 'restaurant_freq', 'crime_freq', 'family_freq', 'traffic_freq', 'beautiful_freq', 'quiet_freq', 'bar_freq', 'old_freq', 'construction_freq']

# querying the database
def query_database(nb):
	engine = create_engine("postgresql+psycopg2://%s:%s@%s:%s/%s" %(usertwitter, passwordtwitter, hosttwitter, porttwitter, dbnametwitter))
	table = pd.read_sql_query("""SELECT tweet FROM NYC_tweets WHERE neighborhood = '%s';""" %(nb,),con=engine)
	
	#put everything in lowercase
	table['tweet'] = table['tweet'].str.lower()
	return table

#Make a list of all searchwords - including synonyms, hypernyms, hyponyms, meronyms, holonyms, and entailments
def all_word_search_list(word):
	list=[]
	syn=wn.synset(word)
	for l in syn.lemma_names(): 
		list.append(l)
	for hyper in syn.hypernyms():
		for l in hyper.lemma_names():
			list.append(l)
	for hypo in syn.hyponyms():
		for l in hypo.lemma_names():
			list.append(l)
	for m in syn.part_meronyms():
		for l in m.lemma_names():
			list.append(l)
	for h in syn.part_holonyms():
		for l in h.lemma_names():
			list.append(l)
	for e in syn.entailments():
		for l in e.lemma_names():
			list.append(l)
	return(list)


''' Main function here '''

#Connect to the Twitter Database created in Postgres
conn = psycopg2.connect(dbname=dbnametwitter, user=usertwitter, password=passwordtwitter, host=hosttwitter, port=porttwitter)
#Create a cursor to perform database operations
cursor = conn.cursor()

#with the cursor now, create the neighborhood table to count tweets in each neighborhood, first make sure to delete the old table  
cursor.execute("DROP TABLE IF EXISTS Neighborhood_frequencies;")
cursor.execute("CREATE TABLE IF NOT EXISTS Neighborhood_frequencies (neighborhood_id SERIAL, neighborhood_name text,  tweet_count int, museum_freq float, shopping_freq float, subway_freq float, theater_freq float, park_freq float, music_freq float, library_freq float, restaurant_freq float, crime_freq float, family_freq float, traffic_freq float, beautiful_freq float, quiet_freq float, bar_freq float, old_freq float, construction_freq float);")


#Get the list of neighborhoods 
cursor.execute("SELECT neighborhood_name FROM Neighborhood_tweets ORDER BY tweet_count DESC LIMIT 20;")
neighborhoods = [r[0] for r in cursor.fetchall()]

# Select a neighborhood and add its word frequencies to the table
for nb in neighborhoods:

# Check how many tweets come from the neighborhood
	if nb is not None:
		cursor.execute("SELECT COUNT(id) FROM NYC_tweets WHERE neighborhood=%s;",(nb,))
		nb_count=cursor.fetchone()[0]
		
		# update the neighborhood table with the neighborhood name and tweet count
		cursor.execute("INSERT INTO Neighborhood_frequencies (neighborhood_name, tweet_count) VALUES (%s, %s);", (nb, nb_count))
		conn.commit()

		# get word frequencies and put them into SQL table
		tweet_table = query_database(nb)
		for element in enumerate(words):
			word_list = all_word_search_list(element[1])
			w_sum  = 0
			for word in word_list:
				w_sum = w_sum + tweet_table.tweet.str.count(word).sum()
			fcat = freq_cat[element[0]]
			print(fcat)
			print(nb)
			cursor.execute(sql.SQL("UPDATE Neighborhood_frequencies SET {} = %s WHERE neighborhood_name = %s").format(sql.Identifier(fcat)),[w_sum/nb_count,nb])
			conn.commit()

#Close cursor and the connection
cursor.close()
conn.close()




