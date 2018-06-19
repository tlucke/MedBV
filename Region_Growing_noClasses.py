import pydicom
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import matplotlib.colors
import Ground_Thruth_Abgleich_3D as groundT
import scipy.signal as sci

#known issues:
#laeuft an den Rändern auf andere Bildseite über;
# - sollte im Normalbetrieb allerdings kein Problem darstellen, da Zielbereich recht zentral liegt

#===============================================================================================
def RegionGrowing(PixelArray,SeedArray, parameters):
    #Input Dicom-PixelArray, Array der Seedpoints des Gitters und ihrer Werte in vorheriger Schicht, 
    #Punkt außerhalb der Leber (optional)

    #Parameters
    threshold = parameters[0] #threshold region growing
    seedThreshold = parameters[1] #threshold reject seed point
    maxDist = parameters[2] #max region growing iterations resultion in max distance from seed point
    outThreshold = parameters[3] 
        #Abstand zum Outsider-Value, ab dem verworfen wird, Annahme: Outsider-Wert kleiner Leberwerte

    print(len(SeedArray))
    
    validSeedFlag = 0 #flag indicating if there's at least one valid seed
    active = []
    newActive = []
    seg = np.zeros(PixelArray.shape)

    for i in range(0,len(SeedArray)): #for all possible seeds
        if(abs(SeedArray[i][2] - PixelArray[SeedArray[i][0]][SeedArray[i][1]]) < seedThreshold):
            #if difference to earlier slice smaller threshold
            active.append((SeedArray[i][0],SeedArray[i][1],PixelArray[SeedArray[i][0]][SeedArray[i][1]]))
            #append seed to active borderline
            validSeedFlag = 1
            seg[SeedArray[i][0]][SeedArray[i][1]] = 1
            #mark valid seed point in segmentation

    result = []
    
    if(validSeedFlag == 0): #if there are no valid seeds return empty segmentation
        print("no valid seeds")
        result.append(seg)
        return (result)

    #Vorarbeitung:
    #PixelArray = sci.medfilt(PixelArray,5)
    ret, PixelArray = cv.threshold(PixelArray,outThreshold,255,cv.THRESH_TOZERO)

    for i in range(0,maxDist):        
        while(len(active) > 0):
            #abarbeiten des Stacks der zu verarbeitenden
            tmp = active.pop(0) #entferne aus zu verarbeitenden
            surrPix = [ (tmp[0]-1,tmp[1]) , (tmp[0],tmp[1]-1) , (tmp[0]+1,tmp[1]) , (tmp[0],tmp[1]+1) ]
            #Pixel in 4er-Nachbarschaft
            for k in range(0,4):
                if(surrPix[k][0] < 0 or surrPix[k][0] >= PixelArray.shape[0]
                or surrPix[k][1] < 0 or surrPix[k][1] >= PixelArray.shape[1]):
                    continue
                if( (int(seg[surrPix[k][0]][surrPix[k][1]])) != 0):
                    continue
                if(abs(PixelArray[surrPix[k][0]][surrPix[k][1]] - tmp[2]) < threshold):
                    #Pixel in Nachbarschaft Schwellenwert nicht überschritten
                    #an dieser Stelle vielleicht noch andere Parameter, wie zB. Gradienten einfügen
                    newActive.append((surrPix[k][0],surrPix[k][1],PixelArray[surrPix[k][0]][surrPix[k][1]]))
                    #hinzufügen für zu verarbeitende der nächsten Iteration (x,y,valueAtPosition)
                    seg[surrPix[k][0]][surrPix[k][1]] = 1
                    #Pixel als zur Segmentierung zugehörig markieren
        #plt.imshow(seg)
        #plt.show()
        active = newActive.copy()

    
    result.append(seg)       
    #result: full-resolution pixel array
    #contains only zeros and ones
    return result
#===============================================================================================
