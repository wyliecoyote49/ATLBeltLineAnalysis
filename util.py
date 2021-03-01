import sys
import heapq
import geopandas as gpd
from shapely.geometry import Point, Polygon, LineString, mapping, shape
import fiona
import itertools






class priorityQueue:
	
	def __init__(self):

		self.heap = []
		self.count = 0

	def push(self, item, priority):
		entry = (priority, self.count, item)
		heapq.heappush(self.heap, entry)

		self.count += 1

	def pop(self):
		(priority, _, item) = heapq.heappop(self.heap)
		return priority, item

	def isEmpty(self):
		return len(self.heap) == 0




class Stack:
	"A container with a last-in-first-out (LIFO) queuing policy."
	def __init__(self):
		self.list = []

	def push(self,item):
		"Push 'item' onto the stack"
		self.list.append(item)

	def pop(self):
		"Pop the most recently pushed item from the stack"
		return self.list.pop()

	def isEmpty(self):
		"Returns true if the stack is empty"
		return len(self.list) == 0



#########################################
# UTILITY FUNCTIONS FOR DATA EXTRACTION #
#########################################
# Potentially move to own file

coordsToUse = {}
sideWalkCoordsToUse = {}
segments = {}
beltline_points = []
sidewalk_segments = {}
high_injury_points = []



def getAllCoords(df):
	allStreetCoords = []
	streets = [lines for lines in df.geometry]
	for street in streets:
		if street.type == "LineString":
			coords = street.coords
			coordsToUse[coords[0]] = 1
			coordsToUse[coords[-1]] = 1
		elif street.type == "MultiLineString":
			for multiline in street:
				first_coords = multiline.coords[0]
				last_coords = multiline.coords[-1]
				coordsToUse[first_coords] = 1
				coordsToUse[last_coords] = 1
	return


def getIntersections(df):
	lines = [shape(line['geometry']) for line in fiona.open(df)]
	inters = []
	for line1,line2 in  itertools.combinations(lines, 2):
		if line1.intersects(line2):
			inter = line1.intersection(line2)
			if "Point" == inter.type:
				inters.append(inter)
				inter_as_coords = list(inter.coords)[0]
				coordsToUse[inter_as_coords] = 1
			elif "MultiPoint" == inter.type:
				inters.extend([pt for pt in inter])
				for pt in inter:
					inter_as_coords = list(pt.coords)[0]
					coordsToUse[inter_as_coords] = 1
			elif "MultiLineString" == inter.type:
				multiLine = [line for line in inter]
				
				first_coords = multiLine[0].coords[0]
				last_coords = multiLine[len(multiLine)-1].coords[-1]
				
				inters.append(Point(first_coords[0], first_coords[1]))
				inters.append(Point(last_coords[0], last_coords[1]))

			elif "GeometryCollection" == inter.type:
				for geom in inter:
					if "Point" == geom.type:
						inters.append(geom)
						inter_as_coords = list(geom.coords)[0]
					
						coordsToUse[inter_as_coords] = 1
					elif "MultiPoint" == geom.type:
						inters.extend([pt for pt in geom])
						for pt in geom:
							inter_as_coords = list(pt.coords)[0]
					elif "MultiLineString" == geom.type:
						multiLine = [line for line in geom]
						first_coords = multiLine[0].coords[0]

						last_coords = multiLine[len(multiLine)-1].coords[-1]

						inters.append(first_coords)
						inters.append(last_coords)


	intersections = []
	for point in inters:
		coords = list(point.coords)

	return intersections



def getAllSidewalkCoords(df):
	allStreetCoords = []
	streets = [lines for lines in df.geometry]
	for street in streets:
		if street.type == "LineString":
			coords = street.coords
			sideWalkCoordsToUse[coords[0]] = 1
			sideWalkCoordsToUse[coords[-1]] = 1
		elif street.type == "MultiLineString":
			for multiline in street:
				first_coords = multiline.coords[0]
				last_coords = multiline.coords[-1]
				sideWalkCoordsToUse[first_coords] = 1
				sideWalkCoordsToUse[last_coords] = 1

	return


def getSidewalkIntersections(df):
	lines = [shape(line['geometry']) for line in fiona.open(df)]
	inters = []
	for line1,line2 in  itertools.combinations(lines, 2):
		if line1.intersects(line2):
			inter = line1.intersection(line2)
			if "Point" == inter.type:
				inters.append(inter)
				inter_as_coords = list(inter.coords)[0]
				sideWalkCoordsToUse[inter_as_coords] = 1
			elif "MultiPoint" == inter.type:
				inters.extend([pt for pt in inter])
				for pt in inter:
					inter_as_coords = list(pt.coords)[0]
					sideWalkCoordsToUse[inter_as_coords] = 1
			elif "MultiLineString" == inter.type:
				multiLine = [line for line in inter]
				
				first_coords = multiLine[0].coords[0]
				last_coords = multiLine[len(multiLine)-1].coords[-1]
				
				inters.append(Point(first_coords[0], first_coords[1]))
				inters.append(Point(last_coords[0], last_coords[1]))

			elif "GeometryCollection" == inter.type:
				for geom in inter:
					if "Point" == geom.type:
						inters.append(geom)
						inter_as_coords = list(geom.coords)[0]
					
						sideWalkCoordsToUse[inter_as_coords] = 1
					elif "MultiPoint" == geom.type:
						inters.extend([pt for pt in geom])
						for pt in geom:
							inter_as_coords = list(pt.coords)[0]
					elif "MultiLineString" == geom.type:
						multiLine = [line for line in geom]
						first_coords = multiLine[0].coords[0]

						last_coords = multiLine[len(multiLine)-1].coords[-1]

						inters.append(first_coords)
						inters.append(last_coords)


	intersections = []
	for point in inters:
		coords = list(point.coords)

	return intersections



def createSegments(df, include_sidewalks):
	streets = [lines for lines in df.geometry]
	usable_coords = coordsToUse.keys()

	for index, street in enumerate(streets):
		if street.type == 'LineString':
			coords = street.coords
			start = 0
			for i in range(len(coords)):
				if coords[i] in usable_coords and i > 0:
					segments[(coords[start], coords[i])] = ((coords[start], coords[i]),LineString(coords[start:i+1]), df.loc[index, 'FUNCCLASS'], df.loc[index, 'LABEL'], has_sidewalk((coords[start], coords[i]), include_sidewalks))
					start = i
		elif street.type == 'MultiLineString':
			for line in street:
				coords = line.coords
				start = 0
				for i in range(len(coords)):
					if coords[i] in usable_coords and i > 0:
						segments[(coords[start], coords[i])] = ((coords[start], coords[i]), LineString(coords[start:i+1]), df.loc[index, 'FUNCCLASS'], df.loc[index, 'LABEL'], has_sidewalk((coords[start], coords[i]), include_sidewalks))
						start = i



def createSidewalkSegments(df):
	streets = [lines for lines in df.geometry]
	usable_coords = sideWalkCoordsToUse.keys()

	for index, street in enumerate(streets):
		if street.type == 'LineString':
			coords = street.coords
			start = 0
			for i in range(len(coords)):
				if coords[i] in usable_coords and i > 0:
					sidewalk_segments[(coords[start], coords[i])] = LineString(coords[start:i+1])
					start = i
		elif street.type == 'MultiLineString':
			for line in street:
				coords = line.coords
				start = 0
				for i in range(len(coords)):
					if coords[i] in usable_coords and i > 0:
						sidewalk_segments[(coords[start], coords[i])] = LineString(coords[start:i+1])
						start = i




def has_sidewalk(segment, include_sidewalks):
	segments = sidewalk_segments.keys()
	# margin of error = 35 feet
	first_buffer = Point(segment[0]).buffer(35)
	second_buffer = Point(segment[1]).buffer(35)
	if not include_sidewalks:
		return False
	for seg in segments:
		if (Point(seg[0]).within(first_buffer)) and (Point(seg[1]).within(second_buffer)):
			return True
		elif (Point(seg[1]).within(first_buffer)) and (Point(seg[0]).within(second_buffer)):
			return True
	return False



def get_all_beltline_points(df, df2):
	lines = [lines for lines in df.geometry]
	for line in lines:
		for point in line.coords:
			beltline_points.append((point[0], point[1]))
	for point in df2.geometry:
		beltline_points.append(point.coords[0])


# TODO (implement correctly and efficiently)

def getHighInjuryNetwork(df):
	for points in df.geometry:
		high_injury_points.append(points.buffer(75.0))

def inHighInjuryNetwork(point):
	for buff in high_injury_points:
		if point.within(buff):
			return True
	return False















	