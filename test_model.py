import os
import magic
#import secml_malware
from secml.array import CArray
from secml_malware.models.malconv import MalConv
from secml_malware.models.c_classifier_end2end_malware import CClassifierEnd2EndMalware, End2EndModel

net = MalConv()
net = CClassifierEnd2EndMalware(net)
net.load_pretrained_model()

#Create output file
outputfile = open("Malconv_Test.csv","w")
outputfile.write("Name, Size, Confidence, Classification\n")

folder = "/extra_room/Win32_EXE/"
X = []
y = []
for i, f in enumerate(os.listdir(folder)):
    path = os.path.join(folder, f)
    with open(path, "rb") as file_handle:
        code = file_handle.read()
    x = End2EndModel.bytes_to_numpy(
        code, net.get_input_max_length(), 256, False
    )
    _, confidence = net.predict(CArray(x), True)

    #Skips printing confidence of files that do not do well
    #if confidence[0, 1].item() < 0.5:
    #    continue

    #Set classification
    classification = 1
    if confidence[0, 1].item() < 0.5:
        classification = 0

    print(f"> Added {f} with confidence {confidence[0,1].item()}")
    #X.append(x)
    conf = confidence[1][0].item()
    y.append([1 - conf, conf])
    
    outputfile.write(""+str(path.split("/")[3])+","+str(os.stat(path).st_size)+","+str(confidence[0,1].item())+","+str(classification)+"\n")
#    os.system("mv "+path+" "+folder_done+"")

outputfile.close()
