import pygame, sys
from time import sleep, time
import random
import math
from priodict import priorityDictionary
from pygame.locals import *

pygame.init()

FPS = 30 # frames per second setting
fpsClock = pygame.time.Clock()

# Set up the window
DISPLAYSURF = pygame.display.set_mode((600, 500), 0, 32)
pygame.display.set_caption('Project Simulation')

WHITE = (255, 255, 255)

# Sprites
quadcopter = pygame.image.load('quadcopter-top2.png')
cloud1 =  pygame.image.load('cloud.jpg')
cloud2 =  pygame.image.load('cloud.jpg')
darkRed = (255,0,0)
point = pygame.image.load('point.png')

# GPS Markers
marker = pygame.image.load('marker.png')

# Obstructions
obstructions = pygame.image.load('obstruction.png')
obstructions_dim = pygame.image.load('obstruction-dim.png')

# Starting position
xOriginal = 10
yOriginal = 10
xDirection = xOriginal
yDirection = yOriginal
xCloud = xOriginal
yCloud = yOriginal

# LIDAR Sway
sway = 0
swayCount = 0
xLidar = xDirection - 10
yLidar = yDirection + 50

# Graph
G = {}

nodes = [[]]

# curr -> north, south, east, west, northeast, southeast, northwest, southwest

def nodeUpdater(node):
    block = {
        str(node): {str(node[0], node[1] + 30):0, str(node[0], node[1] - 30):0, str(node[0] + 30, node[1]):0, str(node[0] - 30, node[1]):0, str(node[0] + 30, node[1] + 30):0, str(node[0] + 30, node[1] - 30):0, str(node[0] - 30, node[1] + 30):0, str(node[0] - 30, node[1] - 30):0},
        str(node[0], node[1] + 30): {str(node[0] - 30, node[1] + 30):0, str(node[0] + 30, node[1] + 30):0, str(node):0},
        str(node[0], node[1] - 30): {str(node[0] - 30, node[1] - 30):0, str(node[0] + 30, node[1] - 30):0, str(node):0},
        str(node[0] + 30, node[1]): {str(node[0] + 30, node[1] + 30):0, str(node[0] + 30, node[1] - 30):0, str(node):0},
        str(node[0] - 30, node[1]): {str(node[0] - 30, node[1] + 30):0, str(node[0] - 30, node[1] + 30):0, str(node):0},
        str(node[0] + 30, node[1] + 30): {str(node[0], node[1] + 30):0, str(node[0] + 30, node[1]):0, str(node):0},
        str(node[0] + 30, node[1] - 30): {str(node[0], node[1] + 30):0, str(node[0] - 30, node[1]):0, str(node):0},
        str(node[0] + 30, node[1] - 30): {str(node[0], node[1] - 30):0, str(node[0] + 30, node[1]):0, str(node):0},
        str(node[0] - 30, node[1] - 30): {str(node[0], node[1] - 30):0, str(node[0] - 30, node[1]):0, str(node):0}
        }
    return block


for pointx in range(0, 600, 30):
    for pointy in range(0, 500, 30):
       nodes.append([pointx, pointy])
'''
for node in nodes:
    if "[node[0] - 30, node[1]]" not in nodes:
        nodes.append("[node[0] - 30, node[1]]")
    elif "[node[0] + 30, node[1]]" not in nodes:
        nodes.append("[node[0] + 30, node[1]]")
    elif "[node[0] - 30, node[1] + 30]" not in nodes:
        nodes.append("[node[0] - 30, node[1] + 30]")
    elif "[node[0] - 30, node[1] - 30]" not in nodes:
        nodes.append("[node[0] - 30, node[1] - 30]")
    elif "[node[0], node[1] + 30]" not in nodes:
        nodes.append("[node[0], node[1] + 30]")
    elif "[node[0], node[1] - 30]" not in nodes:
        nodes.append("[node[0], node[1] - 30]")
    elif "[node[0], node[1]]" not in nodes:#
        nodes.append("[node[0] - 30, node[1]]")

for node in nodes:
    nodeGraph = nodeUpdater(node)
    G.update(nodeGraph)
'''
# State Machine
state_machine = ["Dijkstra Search", "Autonomous Search", "Landing", "Manual Search"]
current_state = state_machine[0]
holdPlace = 0

# 2D Makeshift GPS Coordinates -> Valid from 0,0 to 600,500
gps = [[100,200], [300,400], [500,400]]
costList = [0] * len(gps)

# 2D Makeshift Obstruction Coordinates -> Valid from 0,0 to 600,500
obs = [[120,248]]
found_obstacles = []

while True: # the main game loop
    DISPLAYSURF.fill(WHITE)
    DISPLAYSURF.blit(quadcopter, (xDirection, yDirection))

    # Display Current State
    font = pygame.font.Font(None, 20)
    state_display = "Current State: " + current_state
    text = font.render(state_display, 1, (10, 10, 10))
    textpos = text.get_rect()
    background = pygame.Surface(DISPLAYSURF.get_size())
    textpos.centerx = background.get_rect().centerx
    DISPLAYSURF.blit(text, textpos)

    # Diplay GPS Coordinate Locations
    for coordinates in gps:
        update = gps.index(coordinates)
        DISPLAYSURF.blit(marker, (coordinates[0], coordinates[1]))
        costList[update] = (abs(coordinates[0] - xDirection) + abs(coordinates[1] - yDirection))
        target = gps[costList.index(min(costList))]
        if (coordinates[0] == xDirection and coordinates[1] == yDirection):
            gps.pop(update)
            costList.pop(update)
        if len(gps) == 0:
            target = [xOriginal, yOriginal]

    # Display Found Obstacles
    for obstructs in found_obstacles:
            DISPLAYSURF.blit(obstructions, (obstructs[0], obstructs[1]))

    # Display Unfound Obstacles
    for hidden_obstructs in obs:
            DISPLAYSURF.blit(obstructions_dim, (hidden_obstructs[0], hidden_obstructs[1]))
            
    # Display Points of Graph on Map
    for pointx in range(0, 600, 30):
        for pointy in range(0, 500, 30):
            DISPLAYSURF.blit(point, (pointx, pointy))
            if [pointx, pointy] not in nodes:
                nodes.append([pointx, pointy])
            
    # LIDAR Search Emulation
    if current_state != state_machine[0]:
        pygame.draw.line(DISPLAYSURF, darkRed, (xDirection + 20, yDirection + 20), (xLidar, yLidar), 2)
        
        for obstructs in obs:
            distance1 = math.sqrt((xDirection + 20 - xLidar)**2 + (yDirection + 20 - yLidar)**2) # Length of LIDAR
            distance2 = math.sqrt((xDirection + 20 - obstructs[0])**2 + (yDirection + 20 - obstructs[1])**2)
            # From beginning of LIDAR to object
            distance3 = math.sqrt((obstructs[0] - xLidar)**2 + (obstructs[1] - yLidar)**2) # From end of LIDAR to object
            offset10=(distance2+distance3)*0.15
            distanceTotal=(distance2+distance3)
            if ((distance1 > distanceTotal-offset10) and (distance1 < distanceTotal+offset10)):
                found_obstacles.append(obstructs)
                obs.pop(obs.index(obstructs))
                current_state = state_machine[0]

        if sway == 0:
            if xLidar < xDirection + 40:
                swayCount += 1
                xLidar = xDirection + swayCount
                yLidar = yDirection + 60
            else:
                sway = 1
                swayCount = 40
        elif sway == 1:
            if xLidar > xDirection:    
                swayCount -= 1
                xLidar = xDirection + swayCount
                yLidar = yDirection + 60
            else:
                sway = 0
                swayCount = 0
                
    # State Machine
    if current_state == state_machine[0]: # Dijkstra Search
        if holdPlace < 50:
            holdPlace += 1
        else:
            current_state = state_machine[1]
            holdPlace = 0
            
    elif current_state == state_machine[1]: # Autonomous Search
        if (target[0] - xDirection) > 0:
            xDirection += 2
        elif (target[0] - xDirection) == 0:
            xDirection += 0
        else:
            xDirection -= 2

        if (target[1] - yDirection) > 0:
            yDirection += 2
        elif (target[1] - yDirection) == 0:
            yDirection += 0
        else:
            yDirection -= 2
            
        '''
        
        for obstructs in obs:
            DISPLAYSURF.blit(obstructions, (obstructs[0], obstructs[1]))
            if (obstructs[0] == xDirection + 1):
                gps.append([xDirection + 1, yDirection - 1])
                costList.append([xDirection + 1, yDirection - 1])
            elif (obstructs[1] == yDirection + 1):
                gps.append([xDirection + 1, yDirection + 1])
                costList.append([xDirection + 1, yDirection + 1])
            elif(obstructs[0] == xDirection - 1):
                gps.append([xDirection - 1, yDirection + 1])
                costList.append([xDirection - 1, yDirection + 1])
            elif(obstructs[1] == yDirection - 1):
                gps.append([xDirection + 1, yDirection - 1])
                costList.append([xDirection + 1, yDirection - 1])

        # LIDAR Emulation
        rand1 = random.randrange(0, 300)
        rand2 = random.randrange(1, 4)
        if rand1 == 7:
            if rand2 == 1:
                obs.append([xDirection, yDirection + 15])
            elif rand2 == 2:
                obs.append([xDirection, yDirection - 15])
            elif rand2 == 3:
                obs.append([xDirection + 15, yDirection])
            elif rand2 == 4:
                obs.append([xDirection - 15, yDirection])

        # Autonomous Control
           ''' 
    # Manual Controls        
    for event in pygame.event.get():
        '''
        if event.type==pygame.KEYDOWN:
            
            if event.key==pygame.K_RIGHT:
                    xDirection += 2
                
            if event.key==pygame.K_LEFT:
                    xDirection -= 2
        
            if event.key==pygame.K_UP:
                    yDirection -= 2
                   
            if event.key==pygame.K_DOWN:
                    yDirection += 2
        '''            
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()
    fpsClock.tick(FPS)
    
def Dijkstra(G,start,end=None):

	D = {}	# dictionary of final distances
        P = {}	# dictionary of predecessors
        Q = priorityDictionary()	# estimated distances of non-final vertices
        Q[start] = 0
        
	for v in Q:
            D[v] = Q[v]
            if v == end: break
            
            for w in G[v]:
                vwLength = D[v] + G[v][w]
                if w in D:
                    if vwLength < D[w]:
                        raise ValueError, "Dijkstra: found better path to already-final vertex"
                elif w not in Q or vwLength < Q[w]:
                    Q[w] = vwLength
                    P[w] = v

        return (D,P)
    
def shortestPath(G,start,end):

	D,P = Dijkstra(G,start,end)
	Path = []
	while 1:
		Path.append(end)
		if end == start: break
		end = P[end]
	Path.reverse()
	return Path

#print shortestPath(G,'s','v')
print G
