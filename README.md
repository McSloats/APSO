# APSO modified version
This repository is a modified version to work with the secml_malware model.

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

#### 6. Setup Dataset
```
mkdir dataset
mkdir dataset/failed
mkdir dataset/untested
mkdir dataset/tested
```
Add the dataset to the *untested* directory.

## Run the Attack
The out file is a tmp and not needed. The "-o out" is not functional, but needed to run for PSO.
```
python3 AdversarialPSO.py -i dataset/untested/ -o out
```
=======
# APSO
Adversarial attack with Particle Swarm Optimization.

#### This version may not be up to date...

#### Use 'git checkout APSOMod' to get to the working version.
