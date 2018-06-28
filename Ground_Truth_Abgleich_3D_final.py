#Ground-Truth-Werte:
# 0 -> Padding -> negative
# 1 -> außerhalb Körper -> negative
# 2 -> Körper -> negative
# 3 -> Leber -> positive
# 4 -> Lebertumor? -> positive
# 5 -> irgendwie daran/daneben; eventuell Risikoorgan -> negative TODO sicherstellen, dass negative

# !Warning!
# Dice-Koeffizient ist nur 2D, also für eine Slice -> anders nicht verwenden!
# 3D-Dice-Koeffizient in der Main nach Summation aller Slice-Ground-Truth-Abgleiche errechnen!

import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from scipy.spatial import distance
#===============================================================================================
def GroundTruthAbgleich(Segmentierung, GroundTruth):
    #Input:Segmentierung(2D-Array, Werte 0,1), GroundTruth(dicom.pixelarray, Werte s.o.)
    result = np.zeros(5)
    #Rückgabearray: [TruePositive, FalsePositive, TrueNegative, FalseNegative, Dice-Koeff.]
    #Dice-Koeff. = 2TP / (2TP + FP + FN)
    Segmentierung = np.array(Segmentierung.copy())
    for i in range(0, Segmentierung.shape[0]):
        for j in range(0, Segmentierung.shape[1]):
            if (Segmentierung[i][j] == 1 and GroundTruth[i][j] in [3,4]):
                result[0] = result[0] +1
            elif (Segmentierung[i][j] == 1 and GroundTruth[i][j] in [0,1,2,5]):
                result[1] = result[1] +1
            elif (Segmentierung[i][j] == 0 and GroundTruth[i][j] in [0,1,2,5]):
                result[2] = result[2] +1
            else:
                result[3] = result[3] +1
    #Vergleich; 4 Kombinationen
    result[4] = (2*result[0]) / (2*result[0] + result[1] + result[3])
    #Berechnen Dice-Koeff.
    #print(result) #prints result for single slice, different than prints in main
    #TODO find situation, that creates warnings (doesn't affect results)
    return result
#===============================================================================================
def Hausdorff(Segmentierung, GroundTruth):
    #binarisiere GroundTruth TODO get it to work with OpenCV-Thresholding on PixelArrays
    GroundTruthB = GroundTruth.copy()
    for i in range(0, GroundTruth.shape[0]):
        for j in range(0, GroundTruth.shape[1]):
            if  (GroundTruth[i][j] == 3): #Leber -> to 1
                GroundTruthB[i][j] -= 2
            elif(GroundTruth[i][j] == 4):
                GroundTruthB[i][j] -= 3
            elif(GroundTruth[i][j] == 1): #nicht-Leber -> to zero
                GroundTruthB[i][j] -= 1
            elif(GroundTruth[i][j] == 2):
                GroundTruthB[i][j] -= 2
            elif(GroundTruth[i][j] == 5):
                GroundTruthB[i][j] -= 5

    segContours = getContours(Segmentierung)
    gtContours = getContours(GroundTruthB)

    #leere Mengen -> Hausdorff-Distanz undefiniert:
    #Handling: 
    #kein GroundTruth -> aus Wertung
    #keine Segmentierung -> Vorkommen zaehlen
    if(len(gtContours) == 0):
        return -2
    
    if(len(segContours) == 0):
        return -1

    diffBild = GroundTruthB - Segmentierung
    maxDist = 0
    for i in range(0, GroundTruth.shape[0]):
        for j in range(0, GroundTruth.shape[1]):
            #check for every pixel different in both images
            if(diffBild[i][j] == 1): #seg pixel not in gt
                tmp = minDistance(i,j,segContours)
                if(tmp > maxDist):
                    maxDist = tmp #keep only largest
            if(diffBild[i][j] == -1): #gt pixel not in seg
                tmp = minDistance(i,j,gtContours)
                if(tmp > maxDist):
                    maxDist = tmp
    return maxDist            
#===============================================================================================           
def getContours(array):
    #converts array to image and uses openCV-functions to get contours
    plt.imsave("TmpImg",array,0,1)
    img = cv.imread("TmpImg.png", 0)
    _, img = cv.threshold(img,31,255,cv.THRESH_TOZERO) 
    #weil durch speichern-laden 0 -> 30; 1 -> 215
    _,ret,_ = cv.findContours(img, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)
    #return: Liste aller Konturen, alle Pixel der Konturen
    return ret
#===============================================================================================
def minDistance(x,y,contours):
    #calculates minimal distance of specified point to any on one of the contours
    minDist = 999999 #definitivly larger than any calculated
    for i in range(0, len(contours)):
        for j in range(0, len(contours[i])):
            tmp = distance.euclidean( (y,x) , contours[i][j] )
            if(tmp < minDist):
                minDist = tmp
    return minDist
#===============================================================================================



