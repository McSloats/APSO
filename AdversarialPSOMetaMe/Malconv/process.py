#!/usr/bin/python

import os
import random
import numpy as np
import requests

def bytez_to_numpy(bytez,maxlen):
    b = np.ones( (maxlen,), dtype=np.uint16 )*padding_char
    bytez = np.frombuffer( bytez[:maxlen], dtype=np.uint8 )
    b[:len(bytez)] = bytez
    return b

def getfile_service(names,maxlen=2**20):
    f = open(names,'rb').read()
    return bytez_to_numpy( f, maxlen )

def generator( hashes, labels, batch_size, shuffle=True ):
    X = []
    y = []
    fnames = list(zip(hashes, labels))
    while True:
        if shuffle:
            random.shuffle( fnames )
        for name,l in fnames:
            x = getfile_service(name)
            if x is None:
                continue
            X.append( x )
            y.append( l )
            if len(X) == batch_size:
                yield np.asarray(X,dtype=np.uint16), np.asarray(y)
                X = []
                y = []

def predict():
    test_generator = generator(hashes_test,labels_test,batch_size=1,shuffle=False)
    test_p = model.predict_generator( test_generator, steps=len(labels_test), verbose=1 )
