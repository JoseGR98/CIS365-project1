# baselineTeam.py
# ---------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# baselineTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html
from __future__ import print_function
from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions
import game
from util import nearestPoint


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'CapsuleReflexAgent', second = 'AttackReflexAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """

  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

  def findBasicPath(self, gameState, agentIndex, travelTo):
    openNodes = [Node(gameState, None, None, 0, 0)]
    closedNodes = []
    currentNode = openNodes[0]

    while(len(openNodes) != 0):
      nodeAndIndex = self.findLowestTotalCostNodeAndPop(openNodes)
      currentNode = nodeAndIndex[0]
      currentAgentPosition = currentNode.state.getAgentPosition(agentIndex)
      del openNodes[nodeAndIndex[1]]

      legalActions = currentNode.state.getLegalActions(agentIndex)  # gameState.getLegalActions(self.index)

      successors = []
      for action in legalActions:
        # get game state after current agent moves
        successor = currentNode.state.generateSuccessor(agentIndex, action)

        heuristic = self.calculateBasicHeuristicCost(successor, successor.getAgentPosition(agentIndex), travelTo)

        successors.append(Node(
          successor,
          currentNode,
          action,
          currentNode.generalCost + 1,
          currentNode.generalCost + 1 + heuristic
          ))

      for s in successors:
        if(self.agentPositionMatchesDestination(s, travelTo)):
          path = self.generateBasicPathOfActions(s)
          return path

        if(self.nodeShouldBeOpened(s, openNodes, closedNodes)):
          openNodes.append(s)
      closedNodes.append(currentNode)
    return None

  def findPathAndCost(self, gameState, agentIndex, travelTo, maxCost):
    openNodes = [Node(gameState, None, None, 0, 0)]
    closedNodes = []
    currentNode = openNodes[0]

    while(len(openNodes) != 0):
      nodeAndIndex = self.findLowestTotalCostNodeAndPop(openNodes)
      currentNode = nodeAndIndex[0]
      currentAgentPosition = currentNode.state.getAgentPosition(agentIndex)
      del openNodes[nodeAndIndex[1]]

      legalActions = currentNode.state.getLegalActions(agentIndex)  # gameState.getLegalActions(self.index)

      successors = []
      for action in legalActions:
        # get game state after current agent moves
        successor = currentNode.state.generateSuccessor(agentIndex, action)
        heuristics = self.calculateHeuristicCosts(successor, successor.getAgentPosition(agentIndex), travelTo)

        # if current successor is to expensive, don't evaluate further
        if(heuristics[0] > maxCost):
          continue

        successors.append(Node(
          successor,
          currentNode,
          action,
          # general cost when evaluating total cost of path includes enemyCost
          currentNode.generalCost + 1 + heuristics[0],
          # heuristic cost also includes distance from destination
          currentNode.generalCost + 1 + heuristics[1]
          ))

      for s in successors:
        if(self.agentPositionMatchesDestination(s, travelTo)):
          pathAndCost = self.generatePathOfActions(s, gameState)
          return pathAndCost

        if(self.nodeShouldBeOpened(s, openNodes, closedNodes)):
          openNodes.append(s)
      closedNodes.append(currentNode)
    
      if( len(self.getFood(gameState).asList()) <= 2 ):
        print("There is only 2 or less food left. RETREAT")
        self.retreatToBase(gameState)

    return None

  def retreatToAnyBaseSpace(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    valueX, valueY = node.state.getAgentPosition(self.index)
    print("The position is" + str(self.start))
      
    posibleValidDestinations = []
    costOfPaths = []
    h = 1 
    for h in range(15):
      if( str(gameState.data.layout.walls[h][16]) == "False" ):
        if ( str(gameState.data.layout.walls[h][16-1]) == "False" && str(gameState.data.layout.walls[h][16+1]) == "False" ): 
          print("SpaceAvailable: (" + h + ",16)")
          posibleValidDestinations.apend(h)
          pathCostTuple = findPathAndCost(self, gameState, agentIndex, (h,16), maxCost) #Give this parameter --> (h,16) to the function as the final destination. And return only cost, not path
          cost = pathCostTuple[1]
          costOfPaths.append(cost)

    findPathAndCost(self, gameState, agentIndex, (costOfPaths.index(min(costOfPaths)),16), maxCost) #Give this parameter --> (costOfPaths.index(min(costOfPaths)),16) to the function as the final destination. This would be the true destination.
     
  def findLowestTotalCostNodeAndPop(self, openList):
    lowestNode = openList[0]
    lowIndex = 0

    i = 0
    for o in openList:
      if(o.totalCost <= lowestNode.totalCost):
        lowestNode = o
        lowIndex = i
      i += 1

    return (lowestNode, lowIndex)

  def agentPositionMatchesDestination(self, node, travelTo):
    # agentPosition = node.state.getAgentPosition(self.index)
    agentX, agentY = node.state.getAgentPosition(self.index)
    travelToX = travelTo[0]
    if(agentX == int(travelTo[0]) and int(agentY) == int(travelTo[1])):
      return True
    return False

  def nodeShouldBeOpened(self, node, openList, closedList):
    for o in openList:
      if(node.state.getAgentPosition(self.index) == o.state.getAgentPosition(self.index) and node.totalCost > o.totalCost):
        return False

    for c in closedList:
      if (node.state.getAgentPosition(self.index) == c.state.getAgentPosition(
              self.index) and node.totalCost > c.totalCost):
        return False

    return True

  def generateBasicPathOfActions(self, node):
    actionList = []
    currentNode = node
    while (currentNode.parent != None):
      actionList.insert(0, currentNode.action)
      currentNode = currentNode.parent

    return actionList

  def generatePathOfActions(self, node, originalGameState):
    totalCost = node.generalCost
    actionList = []
    currentNode = node
    while(currentNode.parent != None):
      actionList.insert(0, currentNode.action)
      currentNode = currentNode.parent

    if(self.pathIsDeadend(originalGameState, actionList)):
      totalCost += 100

    return (actionList, totalCost)

  def calculateBasicHeuristicCost(self, gameState, travelFrom, travelTo):
    return self.getMazeDistance(travelFrom, travelTo)

  def calculateHeuristicCosts(self, gameState, travelFrom, travelTo):
    distanceCost = 0
    enemyCost = 0
    closestEnemy = 999999

    # calculate distance to target
    distanceCost = self.getMazeDistance(travelFrom, travelTo)

    # calculate closest defender
    agents = self.getOpponents(gameState)
    for a in agents:
      state = gameState.getAgentState(a)
      if(state.scaredTimer == 0):
        enemyPosition = gameState.getAgentPosition(a)
        proximity = 999999

        if(enemyPosition != None):
          proximity = self.getMazeDistance(gameState.getAgentPosition(self.index), enemyPosition)

        if(proximity < closestEnemy):
          closestEnemy = proximity

    # calculate closest defender cost
    if(closestEnemy == 4):
      enemyCost = 3
    elif(closestEnemy == 3):
      enemyCost = 7
    elif(closestEnemy == 2):
      enemyCost = 15
    elif(closestEnemy == 1):
      enemyCost = 50

    return (enemyCost, distanceCost + enemyCost)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def getLowestCostFoodPath(self, gameState):
    food = self.getFood(gameState).asList()

    lowestCost = 99999
    lowestPath = None

    for f in food:
      path = self.findPathAndCost(gameState, self.index, f, lowestCost)
      if(path != None and path[1] < lowestCost):
        lowestPath = path[0]
        lowestCost = path[1]

    return lowestPath

  def notHoldingGameWinningFood(self, gameState):
    foodHolding = 0
    agents = self.getTeam(gameState)
    for a in agents:
      foodHolding += gameState.getAgentState(a).numCarrying
    return len(self.getFood(gameState).asList()) >= 2

  def pathIsDeadend(self, gameState, path):
    currentPosition = gameState.getAgentPosition(self.index)
    enemies = self.getOpponents(gameState)
    nearestEnemy = None
    closestDistance = 5

    for e in enemies:
      enemyPosition = gameState.getAgentPosition(e)

      # check if agent has access to enemyPosition
      if(enemyPosition == None):
        continue

      distanceFromEnemy = self.getMazeDistance(enemyPosition, currentPosition)
      if(distanceFromEnemy < closestDistance):
        nearestEnemy = e

    if(nearestEnemy == None):
      return False

    # follow given path while nearest enemy follows
    currentGameState = gameState
    for p in path:

      # if can be intercepted, treat this route as a deadend
      if(not p in currentGameState.getLegalActions(self.index)):
        return True

      currentGameState = currentGameState.generateSuccessor(self.index, p)

      enemyPath = self.findBasicPath(currentGameState, nearestEnemy, currentGameState.getAgentPosition(self.index))
      currentGameState = currentGameState.generateSuccessor(nearestEnemy, enemyPath[0])

    # if no solution for retreat return true
    return False #fixme

  def shouldRetreat(self, gameState):
     previousState = gameState

class CapsuleReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """

  def chooseAction(self, gameState):
    capsule = self.getCapsules(gameState)
    if(len(capsule) > 0):
      capsulePath = self.findPathAndCost(gameState, self.index, capsule[0], 999999)
      if(capsulePath != None):
        return capsulePath[0][0]
    if (len(self.getFood(gameState).asList()) > 2):
        return self.getLowestCostFoodPath(gameState)[0]

class AttackReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def chooseAction(self, gameState):
    if (len(self.getFood(gameState).asList()) > 0 and self.notHoldingGameWinningFood(gameState)):
      return self.getLowestCostFoodPath(gameState)[0]

class Node:
  state = None
  parent = None
  action = None
  generalCost = 0
  totalCost = 0

  def __init__(self, s, p, a, g, t):
    self.state = s
    self.parent = p
    self.action = a
    self.generalCost = g
    self.totalCost = t

