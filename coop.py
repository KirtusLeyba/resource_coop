import numpy as np

### The space node class represents the spatial container for agents and
### resources
class SpaceNode:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.neighbors = []
        self.resources = 1.0
        self.agentHere = None

    def tostr(self):
        return str(self.x) + ", " + str(self.y)

    def __hash__(self):
        return hash(self.tostr())

    def __eq__(self, other):
        return hash(self) == hash(other)

### creates a rectangle grid of width and height, adds neighbors
def createRectangleGrid(width, height):
    grid = []

    for i in range(width):
        grid.append([])
        for j in range(height):
            s = SpaceNode(i,j)
            grid[i].append(s)

    ### assign neighbors
    for i in range(width):
        for j in range(height):
            for ii in range(-1,2):
                for jj in range(-1,2):
                    if(i+ii >= 0 and i+ii < width \
                        and j+jj >= 0 and j+jj < width \
                        and not(ii == 0 and jj ==0)):
                        grid[i][j].neighbors.append(grid[i+ii][j+jj])
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
        ### actions
        # move 8
        # steal 8
        # trade 8
        # pick-up 1
        # rest 1
        # reproduce 1
        self.numActions = 8*3 + 2
        self.n = n
        self.nodeAt = None
        self.pastMoves = np.zeros(n)

        ### resource storage
        self.resources = 10.0

        ### action costs
        self.moveCost = 0.0001
        self.stealGain = 0.25
        self.stealCost =  0.1
        self.tradeCost = 0.5 #is also trade gain for trade partner
        self.pickupCost = 0.1
        self.pickupGain = 0.5
        self.reproduceCost = 0.0
        self.reprodRate = 0.1
        self.mutationRate =  0.05
        self.aging = 0.0001

        ### sense vector
        self.s = np.zeros(self.numSenses)
        ### brain
        self.B = np.zeros((self.numSenses, self.numActions))
        ### actions
        self.a = np.zeros(self.numActions)

    def __eq__(self, other):
        if(other == None):
            return False
        elif(self.x == other.x and self.y == other.y):
            return True
        return False

    def __neq__(self, other):
        return not(self == other)

    def __hash__(self):
        return hash(str(self.x) + ", " + str(self.y))

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
        self.a = np.dot(self.s, self.B)

    def randomizeBrain(self):
        self.B = np.random.random((self.numSenses, self.numActions))

    def takeAction(self):

        offSpring = None

        actionIndex = np.argmax(self.a)

        ### move
        if(actionIndex >= 0 and actionIndex < 8):
            if(len(self.nodeAt.neighbors) > actionIndex):
                if(self.nodeAt.neighbors[actionIndex].agentHere == None):
                    self.nodeAt.neighbors[actionIndex].agentHere = self
                    self.nodeAt.agentHere = None
                    self.nodeAt = self.nodeAt.neighbors[actionIndex]
                    self.x = self.nodeAt.x
                    self.y = self.nodeAt.y
            self.resources -= self.moveCost

        ## steal
        if(actionIndex >= 8 and actionIndex < 16):
            if(len(self.nodeAt.neighbors) > actionIndex-8):
                if(self.nodeAt.neighbors[actionIndex-8].agentHere != None):
                    if(self.nodeAt.neighbors[actionIndex-8].agentHere.resources > self.stealGain):
                        self.nodeAt.neighbors[actionIndex-8].agentHere.resources -= self.stealGain
                        self.resources += self.stealGain
                    else:
                        self.resources += self.nodeAt.neighbors[actionIndex-8].agentHere.resources
                        self.nodeAt.neighbors[actionIndex-8].agentHere.resources = 0
            self.resources -= self.stealCost

        ##trade
        if(actionIndex >=16 and actionIndex < 24):
            if(len(self.nodeAt.neighbors) > actionIndex-16):
                if(self.nodeAt.neighbors[actionIndex-16].agentHere != None):
                    if(self.resources > self.tradeCost):
                        self.nodeAt.neighbors[actionIndex-16].agentHere.resources += self.tradeCost
                        self.resources -= self.tradeCost
                    else:
                        self.nodeAt.neighbors[actionIndex-16].agentHere.resources += self.resources
                        self.resources = 0
            
         ##pickup
        if(actionIndex == 24):
            if(self.nodeAt.resources > self.pickupGain):
                self.nodeAt.resources -= self.pickupGain
                self.resources += self.pickupGain
            else:
                self.resources += self.nodeAt.resources
                self.nodeAt.resources = 0.0
            self.resources -= self.pickupCost
        
        ##reproduce
        if(np.random.random() < self.reprodRate):
            reproIndex = np.random.randint(0,9)
            if(len(self.nodeAt.neighbors) > reproIndex):
                if(self.nodeAt.neighbors[reproIndex].agentHere == None):
                    a = Agent(self.nodeAt.neighbors[reproIndex].x, self.nodeAt.neighbors[reproIndex].y, 2)
                    a.B = np.add(self.B, np.random.random((self.numSenses, self.numActions))*self.mutationRate)
                    a.resources = self.resources/2
                    self.nodeAt.neighbors[reproIndex].agentHere = a
                    a.nodeAt = self.nodeAt.neighbors[reproIndex]
                    self.nodeAt.neighbors[reproIndex].agentHere = a
                    self.resources /= 2
                    offSpring = a
            self.resources -= self.reproduceCost

        self.resources -= self.aging

        if(self.resources < 0.0):
            self.resources = 0.0

        return offSpring
                    
                    
            