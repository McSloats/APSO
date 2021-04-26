import numpy as np
from copy import deepcopy
import random
import operator
random.seed(0)
np.random.seed(0)

class particle:
    W=None
    wEND=0
    wSTART=1.0
    
    def __init__(self,particleid=0):
        self.particleID=particleid
        self.bestFitness=0
        self.pastPositions=[]
        self.currentPosition=None
        self.nextPosition=None
        self.bestPosition=None
        self.currentVelocity=None
        self.currentFitness=0
        self.searchSpace={}
    
    def setNextPosition(self,newPosition):
        self.nextPosition=deepcopy(newPosition)
            
    def setCurrentPosition(self,newPosition):
        self.currentPosition=deepcopy(newPosition)
            
    def setBestPosition(self,newPosition):
        self.bestPosition=deepcopy(newPosition)
            
    def setBestFitnessScore(self,newScore):
        self.bestFitness=newScore
        
    def setCurrentFitnessScore(self,newScore):
        self.currentFitness=newScore
        
    def setW(self,C1,C2):
        self.wEND=0.2
        self.wSTART=0.8
        
    def printParticleInformation(self):
        print('Particle %s -- Best Fitness %s \n'%(str(self.particleID),str(self.bestFitness)))
            
    def standardVelocity(self,swarmBestPosition,T,C1,C2,maxIterations):
         particleBestPosition=deepcopy(self.bestPosition)
         particleCurrentPosition=deepcopy(self.currentPosition)
         swarmBestPosition=deepcopy(swarmBestPosition)
         self.calculateW(T,swarmBestPosition,maxIterations)
         v=deepcopy(self.currentVelocity)
         alternatives={}
         for x in particleCurrentPosition:
             alternatives[x]={}
             if particleBestPosition[x]==swarmBestPosition[x]:
                 alternatives[x][particleBestPosition[x]]=1
                 v[x][particleBestPosition[x]]=1
                 continue
             if (particleBestPosition[x] == swarmBestPosition[x]) and not (swarmBestPosition[x]==particleCurrentPosition[x]):
                 alternatives[x][particleBestPosition[x]]=1
                 v[x][particleBestPosition[x]]=1
                 continue
#             if particleBestPosition[x] in self.currentVelocity[x].keys():
#                 pastV=self.currentVelocity[x][particleBestPosition[x]]
#             else:
#                 pastV=0
             alternatives[x][particleBestPosition[x]]=(C2*np.random.uniform(0,1))#+(pastV*self.W)
#             if swarmBestPosition[x] in self.currentVelocity[x].keys():
#                 pastV=self.currentVelocity[x][swarmBestPosition[x]]
#             else:
#                 pastV=0
             alternatives[x][swarmBestPosition[x]]=(C1*np.random.uniform(0,1))#+(pastV*self.W)
             for k in alternatives[x].keys():
                 v[x][k]=np.exp(alternatives[x][k])/np.exp(sum([alternatives[x][s] for s in alternatives[x]]))
         self.currentVelocity=deepcopy(v)
         return v,alternatives
        
    def calculateNextPosition(self,swarmBestPosition,T,C1,C2,maxIterations):
        v,_=self.standardVelocity(swarmBestPosition,T,C1,C2,maxIterations)  
        nextPosition=deepcopy(self.currentPosition)
        for x in nextPosition:
            highestProb=max(v[x].items(),key=operator.itemgetter(1))
            if highestProb[1] > np.random.uniform(0.0,1.0):
                nextPosition[x]=highestProb[0]
        self.setCurrentPosition(nextPosition)
        return nextPosition
        
    def calculateW(self,T,swarmBestPosition,maxIterations):
        if np.all(np.equal(self.bestPosition,swarmBestPosition)):
            W=self.wEND
            self.W=W
            return self.W
        elif not np.all(np.equal(self.bestPosition , swarmBestPosition)):
            W=self.wEND+((self.wSTART-self.wEND)*(1-(T/maxIterations)))
            self.W=W
            return self.W
            
