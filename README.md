# NYC_Neighborhood_Twitter_Project
This project collects tweets that are geolocated in NYC and stores them in a PostgreSQL database (more to come . . . )


NYC_Tweet_Download.py streams tweets through the Twitter API with tweepy and stores them in a PostgreSQL database.  In order to run this code, the following must be done:

  1. Install PostgreSQL and update the postgres_credentials_ex.py file with the information used to set it up
  2. Create a Twitter app to get credentials to update in twitter_credentials_ex.py, to do this:
      a. go the the Twitter app page and click the button: ‘Create New App’
      b. Fill the application details. You can leave the callback url field empty.
      c. Once the app is created, you will be redirected to the app page.
      d. Open the ‘Keys and Access Tokens’ tab.
      e. Copy ‘Consumer Key’, ‘Consumer Secret’, ‘Access token’ and ‘Access Token Secret’.
      
      
Find_Neighborhood.py takes a list of coordinates in a csv file and identifies the Brooklyn neighborhood for these coordinates, if the tweet is from Brooklyn.  In the future this will be hooked up to the PostgreSQL database of NYC tweet locations to associate tweets with neighborhoods.  This can be run with the NYC Open Data neighborhood shapefile: https://data.cityofnewyork.us/City-Government/Neighborhood-Tabulation-Areas/cpf4-rkhq and a sample CSV (with the correct columsn names inserted).
