import pydicom
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import matplotlib.colors
import Ground_Thruth_Abgleich_3D as groundT
import Region_Growing_v3 as rG
import user_interaction_05 as uInter
import next_seeds_02 as nSeed
import First_Layers as fL




m = pydicom.dcmread("medbv_data/P01/img0040.dcm").pixel_array
u = pydicom.dcmread("medbv_data/P01/img0041.dcm").pixel_array
l = pydicom.dcmread("medbv_data/P01/img0039.dcm").pixel_array
f = pydicom.dcmread("medbv_seg/P01/img0040.dcm").pixel_array
params = [20,50,100,10,25,100]

first = fL.firstLayers(u,m,l,params)

downPath = nSeed.next_seeds(m,first,l)
upPath = nSeed.next_seeds(m,first,u)

result = groundT.GroundTruthAbgleich(first,f)

for i in range(41,45):
    tmpImg = pydicom.dcmread("medbv_data/P01/img00" + str(i) + ".dcm")
    pArr =tmpImg.pixel_array
    segParts = rG.RegionGrowing(pArr,upPath, 20, 50, 100)
    gArr = pydicom.dcmread("medbv_seg/P01/img00" + str(i) + ".dcm").pixel_array
    tmpSeg = np.zeros(pArr.shape)
    for j in range (0,len(segParts)):

        result += groundT.GroundTruthAbgleich(segParts[j],gArr)
        tmpSeg += segParts[j]
    plt.imshow(tmpSeg)
    plt.show()
    if(i != 80):
        imgNext = pydicom.dcmread("medbv_data/P01/img00" + str(i+1) + ".dcm").pixel_array
        upPath = nSeed.next_seeds(pArr,tmpSeg,imgNext)

print(result)

    
