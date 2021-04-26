# APSO
This is an adversarial example attack against the Malconv malware detection model. Malware is changed using a modified version of the metamorphic engine that makes instruction replacements found publicly at *https://github.com/a0rtega/metame*. Particle Swarm Optimization is used to make intelligent changes to the malware executable instructions based on the output confidence of the model.

## Installation Instructions
#### 1. Pre-requisite Information
Operating System - Ubuntu 20.04.2 LTS Desktop
- Updated and upgraded

Programming Language - Python3.8.5

#### 2. Pre-requisite Installation Instructions
Download the needed packages.
```
sudo apt-get install python3-pip cmake radare2 git
```

#### 3. Download Git files
```
git clone https://github.com/McSloats/APSO.git
cd APSO
```

#### 4. PIP Installs
The *requirements.txt* are for PSO and *secml_malware/requirements.txt* is for the Secml Malware library.
```
pip3 install -U setuptools
pip3 install keystone-engine
pip3 install torch
pip3 install torchvision
pip3 install -r requirements
pip3 install -r secml_malware/requirements.txt
```

#### 5. Ember Installation
```
pip3 install git+https://github.com/elastic/ember.git
```

#### 6. Dataset Setup
```
mkdir dataset
mkdir dataset/failed
mkdir dataset/untested
mkdir dataset/tested
```
Add the dataset to the *untested* directory.

## Run the Attack
The "-i" is the input directory where the malware samples should exist. In the case of the *Dataset Setup* steps, they should be located in "-i dataset/untested". The "-o out" is not functional, but needed to run for PSO.
```
python3 AdversarialPSO.py -i dataset/untested/ -o out
```
