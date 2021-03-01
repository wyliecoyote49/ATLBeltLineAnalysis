import sys
import util
from shapely.geometry import Point, Polygon, LineString, mapping, shape
import math



# FUNCTIONS FOR PATH SEARCHING


def flatten(street):
	uniqueCords = []
	if street.type == "LineString":
		for coords in street.coords:
			if coords in util.coordsToUse.keys():
				uniqueCords.append(coords)
	elif street.type == "MultiLineString":
		lines = [line for line in street]
		i = 0
		found = False
		while(i < len(lines)):
			coords = lines[i].coords
			for index, coord in enumerate(coords):
				if coord in util.coordsToUse.keys():
					uniqueCords.append(coord)
			i += 1

	return uniqueCords


def getNextPoints(point):
	next_pos = []
	moves = []
	next_streets = util.segments.keys()


	for street in next_streets:
		if (street[0] == point):
			next_pos.append(street[1])
		elif(street[1] == point):
			next_pos.append(street[0])
	
	return next_pos


# COST FUNCTION FOR ROAD
	# start simple with distace = cost
	# is this an okay way to treat distance?

def getCost(moves):
	cost = 0
	for i in range(len(moves) - 1):
		# distance cost
		diff_x = moves[i][0] - moves[i+1][0]
		diff_y = moves[i][1] - moves[i+1][1]
		aux_dist = math.sqrt((diff_x ** 2) + (diff_y ** 2))
		aux_dist = aux_dist/5280

		# beltline benefit
		if moves[i] in util.beltline_points or moves[i+1] in util.beltline_points:
			cost += aux_dist
		else:
			cost += aux_dist + 1

		# get type cost
		if  (moves[i], moves[i+1]) in util.segments.keys():
			type_cost = getTypeCost(util.segments[(moves[i], moves[i+1])][2]) * 1
			cost += type_cost
		elif (moves[i+1], moves[i]) in util.segments.keys():
			type_cost = getTypeCost(util.segments[(moves[i+1], moves[i])][2]) * 1
			cost += type_cost

		# sidewalk cost 
		if (moves[i], moves[i+1]) in util.segments.keys():
			if util.segments[(moves[i], moves[i+1])][4] == False:
				cost += 1
		elif (moves[i+1], moves[i]) in util.segments.keys():
			if util.segments[(moves[i+1], moves[i])][4] == False:
				cost += 1

		# Check if in high injury Network
		
		# in_HIN = inHighInjuryNetwork(Point(moves[i+1]))
		# if in_HIN == True:
		# 	print('Found')
		# 	cost += 1

	return cost

def getTypeCost(type):
	if type == '':
		return 0
	elif type == 'Local':
		return 1
	elif type == 'Collector':
		return 2
	elif type == 'Minor Arterial':
		return 3
	elif type == 'Minor Arterial 2':
		return 4
	elif type == 'Major Arterial':
		return 5

def inHighInjuryNetwork(point):
	for buff in util.high_injury_points:
		if point.within(buff):
			return True
	return False

def getDistance(moves):
	dist = 0
	for i in range(len(moves) - 1):
		diff_x = moves[i][0] - moves[i+1][0]
		diff_y = moves[i][1] - moves[i+1][1]
		aux_dist = math.sqrt((diff_x ** 2) + (diff_y ** 2))
		dist += aux_dist	
	return dist

def getPathOnBeltline(moves):
	dist = 0
	for i in range(len(moves) - 1):
		diff_x = moves[i][0] - moves[i+1][0]
		diff_y = moves[i][1] - moves[i+1][1]
		aux_dist = math.sqrt((diff_x ** 2) + (diff_y ** 2))
		if moves[i] in util.beltline_points or moves[i+1] in util.beltline_points:
			dist += aux_dist	
	return dist

def heuristic(nextState, goalState):
	diff_x = nextState[0] - goalState[0]
	diff_y = nextState[1] - goalState[1]
	dist = math.sqrt((diff_x ** 2) + (diff_y ** 2))
	return dist/5280


def aStarSearch(start_state, goal_state):

	start = start_state
	visited = []
	paths = []
	fringe = util.priorityQueue()
	fringe.push((start, []), heuristic(start_state, goal_state))
	while not fringe.isEmpty():
		priority, node = fringe.pop()
		state = node[0]
		moves = node[1]
		if state == goal_state:
			moves = moves + [state]
			return moves, visited, fringe
		if state not in visited:
			for child in getNextPoints(state):
				if not child in visited:
					newNode = (child, moves + [state])
					cost = getCost(newNode[1] + [child]) + heuristic(newNode[0], goal_state)
					fringe.push((child, moves + [state]), cost)
			visited.append(state)

	return moves, visited, fringe
	util.raiseNotDefined()





	


	