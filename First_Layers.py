import pydicom
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import matplotlib.colors
import Ground_Thruth_Abgleich_3D as groundT
import Region_Growing_v3 as rG
import user_interaction_05 as uInter

#===============================================================================================
def firstLayers(upperLayer, middleLayer, lowerLayer, parameters, uArr):
    #Input: PixelArrays of the middle +/- 1 Layers; Array with several parameters
    
    #Parameters for Region Growing
    threshold = parameters[0]     #threshold region growing
    seedThreshold = parameters[1] #threshold seed reject
    maxDist = parameters[2]        #max iterations of region growing

    #Parameters from User Interaction; TODO: change to function call on completion
    #hardcode results of user interaction here for (parameter) testing
    """uArr = uInter.user_interaction(middleLayer)
    moved to main, uArr is now argument of the function"""
    SeedArray = []
    for i in range(0, len(uArr)):
        SeedArray.append((uArr[i][0],uArr[i][1],middleLayer[uArr[i][0]][uArr[i][1]]))
    SeedArray = np.array(SeedArray)
    #fuegt den Positionen aus der UserInteraction die Werte hinzu
    """Outsider = (0,0,0)
    outsiderThreshold = Outsider[2] + parameters[3]
    now modified in main"""
    outsiderThreshold = parameters[3]

    #Parameters for further processing
    gradientThreshold = parameters[4] #threshold for squared gradient
    varianceThreshold = parameters[5]

    #Idee: thresholds durch Streuung und Wertebereich des SeedArrays/Outsiders anpassen

    #Inital Region Growing on Layers
    params = [threshold, seedThreshold, maxDist, outsiderThreshold]
    segUpper = rG.RegionGrowing(upperLayer,SeedArray,params)
    segMiddle = rG.RegionGrowing(middleLayer,SeedArray,params)
    segLower = rG.RegionGrowing(lowerLayer,SeedArray,params)
    #no splits expected -> fuse labels
    #TODO Fehlerhafte Annahme! Aendern, wenn Splits in der Main behandelt!
    segUppertmp = segUpper[0]
    for i in range(1,len(segUpper)):
        segUppertmp = segUppertmp + segUpper[i]
    segUpper = segUppertmp
    segMiddletmp = segMiddle[0]
    for i in range(1,len(segMiddle)):
        segMiddletmp = segMiddletmp + segMiddle[i]
    segMiddle = segMiddletmp
    segLowertmp = segLower[0]
    for i in range(1,len(segLower)):
        segLowertmp = segLowertmp + segLower[i]
    segLower = segLowertmp


    #calculate gradients of layers
    sobelXUpper = cv.Sobel(upperLayer,cv.CV_64F,1,0,3)
    sobelYUpper = cv.Sobel(upperLayer,cv.CV_64F,0,1,3)
    absGradUpper = pow(sobelXUpper,2) + pow(sobelYUpper,2)
    sobelXMiddle = cv.Sobel(middleLayer,cv.CV_64F,1,0,3)
    sobelYMiddle = cv.Sobel(middleLayer,cv.CV_64F,0,1,3)
    absGradMiddle = pow(sobelXMiddle,2) + pow(sobelYMiddle,2)
    sobelXLower = cv.Sobel(lowerLayer,cv.CV_64F,1,0,3)
    sobelYLower = cv.Sobel(lowerLayer,cv.CV_64F,0,1,3)
    absGradLower = pow(sobelXLower,2) + pow(sobelYLower,2)

    #if pixel only in one segmantation, check some constraints
    #if not passed -> delete
    segAll = segUpper + segMiddle + segLower
    for i in range(0,middleLayer.shape[0]):
        for j in range(0,middleLayer.shape[1]):
            if(segAll[i][j] == 1): 
                maxGrad = max(absGradUpper[i][j],absGradMiddle[i][j], absGradLower[i][j])
                #""" (deleting # here and further down disables costraint checks)
                if(maxGrad > gradientThreshold):
                    #local gradient too strong so likely on edge
                    segAll[i][j] = 0
                    continue
                if(min(upperLayer[i][j],middleLayer[i][j],lowerLayer[i][j]) < outsiderThreshold):
                    #value to close to assumed outside values
                    segAll[i][j] = 0
                    continue
                #TODO:add more constraints, like local variance threshold
                #"""
            elif(segAll[i][j] > 1):
                segAll[i][j] = 1
    

    #morphological closing
    #kernelY = cv.getStructuringElement(cv.MORPH_RECT(1,2)) #producing errors
    #kernelX = cv.getStructuringElement(cv.MORPH_RECT(2,1))
    kernelY = np.array([[1],[1]])
    kernelX = np.array([[1,1]])
    #TODO test different kernels, don't forget to change "shift" parameter
    closingY = cv.morphologyEx(segAll, cv.MORPH_CLOSE, kernelY)
    closingX = cv.morphologyEx(closingY, cv.MORPH_CLOSE, kernelX)
    result = closingX
    shift = 1 #rows/columns for backshift
    for i in range(shift,middleLayer.shape[0]):
        for j in range(shift,middleLayer.shape[1]):
            result[i-shift][j-shift] = result[i][j]
    #shifts back up "shift" row/column after down/right shift due to closing
    #"deletes" top row/column, doubles bottom row/column
    #no errors expected, since region is irrelevant
    return result

#===============================================================================================
#Testmain
"""
layer1 = pydicom.dcmread("medbv_data/P01/img0040.dcm").pixel_array
layer2 = pydicom.dcmread("medbv_data/P01/img0039.dcm").pixel_array
layer3 = pydicom.dcmread("medbv_data/P01/img0041.dcm").pixel_array

params = [20,20,100,10,25,100]

seg1 = firstLayers(layer1,layer2,layer3,params)
gt = pydicom.dcmread("medbv_seg/P01/img0040.dcm").pixel_array


plt.imshow(seg1)
plt.show()
plt.imshow(gt)
plt.show()
result = groundT.GroundTruthAbgleich(seg1, gt)
print(result)
"""