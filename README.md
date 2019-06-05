# NYC_Neighborhood_Twitter_Project
This project collects tweets that are geolocated in NYC and stores them in a PostgreSQL database, and assigns a neighborhood to each tweet based on its coordinates (more to come . . . )


NYC_Tweet_Download.py streams tweets through the Twitter API with tweepy and stores them in a PostgreSQL database.  In order to run this code, the following must be done:

  1. Install PostgreSQL and update the postgres_credentials_ex.py file with the information used to set it up
  2. Create a Twitter app to get credentials to update in twitter_credentials_ex.py, to do this:
      a. go the the Twitter app page and click the button: ‘Create New App’
      b. Fill the application details. You can leave the callback url field empty.
      c. Once the app is created, you will be redirected to the app page.
      d. Open the ‘Keys and Access Tokens’ tab.
      e. Copy ‘Consumer Key’, ‘Consumer Secret’, ‘Access token’ and ‘Access Token Secret’.
      
      
Assign_Neighborhood.py takes tweet coordinates from the PostgreSQL database, identifies the neighborhood for these coordinates, then updates the neighborhood in the database.  This can be run with the NYC Open Data neighborhood shapefile: https://data.cityofnewyork.us/City-Government/Neighborhood-Tabulation-Areas/cpf4-rkhq and I deleted any shape that was a "park-cemetary-etc" shape as they overlapped neighborhoods.

NeighborhoodTweets.py creates a new table that counts the number of tweets in each neighborhood

Neighborhood_WordCloud.py makes and saves word clouds for the 10 neighborhoods with the most tweets

Neighborhood_WordCount.py creates a list of search words and their synonyms/hypernyms/hyponyms/mesonyms/holonyms/entitlements to search in the tweets from each of the top 20 neighborhoods by tweet count.  Then a new table is created with the frequency of each word in a neighborhoods tweets (as word occurence/tweet)
