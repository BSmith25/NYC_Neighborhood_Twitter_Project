# This program will count the number of tweets assicuated with certain neighborhoods, then make word clouds out of them

import psycopg2

#Importing postgres credentials
from postgres_credentials import *

#Connect to Twitter Database created in Postgres
conn = psycopg2.connect(dbname=dbnametwitter, user=usertwitter, password=passwordtwitter, host=hosttwitter, port=porttwitter)
	
#Create a cursor to perform database operations
cursor = conn.cursor()

# Delete duplicate tweets in the NYC_tweets database
cursor.execute("DELETE FROM NYC_tweets a using NYC_tweets b WHERE a.id>b.id AND a.tweet = b.tweet;")
conn.commit()
	
#with the cursor now, create the neighborhood table to count tweets in each neighborhood, first make sure to delete the old table  
cursor.execute("DROP TABLE IF EXISTS Neighborhood_tweets;")
cursor.execute("CREATE TABLE IF NOT EXISTS Neighborhood_tweets (neighborhood_id SERIAL, neighborhood_name text,  tweet_count int);")

#make a list of all neighborhoods
query_neighborhood = "SELECT DISTINCT neighborhood FROM NYC_tweets"
cursor.execute(query_neighborhood)
result = [r[0] for r in cursor.fetchall()]


# add neighborhoods to the neighborhood table and count tweets
for nb in result:
	# Check how many tweets come from the neighborhood
	if nb is not None:
		cursor.execute("SELECT COUNT(id) FROM NYC_tweets WHERE neighborhood=%s;",(nb,))
		nb_count=cursor.fetchone()[0]
		
		# update the neighborhood table with the neighborhood name and tweet count
		cursor.execute("INSERT INTO Neighborhood_tweets (neighborhood_name, tweet_count) VALUES (%s, %s);", (nb, nb_count))

#Commit changes
conn.commit()

#Close cursor and the connection
cursor.close()
conn.close()
