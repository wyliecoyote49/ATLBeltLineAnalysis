import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import shapely
from shapely.geometry import Point, Polygon, LineString, mapping, shape
import fiona
import itertools
import util
import search
import math
import functools
import sys
import os
import csv
import json

# Global Variables

beltline_Access_pts_df = gpd.GeoDataFrame()
beltline_trail_df = gpd.GeoDataFrame()
parcels_df = gpd.GeoDataFrame()
sidewalks_df = gpd.GeoDataFrame()
streets_df = gpd.GeoDataFrame()
campus_df = gpd.GeoDataFrame()
zone_df = gpd.GeoDataFrame()

access_points = []

parcel_by_neighborhood = gpd.GeoDataFrame()
streets_with_sidewalks = gpd.GeoDataFrame()
street_with_points = gpd.GeoDataFrame()
high_injury_df = gpd.GeoDataFrame()
segments_df = pd.DataFrame()
parcel_centroids = []
neighborhood_centroids = []	
street_inters = []
sidewalk_inters = []
street_point_for_parcel = []

access_points_on_beltline = {}
usable_coords = {}
access_points_intersections = {}
beltline_segments = {}
streets = []
paths = []
neighborhood_codes = []

pd.set_option("display.max_rows", None)


def main():
	arg = sys.argv[1]
	include_sidewalks = False
	if arg == '-s':
		include_sidewalks = True
	print("\n\n\n*Preproccessing")
	import_data()
	clean_data()
	data_extractions(include_sidewalks)
	

	print("\n*Ready To Search  (-h for help)")
	
	while(1):
		args = input(">>  ")
		arg_array = args.split(" ")
		print(arg_array)

		if arg_array[0] == '-h':
			print('	search (-a)')
			print('	search (-n) (nbhd code)')
		elif arg_array[0] == 'search':

			if arg_array[1] == '-a':

				streets, paths = find_paths()
				plot_map()
				summary_table()
				plt.show()

			elif arg_array[1] == '-n':
				streets, paths = find_paths(arg_array[2])
				plot_map()
				summary_table()
				plt.show()


def import_data(preproccessing = False):
	print("    *Importing Data...")
	global beltline_Access_pts_df,  beltline_trail_df, parcels_df, sidewalks_df, streets_df, campus_df, zone_df, zone_df, access_points, segments_df, high_injury_df
	beltline_Access_pts_df = gpd.read_file("./Washington_SHARE/BeltLine_AccessPts_Washington.shp", encoding='utf-8')
	beltline_trail_df = gpd.read_file("./Washington_SHARE/BeltLine_Trails_Washington.shp", encoding='utf-8')
	parcels_df = gpd.read_file("./Washington_SHARE/Parcels_Washington_Zone.shp", encoding='utf-8')
	sidewalks_df = gpd.read_file("./Washington_SHARE/Sidewalks_Washington.shp", encoding='utf-8')
	streets_df = gpd.read_file("./Washington_SHARE/Streets_Washington.shp", encoding='utf-8')
	campus_df = gpd.read_file("./Washington_SHARE/Washington_Campus.shp")
	zone_df = gpd.read_file("./Washington_SHARE/Washington_Zone.shp")
	access_points = [shape(point['geometry']) for point in fiona.open("./Washington_SHARE/BeltLine_AccessPts_Washington.shp")]
	high_injury_df = gpd.read_file("./Washington_SHARE/High_Injury_Intersections.shp")

def clean_data():
	print("    *Clening Data...")
	global parcels_df, parcel_by_neighborhood, streets_with_sidewalks, streets_df, sidewalks_df
	parcels_df = parcels_df.loc[parcels_df['Include'] == 'Yes']
	parcel_by_neighborhood = gpd.GeoDataFrame(parcels_df.groupby('NGHBRHDCD').geometry.agg(shapely.ops.unary_union).reset_index(), geometry="geometry", crs=parcels_df.crs)
	streets_with_sidewalks = gpd.sjoin(streets_df, sidewalks_df, how="left", op='intersects')


def getDist(start, end):
	# print(start, end)
	diff_x = start[0] - end[0]
	diff_y = start[1] - end[1]
	dist = math.sqrt((diff_x ** 2) + (diff_y ** 2))
	return dist/5280

def getStreetIntersection(point):
	minDist = 9999999
	new_point = ()
	for coord in util.coordsToUse.keys():
		dist = getDist(point, coord)
		if dist < minDist:
			minDist = dist
			new_point = coord
	return new_point

def getStreets(points):
	streets = []
	fake_streets = []
	for i in range(len(points)-1):
		start = points[i]
		end = points[i+1]
		key = (start, end)
		if (key in util.segments.keys()):
			streets.append(util.segments[key][1])
		elif (key[1], key[0]) in util.segments.keys():
			streets.append(util.segments[(key[1], key[0])][1])


	return streets

# The next four funcs should be moved to the util file #

def all_beltline_coords():
	lines = beltline_trail_df.geometry
	points = []
	for line in lines:
		usable_coords[(line.coords[0][0], line.coords[0][1])] = 1
		usable_coords[(line.coords[-1][0], line.coords[-1][1])] = 1
		for point in line.coords:
			points.append(Point(point[0], point[1]))
	return points


def find_true_access_points(points):
	min_beltline_points = []
	for point in access_points:
		
		dist = [(line_point.distance(point)) for line_point in points]
		min_index = dist.index(min(dist))
		min_beltline_points.append(points[min_index])
		access_points_on_beltline[(point.coords[0], points[min_index].coords[0])] = ((point.coords[0], points[min_index].coords[0]), LineString([point, Point(points[min_index])]), '', 'Seg to Beltline', True)
		usable_coords[points[min_index].coords[0]] = 1

	return access_points_on_beltline


def create_access_point_segments():
	min_intersection = []
	coords = list(util.coordsToUse.keys())
	for point in access_points:
		dist = [Point(intersection).distance(point) for intersection in coords]
		min_index = dist.index(min(dist))
		min_intersection.append(coords[min_index])
		access_points_intersections[(point.coords[0], coords[min_index])] = ((point.coords[0], coords[min_index]), LineString([point, Point(coords[min_index])]), '', 'Seg to Beltline', True)


def create_beltline_segments():
	lines = [lines for lines in beltline_trail_df.geometry]
	for line in lines:
		if line.type == 'LineString':
			coords = [(coord[0], coord[1]) for coord in line.coords]
			start = 0
			for i in range(len(coords)):
				if coords[i] in usable_coords and i > 0:
					beltline_segments[(coords[start], coords[i])] = ((coords[start], coords[i]), LineString(coords[start:i+1]), '', 'Beltline', True)
					start = i


def data_extractions(include_sidewalks):
	print("    *Extracting Data...")
	global street_with_points, streets_with_sidewalks, parcel_centroids, parcels_df, neighborhood_centroids, parcel_by_neighborhood, street_inters, street_point_for_parcel, access_points_on_beltline, sidewalk_inters, segments_df, \
		neighborhood_codes
	street_with_points = streets_with_sidewalks.copy()
	parcel_centroids = parcels_df.centroid
	neighborhood_centroids = parcel_by_neighborhood.centroid
	neighborhood_codes = parcel_by_neighborhood['NGHBRHDCD'].tolist()

	util.getHighInjuryNetwork(high_injury_df)

	util.getAllCoords(streets_df)
	util.getAllCoords(beltline_trail_df)
	street_inters = util.getIntersections("./Washington_SHARE/Streets_Washington.shp")
	
	if (include_sidewalks == True):
		util.getAllSidewalkCoords(sidewalks_df)
		sidewalk_inters = util.getSidewalkIntersections("./Washington_SHARE/Sidewalks_Washington.shp")
		util.createSidewalkSegments(sidewalks_df)


	util.createSegments(streets_df, include_sidewalks)

		# segment_df = gdf.DataFrame.from_dict(util.segments, orient='index', columns=['key', 'LineString', 'Type', 'Label', 'has_side_walk'])
		# segment_df.to_csv('segments.csv', encoding='utf-8', index=False)

	for centroid in neighborhood_centroids:
		point = getStreetIntersection(centroid.coords[0])
		street_point_for_parcel.append(point)
		# plt.plot(point[0], point[1], color='black', marker='o', markersize=2)

	points = all_beltline_coords()
	access_points_on_beltline = find_true_access_points(points)
	create_access_point_segments()
	create_beltline_segments()
	util.segments.update(beltline_segments)
	util.segments.update(access_points_on_beltline)
	util.segments.update(access_points_intersections)

	# manually manipulate beltline
	lines = [lines for lines in beltline_trail_df.geometry]
	util.segments[(lines[0].coords[0], lines[1].coords[-1])] = ((lines[0].coords[0], lines[1].coords[-1]), LineString([lines[0].coords[0],lines[1].coords[-1]]), '', '', True)
	util.segments[(lines[1].coords[0], lines[3].coords[-1])] = ((lines[1].coords[0], lines[3].coords[-1]), LineString([lines[1].coords[0],lines[3].coords[-1]]), '', '', True)
	util.segments[(lines[4].coords[-1], lines[9].coords[-1])] = ((lines[4].coords[-1], lines[9].coords[-1]), LineString([lines[4].coords[-1],lines[9].coords[-1]]), '', '', True)






def find_paths(nbhd = None):
	print("\n*Finding Paths...")
	global street_point_for_parcel, neighborhood_codes
	util.get_all_beltline_points(beltline_trail_df, beltline_Access_pts_df)
	path_sum = 0
	beltline_path_sum = 0
	print(neighborhood_codes)
	# for i in range(len(street_point_for_parcel)):
	if nbhd == None:
		for i in range(len(street_point_for_parcel)):
			points_in_path, visited, fringe = search.aStarSearch(street_point_for_parcel[i], (2218878.4499617554, 1365096.1014726758))
			streets.append(getStreets(points_in_path))
			paths.append(points_in_path)
	else: 
		print(nbhd)
		i = neighborhood_codes.index(nbhd)
		points_in_path, visited, fringe = search.aStarSearch(street_point_for_parcel[i], (2218878.4499617554, 1365096.1014726758))
		streets.append(getStreets(points_in_path))
		paths.append(points_in_path)

	return streets, paths
		

def summary_table():
	global paths
	print("\n\n")
	print ("*********************")
	print ("*   Summary Table   *")
	print ("*********************\n")
	data = []
	for index, points in enumerate(paths):
		print("NGHBRHDCD: ", parcel_by_neighborhood.loc[index, 'NGHBRHDCD'], "\n")
		for i in range(len(points)-1):
			start = points[i]
			end = points[i+1]
			key = (start, end)
			if (key in util.segments.keys()):
				data.append([util.segments[(key[0], key[1])][3], getDist(key[0], key[1])])
			elif (key[1], key[0]) in util.segments.keys():
				data.append([util.segments[(key[1], key[0])][3], getDist(key[1], key[0])])

		total_sum = search.getDistance(points)/5280
		beltline_path_sum = search.getPathOnBeltline(points)/5280

		df = pd.DataFrame(data, columns=['Street Name', 'Distance (mi)'])
		print(df)
		print()
		print('Total Distance: ', total_sum, '	Distance on Beltline: ', beltline_path_sum, '	Percentage On Beltline: ', (beltline_path_sum/total_sum)*100, '\n\n')

		data = []

	paths = []


def plot_map():
	print("*Plotting Map...")
	global streets
	ax = beltline_Access_pts_df.plot()
	zone_df.plot(ax=ax, color='#A4FF98', alpha=.75)
	beltline_trail_df.plot(ax=ax, color='pink')
	streets_df.plot(ax=ax, color='black', alpha=.25)
	# streets_with_sidewalks.plot(ax=ax, color='blue', alpha=.5)
	campus_df.plot(ax=ax, color='brown')
	neighborhood_centroids.plot(ax=ax, color='black', marker='x', markersize=1.5)
	for point in util.coordsToUse:
		plt.plot(point[0], point[1], color='green', marker='o', markersize='1')
	for keys in util.sidewalk_segments.keys():
		plt.plot(*util.sidewalk_segments[keys].xy, color='blue')
	for street in streets:
		for seg in street:
			if seg.type == 'LineString':
				plt.plot(*seg.xy, color='red', alpha=.33)



main()



















###############################################################
# EVERYTHING BEYOND THIS POINT IS DEAD OR IMPLEMENTED ABOVE   #
# WILL DELETE THIS AT SOME POINT BUT COULD NEED LATER		  #
###############################################################

# accessPointColumns = beltline_Access_pts_df.columns


# print("Parcel Head\n")
# print(parcels_df.head().T)
# print("\n\n")


# print(beltline_Access_pts_df.shape)

# print("Printing Access Point Columns\n")
# print(accessPointColumns)

# access_point_shape = beltline_Access_pts_df.to_crs({'init': 'epsg:4326'})


# getCentroids(beltline_Access_pts_df)
# print(beltline_Access_pts_df.centroid)
# parcel_centroids = parcels_df.centroid
# neighborhood_centroids = parcel_by_neighborhood.centroid

# ax = beltline_Access_pts_df.plot()
# zone_df.plot(ax=ax, color='#A4FF98', alpha=.75)
# beltline_trail_df.plot(ax=ax, color='pink')
# parcel_by_neighborhood.plot(ax=ax, color='#4A98FC')

# shapes = [neighborhood for neighborhood in parcel_by_neighborhood.geometry]
# for shape in shapes:
# 	print(shape.type)
# 	if shape.type == 'MultiPolygon':
# 		coords = []
# 		for index, poly in enumerate(shape):
# 			exterior = poly.exterior.coords
# 			if index == 0:
# 				coords.extend(exterior)
# 			else:
# 				coords = functools.reduce(lambda x, y: x ^ y, coords)
# 		for coord in coords:
# 			plt.plot(coord[0], coord[1], color='black')
# 	else:
# 		plt.plot(*shape.exterior.xy, color='black')

# parcels_df.plot(ax=ax, color='black')
# sidewalks_df.plot(ax=ax, color='#B362FF')
# streets_df.plot(ax=ax, color='#F8FF62')
# streets_df.plot(ax=ax, color='black', alpha=.25)
# # streets_with_sidewalks.plot(ax=ax, color="#4A98FC")
# # street_indv.plot(ax=ax, color='black')
# campus_df.plot(ax=ax, color='brown')
# neighborhood_centroids.plot(ax=ax, color='black', marker='x', markersize=1.5)

# for i in range(len(streetAsList)):
# print(streetAsList[0])

# street_indv.points.plot(ax=ax, color='black', marker='o')
# print(streetAsList[0][0])
# print('=====================\n\n\n\n\n\n\n\n\n\n\n\n\n check from here')


# GET ENDS OF STREETS
# coordsToUse = {}
# util.coord_street_table = {}

# util.getAllCoords(streets_df)


# print(len(util.coordsToUse))
# print(len(util.coord_street_table.keys()))

# sidewalk_lines = [shape(line['geometry']) for line in fiona.open("./Washington_SHARE/Sidewalks_Washington.shp")]




# sidewalk_inters = getIntersections(sidewalk_lines)
# endpts = []
# for index, line in enumerate(lines):
#   if (line.type == 'LineString'):
#       # endpts.append((Point(list(line.coords)[0]), Point(list(line.coords)[-1])))
#       pass
#   else:
#       # for geom in line:
#       print(line)
		# print((Point(line['geometry']['coordinates'][0]), Point(line['geometry']['coordinates'][-1])))
# street_inters = util.getIntersections()


# for point in util.coordsToUse.keys():
# 	util.addToCoordStreeTable(point)


# street_endpoints = [(Point(list(line.coords)[0]), Point(list(line.coords)[-1])) for line  in lines]
# print(endpts)


# intersections = []
# for point in street_inters:
# 	coords = list(point.coords)
# 	util.coordsToUse[coords[0]] = 1


# util.createSegments(streets_df)
# for keys in util.segments.keys():
# 	plt.plot(*util.segments[keys].xy, color='green')

# endpoints = []
# for point in street_endpoints:
#   endpoints.extend(list(point.coords))


# print(len(lines))
# print(len(sidewalk_lines))
# print(len(streets_with_sidewalks))

# next_coords = search.getNextPoints((2219463.474054169, 1365920.2103887573))
# print(next_coords)
# streets = util.coord_street_table[(2219463.474054169, 1365920.2103887573)]
# for street in streets:
# 	x, y = street.coords[0]
# 	plt.plot(x, y, color='blue', zorder=1)
# for point in util.coordsToUse:
# 	plt.plot(point[0], point[1], color='green', marker='o', markersize='1')
	

# plt.plot(2218878.4499617554, 1365096.1014726758, color='green', marker = 'o')
# plt.plot(2220682.003769338, 1372261.9742800072, color='blue', marker = 'o')
# plt.plot(2220979.4720064215, 1371953.09202376, color='blue', marker='o')
# plt.plot(2219191.4135746695, 1366610.3648483455, color='red', marker='x')


# for point in next_coords:
#   plt.plot(point[0], point[1], color='red', marker='o')


# line = [(2221821.531345919, 1367792.9743597582), (2221823.140922755, 1367912.345512092), (2221823.6346881688, 1367948.9658456743), (2221824.1898051687, 1367990.1134011745), (2221825.6756945886, 1368108.4625739232), (2221826.7895375043, 1368185.2216067612), (2221827.770834755, 1368252.8448310941), (2221828.6556755044, 1368316.889978595), (2221828.9607930034, 1368338.9703150094), (2221830.171092421, 1368433.4465040118), (2221831.2029145025, 1368499.1045091748), (2221834.4319106713, 1368751.9471793398), (2221835.460780002, 1368821.9913305938), (2221835.7380104214, 1368840.8561222628), (2221837.5008021705, 1368891.8409284279), (2221839.2537514195, 1369076.2427905947), (2221840.579208087, 1369234.8438513428), (2221841.7032215856, 1369369.3350521773), (2221843.949280087, 1369622.834873259), (2221845.358726088, 1369784.316505678), (2221847.26160942, 1370002.3478937596), (2221848.4840479195, 1370147.9447154254), (2221848.5263706706, 1370156.4086092561), (2221848.693693172, 1370189.9603794292), (2221848.2921191715, 1370320.3265885115), (2221847.7688262537, 1370490.1999364272), (2221848.5244021714, 1370660.4889659286), (2221849.18877092, 1370810.2140601724), (2221850.8931638375, 1371131.496882178), (2221850.977809336, 1371147.4525589272), (2221852.773081336, 1371487.2130342573), (2221853.9827245884, 1371719.1020061746), (2221854.250768669, 1371781.1005698442), (2221854.9584444202, 1371944.7035890892)]
# for point in line:
#   plt.plot(point, color='red', marker='x')

# (2220662.483467169, 1370346.599173762)


# get the intersection closest to parcel centroid






# street_point_for_parcel = []
# for centroid in neighborhood_centroids:
# 	point = getStreetIntersection(centroid.coords[0])
# 	street_point_for_parcel.append(point)
# 	plt.plot(point[0], point[1], color='black', marker='o', markersize=2)

# points_in_path, visited, fringe = search.aStarSearch((2220682.003769338, 1372261.9742800072), (2218878.4499617554, 1365096.1014726758))
# print("=========================================")
# streets = getStreets(points_in_path)
# print(streets)


# for street in streets:
# 	print(street)
# 	# for point in street:
# 	# x, y = street.xy
# 	plt.plot(*street.xy, color='red', opcaticy=.2)

# for i in range(len(street_point_for_parcel)):
# 	points_in_path, visited, fringe = search.aStarSearch(street_point_for_parcel[i], (2218878.4499617554, 1365096.1014726758))
# 	# points_in_path = list(dict.fromkeys(points_in_path))
# 	streets = getStreets(points_in_path)
# 	# for street in fake_streets:
# 	# 	if street.type == 'LineString':
# 	# 		plt.plot(*street.xy, color='blue', alpha=.75)
# 	for street in streets:
# 		if street.type == 'LineString':
# 			plt.plot(*street.xy, color='red', alpha=.33)
	# for point in points_in_path:
	# 	plt.plot(point[0], point[1], color='black', marker='x')
# print(visited)
# print(points_in_path)

# for point in visited:
# 	plt.plot(point[0], point[1], color='red', marker='x')

# while not fringe.isEmpty():
# 	priority, node = fringe.pop()
# 	plt.plot(node[0][0], node[0][1], color='blue', marker='x')

# for point in points_in_path:
# 	plt.plot(point[0], point[1], color='black', marker='x')

# for path in points_in_path:
# 	for points in path:
# 		plt.plot(points[0], points[1], color="red", alpha=0.1, marker='o')



########################
# Incorporate beltline #
########################


# access_points_on_beltline = {}
# usable_coords = {}
# # get access point on the belt_line adn find the 

# access_points = [shape(point['geometry']) for point in fiona.open("./Washington_SHARE/BeltLine_AccessPts_Washington.shp")]

# def all_beltline_coords():
# 	lines = beltline_trail_df.geometry
# 	points = []
# 	for line in lines:
# 		usable_coords[(line.coords[0][0], line.coords[0][1])] = 1
# 		usable_coords[(line.coords[-1][0], line.coords[-1][1])] = 1
# 		print(line.coords[0], line.coords[-1])
# 		for point in line.coords:
# 			points.append(Point(point[0], point[1]))
# 	return points

# points = all_beltline_coords()




# def find_true_access_points():
# 	print("getting access points")
# 	print(access_points)
# 	min_beltline_points = []
# 	for point in access_points:
# 		dist = [(line_point.distance(point)) for line_point in points]
# 		min_index = dist.index(min(dist))
# 		min_beltline_points.append(points[min_index])
# 		print(point.coords[0])
# 		print(points[min_index].coords[0])
# 		access_points_on_beltline[(point.coords[0], points[min_index].coords[0])] = LineString([point, Point(points[min_index])])
# 		usable_coords[points[min_index].coords[0]] = 1
# 		# util.coordsToUse[points[min_index].coords[0]] = 1
# 		# util.coordsToUse[point.coords[0]] = 1

# 	return access_points_on_beltline


# print(access_points)
# print("about to get access points")
# access_points_on_beltline = find_true_access_points()



# # # for point in access_points_on_beltline.keys():
# # 	# plt.plot(point[1][0], point[1][1], color='blue', marker='x')
# # 	# plt.plot(*access_points_on_beltline[point].xy, color='blue')



# # # join streets with access_points
# access_points_intersections = {}


# def create_access_point_segments():
# 	min_intersection = []
# 	coords = list(util.coordsToUse.keys())
# 	for point in access_points:
# 		dist = [Point(intersection).distance(point) for intersection in coords]
# 		min_index = dist.index(min(dist))
# 		min_intersection.append(coords[min_index])
# 		access_points_intersections[(point.coords[0], coords[min_index])] = LineString([point, Point(coords[min_index])])


# create_access_point_segments()




# for point in access_points_intersections.keys():
# 	plt.plot(point[1][0], point[1][1], color='blue', marker='x')
# 	plt.plot(*access_points_intersections[point].xy, color='blue')

# util.getAllCoords(beltline_trail_df)



# get line segments on beltline
# beltline_segments = {}

# def create_beltline_segments():
# 	lines = [lines for lines in beltline_trail_df.geometry]
# 	for line in lines:
# 		if line.type == 'LineString':
# 			coords = [(coord[0], coord[1]) for coord in line.coords]
# 			start = 0
# 			for i in range(len(coords)):
# 				if coords[i] in usable_coords and i > 0:
# 					beltline_segments[(coords[start], coords[i])] = LineString(coords[start:i+1])
# 					start = i

# create_beltline_segments()

# print(beltline_segments)
# print(access_points_intersections)
# print(access_points_on_beltline)
# for seg in beltline_segments.keys():
# 	plt.plot(seg[0][0], seg[0][1], color='blue', marker='x')
# 	plt.plot(seg[1][0], seg[1][1], color='blue', marker='x')
# 	plt.plot(*beltline_segments[seg].xy, color='blue')

# util.segments.update(beltline_segments)
# util.segments.update(access_points_on_beltline)
# util.segments.update(access_points_intersections)

# print(util.segments)

# util.get_all_beltline_points(beltline_trail_df, beltline_Access_pts_df)

# # manually manipulate beltline
# lines = [lines for lines in beltline_trail_df.geometry]
# util.segments[(lines[0].coords[0], lines[1].coords[-1])] = LineString([lines[0].coords[0],lines[1].coords[-1]])
# util.segments[(lines[1].coords[0], lines[3].coords[-1])] = LineString([lines[1].coords[0],lines[3].coords[-1]])
# util.segments[(lines[4].coords[-1], lines[9].coords[-1])] = LineString([lines[4].coords[-1],lines[9].coords[-1]])
# plt.plot(*util.segments[(lines[4].coords[-1], lines[9].coords[-1])].xy, color='black')


#street_point_for_parcel is all the neighborhood parcels



# search paths
# for i in range(len(street_point_for_parcel)):
# 	points_in_path, visited, fringe = search.aStarSearch(street_point_for_parcel[i], (2218878.4499617554, 1365096.1014726758))
# 	# points_in_path = list(dict.fromkeys(points_in_path))
# 	streets = getStreets(points_in_path)
# 	# for street in fake_streets:
# 	# 	if street.type == 'LineString':
# 	# 		plt.plot(*street.xy, color='blue', alpha=.75)
# 	for street in streets:
# 		if street.type == 'LineString':
# 			plt.plot(*street.xy, color='red', alpha=.33)
# 		for point in visited:
# 			plt.plot(point[0], point[1], color='black', marker='x')


# print(beltline_points)
# for point in util.coordsToUse.keys():
# 	plt.plot(point[0], point[1], color='blue', marker='x')










# plt.show()







