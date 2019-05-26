# This program will use a shapefile of Brooklyn Neighborhoods and tell you which neighborhood a point in decimal degrees is in
# base code borrowed from https://gis.stackexchange.com/questions/250172/finding-out-if-coordinate-is-within-shapefile-shp-using-pyshp
import shapefile as shp
from shapely.geometry import Point
import csv
from shapely.geometry.polygon import Polygon

fileName = 'TestLatLon.csv'                #Open CSV file with points to check   
sf = shp.Reader("NeighborhoodTabulationAreas/geo_export_7a21a6c4-c430-4909-a599-d5502a088403.shp")   #Open Shapefile with shapes to check points against
sfRec = sf.records() #Read records in shapefile neighborhood neame is field 4 and borough is field 1

n = 0
m = 1
coor = ''
coorDict = {}
matplotDict = [] #Data dictionary of all points to find in the shapefile by lat and lon
nbFinal = {}

# Open shape file and store each Brooklyn neighborhood polygon along with it neighborhood name
for shape in sf.shapeRecords(): #Iterate through shapes in shapefile
	if sfRec[n][1]=='Brooklyn':
		print(sfRec[n][4])
		x = [i[0] for i in shape.shape.points[:]] #Initially for use in matplotlib to check shapefile
		y = [i[1] for i in shape.shape.points[:]] #Initially for use in matplotlib to check shapefile
		for i in x:
			matplotDict.append((x[x.index(i)],y[x.index(i)]))  

		nbshp = Polygon(matplotDict)
		nbFinal[sfRec[n][4]] = nbshp #Store shape in dictionary with neighborhood name

		matplotDict = [] #refresh coordinate store for next shape 		
	n += 1 

with open(fileName) as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		# print(row['latitude'],row['longitude'])
		coor = (row['latitude'],row['longitude'])
		rlat = float(row['latitude'])
		rlong = float(row['longitude'])
		if coor == ' ,   ' or coor == ', ':
			coorDict[row['PrimaryKey']] = 'No Data' #PrimaryKey is my primary key that I will use to write the data back into the .csv 
		else:
			if float(row['longitude']) > 0:
				coorDict[row['PrimaryKey']] = (rlat,rlong)
			else:
				coorDict[row['PrimaryKey']] = (rlong,rlat)
		m += 1




#proof of concept- save the results however you'd like
for j in coorDict:
	for k in nbFinal:
		if nbFinal[k].contains(Point(coorDict[j])):
			print(j, 'in', k)
		else:
			print('not found')