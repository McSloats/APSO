from particle import particle
from Utilities import fitnessScore,get_probs
import numpy as np
from copy import deepcopy
import random
from Dataset import loadSurrogate
import r2parser
import os
import x86handler as x86handler
from IPython import embed
random.seed(0)
np.random.seed(0)

class Swarm:

    def __init__(self,numOfParticles,randomMutation,maxQueries,x,C1,C2,e):
        self.numberOfParticles=numOfParticles
        self.targetModel=loadSurrogate()
        self.bestFitness=0
        #_,self.dLength,_ = self.targetModel.layers[1].output_shape
        self.dLength,_ = 2**20#self.targetModel.layers[1].output_shape
        self.numberOfQueries=0
        self.bestPosition=[255]*self.dLength
        self.randomMutation=randomMutation
        self.maxQueries=maxQueries
        self.pastFitness=[]
        self.inputX=x
        self.earlyTermination=e
        try:
            self.getOpCodesWithPatches(self.inputX)
        except:
            raise Exception("Analysis of opcodes failed...Skipping this sample")
        self.setCs(C1,C2)
        self.x86_handler=x86handler.X86Handler(32,False,False)
        
    def getOpCodesWithPatches(self,pos):
        with open('tmp','wb') as f:
            f.write(pos)
        r = r2parser.R2Parser('tmp', True)
        patches = r.iterate_fcn()
        #Spliting the results is a bit hacky but its the fastest way to implement this. We should look into regex for a more cleaner implementation.
        #Here I split according to spaces as that is how the R2 commands returns the results, and this works most of the time.
        #Very rarely do the opcodes appear in a different position which prompted the if in the loop
        #Example: 0x0042aff5      85ff           test edi, edi\n', (Good after splitting)
        #Example: 0x0042acf9      b920000000     mov ecx, 0x20               ; 32\n', (Bad after splitting, ; denotes a comment in assembly so safe to discard)
        self.replacements={}
        self.originalOpcode={}
        for add in patches:
            if ';' in r.r2.cmd('pd 1 @ %s'%add['offset']).split('   ')[-1].strip():
                continue
            originalOpcode=[r.r2.cmd('pd 1 @ %s'%add['offset']).split('     ')[-1].strip()]
            self.originalOpcode[add['offset']]=deepcopy(originalOpcode[0])
            subs=add['subs']
            originalOpcode.extend(subs)
            self.replacements[add['offset']]=originalOpcode
        r.close()
        os.remove('tmp')
        
    def patchTempFile(self,pos):
        with open('tmp','wb') as f:
            f.write(self.inputX)
        r = r2parser.R2Parser('tmp', False,write=True)
        replacements=[]
        for offset in pos:
            replacements.append({"offset":offset,"newbytes":self.x86_handler.assemble_code(pos[offset])})
        r.patch_binary(replacements)
        r.close()
        with open('tmp','rb') as f:
            newPos=f.read()
        os.remove('tmp')
        return newPos
        
    def setBestPosition(self,newPosition):
        self.bestPosition=deepcopy(newPosition)
            
    def setCs(self,C1,C2):       
        self.C1=C1
        self.C2=C2
        
    def setBestFitnessScore(self,newScore):
        self.bestFitness=newScore
        
    def calculateBaselineConfidence(self):
        pred=get_probs(self.targetModel,self.inputX)
        self.baselineConfidence=pred
        self.bestProba=pred
        return pred

    def resetParticlesSearchSpaces(self):
        for p in self.particles:
            p.searchSpace={}
            
    def generateSearchSpaces(self):
        self.searchSpaces={o:deepcopy(self.replacements[o]) for o in self.replacements}
    
    def returnRandomSearchSpaces(self,p):
        keys=random.sample(list(self.searchSpaces.keys()),self.changeRate if self.changeRate<=len(self.searchSpaces) else len(self.searchSpaces))
        iss=self.iterateKeys(p,keys)
        if len(self.searchSpaces)==0:
            self.flag=True
        if len(iss)==0:
            return []
        else:
            return iss

    def iterateKeys(self,p,keys):
        iss={}
        for key in keys:
            if len(iss)>=self.changeRate:
                break
            if len(self.searchSpaces[key])==0:
                self.searchSpaces.pop(key,None)
                continue
            p.searchSpace[key]=[]
            directionsToSample=self.searchSpaces[key]
            if not directionsToSample:
                continue
            lowLevel=random.choice(directionsToSample)
            iss[key]=lowLevel
            p.searchSpace[key].append(lowLevel)
            self.searchSpaces[key].remove(lowLevel)
            if len(self.searchSpaces[key])==0:
                self.searchSpaces.pop(key,None)
        return iss
        
    def initializeSwarmAndParticles(self):
        print('Initializing Swarm and Particles...\n')
        self.initializeSwarm()
        self.initializeParticles()
        
    def initializeSwarm(self):
        print("Generating search space...\n")
        self.generateSearchSpaces()
        self.changeRate=int(np.ceil(len(self.searchSpaces)/self.numberOfParticles))
        self.flag=False
        self.setBestPosition(self.originalOpcode)
        self.bestPosition={p:self.bestPosition[p] for p in self.bestPosition}
        self.setBestFitnessScore(0) 
        
    def initializeParticles(self):
        particleList=[]        
        for x in range(self.numberOfParticles):
            p=None
            p=particle(x)
            p.setW(self.C1,self.C2)
            p.currentVelocity={}
            replacementsVelocity={}
            for offset in self.originalOpcode:
                replacementsVelocity[offset]={}
                for replacement in self.replacements[offset]:
                    replacementsVelocity[offset][replacement]=np.random.uniform(0.0,1.0)
                p.currentVelocity[offset]=replacementsVelocity[offset]
            p.setBestFitnessScore(self.bestFitness)
            p.setBestPosition(self.bestPosition)
            self.randomizeParticle(p,self.originalOpcode)
            particleList.append(deepcopy(p))
        self.particles=deepcopy(particleList)
            
    def randomizeParticle(self,p,basePosition):
        temp=deepcopy(basePosition)
        iss=self.returnRandomSearchSpaces(p)
        if not iss:
            return False
        for x in iss:
            temp[x]=iss[x]
        p.setCurrentPosition(temp)
        self.check(p)
        p.pastPositions.append(p.currentPosition) 
        return True
        
    def searchOptimum(self,sampleNumber=None):
        if self.bestProba < 0.5:
            return self.bestPosition , self.bestFitness,0,self.numberOfQueries
        iteration=1
        while self.numberOfQueries<self.maxQueries:
            if self.bestProba < 0.5:
                return self.bestPosition , self.bestFitness,iteration,self.numberOfQueries
            for p in self.particles:
                if self.flag:
                    print("Re-generating search space...\n")
                    self.generateSearchSpaces()
                    self.resetParticlesSearchSpaces()
                    self.flag=False
                self.randomizeParticle(p,p.currentPosition)
                p.calculateNextPosition(self.bestPosition,self.numberOfQueries,self.C1,self.C2,self.maxQueries)   
                self.check(p)
            self.pastFitness.append(self.bestFitness)
            print('Iteration %s - Best Fitness %s - Number of Queries %s'%(str(iteration),str(self.bestFitness),str(self.numberOfQueries)))
            if self.earlyTermination>0 and len(self.pastFitness)>=self.earlyTermination and len(set(self.pastFitness))==1:
                return deepcopy(self.bestPosition) , self.bestFitness, iteration ,self.numberOfQueries
            if self.bestProba < 0.5:
                return deepcopy(self.bestPosition) , self.bestFitness, iteration ,self.numberOfQueries
            iteration=iteration+1
        print("Number of Queries: %s"%(self.numberOfQueries))
        return deepcopy(self.bestPosition) , self.bestFitness, iteration ,self.numberOfQueries       

    def check(self,p):
        newPos=self.patchTempFile(p.currentPosition)
        newFitness,newProba=fitnessScore(newPos,self.targetModel,self.baselineConfidence)
#        print("Particle ID %s, Fitness %s, Model confidence %s" %(p.particleID,newFitness,newProba))
        self.numberOfQueries=self.numberOfQueries+1
        p.setCurrentFitnessScore(newFitness)
        if newFitness > p.bestFitness:
            p.setBestFitnessScore(newFitness)
            p.setBestPosition(p.currentPosition)
        if p.bestFitness > self.bestFitness:
            self.setBestFitnessScore(p.bestFitness)
            self.setBestPosition(p.bestPosition)
            self.bestProba=deepcopy(newProba)
            
    def numberOfChanges(self):
        numberOfChanges=sum([1 for x in self.originalOpcode if not self.originalOpcode[x] == self.bestPosition[x]])
        return numberOfChanges
                
        
