import numpy as np

### The space node class represents the spatial container for agents and
### resources
class SpaceNode:
	def __init__(self, x, y)
		self.x = x
		self.y = y
		self.neighbors = []
		self.resources = 0.0
		self.agentHere = None

	def __str__(self):
		return str(self.x) + ", " + str(self.y)

	def __hash__(self):
		return hash(str(self))

	def __eq__(self, other):
		return hash(self) == hash(other)

### creates a rectangle grid of width and height, adds neighbors
def createRectangleGrid(width, height):
	grid = []

	for i in range(width):
		for j in range(height):
			s = SpaceNode(i,j)
			grid.append(s)

	### assign neighbors
	for i in range(width):
		for j in range(height):
			for ii in range(-1,2):
				for jj in range(-1,2):
					if(ii >= 0 and ii < width \
						and jj >= 0 and jj < width \
						and not(ii == 0 and jj ==0)):
						grid[i][j].neighbors.append(grid[ii][jj])
	return grid

### Agent of the simulation
# x,y position
# n number of previous moves to track
# TODO: Encode categorical inputs
class Agent:
	def __init__(self, x, y, n):
		self.x = x
		self.y = y
		self.neighbors = []
		self.numSenses = 9 + 8*n + 8
		self.numActions = (9*8)*2 + 12
		self.n = n
		self.nodeAt = None
		self.pastMoves = np.zeros(n)

		### sense vector
		self.s = np.zeros(self.numSenses)
		### brain
		self.B = np.zeros((self.numSenses, self.numActions))
		### actions
		self.a = np.zeros(self.numActions)

	### calculate the sense vector
	def calcSenseVector(self):
		self.s = np.zeros(self.numSenses)
		### check resources
		i = 0
		self.s[i] = self.nodeAt.resources
		i += 1
		for node in self.nodeAt.neighbors:
			self.s[i] = node.resources
			i += 1
		for node in self.nodeAt.neighbors:
			if(node.agentHere != None):
				self.s[i] = 1.0
			i += 1
		for node in self.nodeAt.neighbors:
			if(node.agentHere != None):
				for j in node.agentHere.pastMoves:
					self.s[i] = j
					i += 1

	### determine what action to take
	def calcAction(self):
		self.a = np.dot(self.B, self.s)