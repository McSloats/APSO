import argparse
import sys
import os


parser = argparse.ArgumentParser(description="Metamorphic engine guided with PSO that modifies assembly code while keeping the same functionality")
parser.add_argument("-i", "--input", help="Input directory",default=None)
parser.add_argument("-s" , "--sample" , help="Single input file" , default=None)
parser.add_argument("-o", "--output", help="Output directory",default=None)
parser.add_argument("-d", "--debug", action="store_true", help="print debug information",default=False)
parser.add_argument("-f", "--force", action="store_true", help="force instruction replacement when possible (decreases metamorphism entropy!)",default=False)
parser.add_argument("-p", "--numOfParticles" , help="Number of particles in the swarm",default=10 , type=int)
parser.add_argument("-q", "--maxQueries" , help="Maximum number of allowed queries",default=10000, type=int)
parser.add_argument("-r","--randomMutation",help="Probability of random mutation",default=0.1, type=float)
parser.add_argument("-e","--earlyTermination",help="Number of iterations of unchanged fitness before terminating search process. Set to -1 to disable",default=20, type=int)
args = parser.parse_args()

if (not args.input and not args.sample) or not args.output:
    parser.print_help()
    sys.exit(1)

from Dataset import readSamples,readSample,loadSurrogate
from Swarm import Swarm
from Utilities import get_probs

inputDir=args.input
outputDir=args.output
inputSample=args.sample
numOfParticles=args.numOfParticles
maxQueries=args.maxQueries
randomMutations=args.randomMutation
earlyTermination=args.earlyTermination
C1=1
C2=1

def logPSOOutput():
    failed = open("Failed_files.txt","w")
    if not inputDir==None:
        samples=readSamples(inp=inputDir)
    else:
        samples=[(inputSample,1)]
    with open('Malware_Samples_PSO_Results.csv','w') as f:
        f.write('Sample,Sample_Length,Number_of_Initial_Mappings,BaselineCofidence,BaselineFitness,Prediction_Before_PSO, Confidence_After_PSO,Fitness_After_PSO,Prediction_After_PSO,Iteration,Number_of_Required_Changes,Number_Of_Queries\n')
    i=0
    for samplePath,_ in samples:
        sample=readSample(samplePath)
        print(samplePath)
        length=(len(sample))
        try:
            swarm=Swarm(numOfParticles,randomMutations,maxQueries,sample,C1,C2,earlyTermination)
        except:
            print("\n############################################\n")
            print("Radare2 failed to analyze sample %s. Skipping...\n" %(samplePath))
            print("\n############################################\n")
            failed.write(str(samplePath)+" - Failed to analyze \n")
            continue
        try:
            numberOfPotentialMappings=len(swarm.replacements)
            baselineConfidence=swarm.calculateBaselineConfidence()
            if baselineConfidence < 0.5:
                continue
            print("Searching Optimum Advresarial Example... %s\n"%(i))
            swarm.initializeSwarmAndParticles()                
            print('Number of Potential Changes %s\n'%(numberOfPotentialMappings))
            print('Model Prediction Before PSO= %s\n'%(0 if baselineConfidence < 0.5 else 1))
            print('Baseline Confidence= %s\n'%(str(baselineConfidence)))
            _,_,iterations,numberOfQueries=swarm.searchOptimum()
            modelConfidence=baselineConfidence-swarm.bestFitness
            print('Model Confindence After PSO %s'%(modelConfidence))
            print('Best Fitness Score= %s'%(swarm.bestFitness))
            finalPosition=swarm.patchTempFile(swarm.bestPosition)
            predAfter=get_probs(swarm.targetModel,finalPosition)
            predAfter=0 if predAfter<0.5 else 1
            numberOfChanges=swarm.numberOfChanges()
            print('Model Prediction After PSO= %s'%(str(predAfter)))
            print('Required number of changes (L1)= %s'%(numberOfChanges))
            with open('Malware_Samples_PSO_Results.csv','a') as f:
                f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n'%(samplePath,str(length),str(numberOfPotentialMappings),str(baselineConfidence),str(1-baselineConfidence),str(0 if baselineConfidence < 0.5 else 1),str(modelConfidence),str(swarm.bestFitness),str(predAfter),str(iterations),str(numberOfChanges),str(numberOfQueries)))
            i=i+1
            os.system("mv "+str(samplePath)+" dataset-2k/done")
        except:
            failed.write(str(samplePath)+" - Number of Potential Changes "+str(numberOfPotentialMappings)+" \n")
            os.system("mv "+str(samplePath)+" dataset-2k/fail")
            
def testModel():
    if not inputDir==None:
        samples=readSamples(inp=inputDir)
    else:
        print("Please input directory path with malware in a folder named malware and benignware in a folder named bengineare\n")
        return
    model=loadSurrogate()
    res=[]
    i=1
    for x,y in samples:
        if i%100==0:
            print('Sample %s\n'%i)
        sample=readSample(x)
        proba=get_probs(model,sample)
        if (proba>0.5 and y==1) or (proba<0.5 and y==0):
            res.append(1)
        else:
            res.append(0)
        if i%500==0:
            print('Accuracy %s\n'%(sum(res)/len(res)))
        i=i+1
    print('Samples: %s  Accuracy: %s\n'%(len(res),sum(res)/len(res)))
    
    
if __name__ == "__main__":
    logPSOOutput()
