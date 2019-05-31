# This program will use a shapefile of NYC Neighborhoods to update the neighborhood field in the NYC_tweets database
# base code borrowed from https://gis.stackexchange.com/questions/250172/finding-out-if-coordinate-is-within-shapefile-shp-using-pyshp
# and https://pynative.com/python-postgresql-insert-update-delete-table-data-to-perform-crud-operations/

import shapefile as shp
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import psycopg2

#Importing postgres credentials
from postgres_credentials import *


# First create a shapefile to use for neighborhood assignment, not shapefile is from NYC Open Data, and all "park-cemetary-etc" shapes have been deleted
sf = shp.Reader("NeighborhoodTabulationAreas/geo_export_7a21a6c4-c430-4909-a599-d5502a088403.shp")   #Open Shapefile with shapes to check points against
sfRec = sf.records() #Read records in shapefile neighborhood neame is field 4 and borough is field 1

n = 0
m = 1
coor = ''
coorDict = {}
matplotDict = [] #Data dictionary of all points to find in the shapefile by lat and lon
nbFinal = {}

# Open shape file and store each NYC neighborhood polygon along with it neighborhood name
for shape in sf.shapeRecords(): #Iterate through shapes in shapefile
	print(sfRec[n][4])
	x = [i[0] for i in shape.shape.points[:]] #Initially for use in matplotlib to check shapefile
	y = [i[1] for i in shape.shape.points[:]] #Initially for use in matplotlib to check shapefile
	for i in x:
		matplotDict.append((y[x.index(i)],x[x.index(i)]))  

	nbshp = Polygon(matplotDict)
	nbFinal[sfRec[n][4]] = nbshp #Store shape in dictionary with neighborhood name

	matplotDict = [] #refresh coordinate store for next shape 		
	n += 1 
	

# Get a tweet and assign it a neighborhood
def AddNeighborhood(i):
	try:
		connection = psycopg2.connect(dbname=dbnametwitter, user=usertwitter, password=passwordtwitter, host=hosttwitter, port=porttwitter)
		cursor = connection.cursor()
		
		print("Connection opened")
		
		# Find the coordinates of the tweet		
		sql_select_query = """select * from NYC_tweets where id = %s"""
		cursor.execute(sql_select_query, (i,))
		record = cursor.fetchone()
		rlat = float(record[1])
		rlon = float(record[2])
		coor = (rlat, rlon)
		print (coor)
		
		#proof of concept- save the results however you'd like
		for k in nbFinal:
			if nbFinal[k].contains(Point(coor)):
				print("%s is in %s" % (i,k))
				sql_update_query = """Update NYC_tweets set neighborhood = %s where id = %s"""
				cursor.execute(sql_update_query, (k, i))
				connection.commit()

	except (Exception, psycopg2.Error) as error:
		print("Error in update operation", error)
		
	finally:
		# closing database connection.
		if (connection):
			cursor.close()
			connection.close()
			print("PostgreSQL connection is closed")

for id in range(50000):
	print(id)
	AddNeighborhood(id+1)
