from coop import *
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import HTML
import matplotlib.animation as animation

width = 100
height = 100
grid = createRectangleGrid(width, height)

#### simulation set up
agentList = []
popSize = 100
for i in range(popSize):
    rx = np.random.randint(0, width)
    ry = np.random.randint(0, height)
    while(grid[rx][ry].agentHere != None):
        rx = np.random.randint(0, width)
        ry = np.random.randint(0, height)
    a = Agent(rx, ry, 2)
    grid[rx][ry].agentHere = a
    a.nodeAt = grid[rx][ry]
    a.randomizeBrain()
    agentList.append(a)

resources = []
count = 0.0
move = []
steal = []
trade = []
pickup = []



def init():
    im.set_data(data)
    return im,

def animate(i):
    move.append(0)
    steal.append(0)
    trade.append(0)
    pickup.append(0)
    total = len(agentList)

    data = np.zeros((width, height))

    resources.append(0.0)
    for x in range(width):
        for y in range(height):
            grid[x][y].resources += grid[x][y].resourceRate*(1-grid[x][y].resources/grid[x][y].carryingCapacity)*grid[x][y].resources
            if(grid[x][y].resources>grid[x][y].carryingCapacity):
                grid[x][y].resources=grid[x][y].carryingCapacity
            resources[-1] += grid[x][y].resources

    for _ in range(width*height):
        rx = np.random.randint(0, width-1)
        ry = np.random.randint(0, height-1)
        rindex = np.random.randint(0, len(grid[rx][ry].neighbors)-1)
        rFlow = np.random.uniform(0,(grid[rx][ry].resources-grid[rx][ry].neighbors[rindex].resources)/2)
        grid[rx][ry].resources -= rFlow
        grid[rx][ry].neighbors[rindex].resources += rFlow

    agentsToBirth = []
    agentsToKill = []
    for a in agentList:
        data[a.x, a.y] = 1.0 + a.resources
        a.calcSenseVector()
        a.calcAction()
        resultOfAction = a.takeAction()
        offspring = resultOfAction[0]
        chosenAction = resultOfAction[1]
        if(chosenAction == 1):
            move[i] += 1
        elif(chosenAction == 2):
            steal[i] += 1
        elif(chosenAction == 3):
            trade[i] += 1
        elif(chosenAction == 4):
            pickup[i] += 1
        if(offspring != None):
            agentsToBirth.append(offspring)
        if(a.resources <= 0.0000001):
            agentsToKill.append(a)
    move[i] /= total
    steal[i] /= total
    trade[i] /= total
    pickup[i] /= total
    for a in agentsToKill:
        agentList.remove(a)
    for a in agentsToBirth:
        agentList.append(a)

    im.set_data(data)

    return im,

#### Run the sim and animate live
data = np.zeros((width, height))
for a in agentList:
    data[a.x, a.y] = a.resources

fig, ax = plt.subplots()
ax.set_xlim((-0.5, width-0.5))
ax.set_ylim((-0.5, height-0.5))
im = ax.imshow(data, cmap="cividis")

anim = animation.FuncAnimation(fig, animate, init_func=init, blit=False, interval=1000/60)
plt.show()


plt.figure()
plt.plot(resources)
plt.show()

decisions=plt.figure()
plt.plot(move,label='move')
plt.plot(steal,label='steal')
plt.plot(trade,label='trade')
plt.plot(pickup,label='pickup')
plt.legend()
plt.xlabel('time')
plt.ylabel('agent decisions')
plt.title('Evolution of decision making process')
plt.show()
