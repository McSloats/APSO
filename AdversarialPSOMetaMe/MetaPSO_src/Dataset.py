import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
#from keras import metrics
#from keras.models import load_model
#from keras.optimizers import SGD
from secml.array import CArray
from secml_malware.models.malconv import MalConv
from secml_malware.models.c_classifier_end2end_malware import CClassifierEnd2EndMalware, End2EndModel
from os import listdir
from os.path import isfile, join,isdir
    
def loadSurrogate():
    #model = load_model('malconv.h5')
    #model.compile( loss='binary_crossentropy', optimizer=SGD(lr=0.01,momentum=0.9,nesterov=True,decay=1e-3), metrics=[metrics.binary_accuracy] )
    #return model
    net = MalConv()
    net = CClassifierEnd2EndMalware(net)
    net.load_pretrained_model()
    return net

def readSample(path):
    #with open(filePath,'rb') as f:
    #    data=f.read()
    #return data
    with open(path, "rb") as file_handle:
        code = file_handle.read()
    return code

def readSamples(inp=os.path.join('.','Test_Samples')):
    onlyfiles = [(os.path.join(inp,f),1) if 'malware' in inp else (os.path.join(inp,f),0) for f in listdir(inp) if isfile(join(inp, f))]
    directories=[os.path.join(inp,f) for f in listdir(inp) if isdir(join(inp, f))]
    for d in directories:
        onlyfiles.extend(readSamples(d))
    return onlyfiles
    
