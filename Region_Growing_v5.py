import pydicom
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import matplotlib.colors
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

    #print(len(SeedArray))
    
    validSeedFlag = 0 #flag indicating if there's at least one valid seed
    activeLabels = []
    seg_labeled = np.zeros(PixelArray.shape)

    for i in range(0,len(SeedArray)): #for all possible seeds
        if(abs(SeedArray[i][2] - PixelArray[SeedArray[i][0]][SeedArray[i][1]]) < seedThreshold):
            #if difference to earlier slice smaller threshold
            activeLabels.append(RegionLabel(SeedArray[i],i+1))
            #create new label in array at position = i = labelname-1
            validSeedFlag = 1
            seg_labeled[SeedArray[i][0]][SeedArray[i][1]] += i+1
            #mark valid seed point in segmentation
        else:
            #print(SeedArray[i][2] , PixelArray[SeedArray[i][0]][SeedArray[i][1]])
            activeLabels.append(0) 
    
    #Vorarbeitung:
    #PixelArray = sci.medfilt(PixelArray,5)
    ret, PixelArray = cv.threshold(PixelArray,outThreshold,255,cv.THRESH_TOZERO)

    result = []
    
    if(validSeedFlag == 0): #if there are no valid seeds return empty segmentation
        #print("no valid seeds")
        result.append(seg_labeled)
        return (result)

    for i in range(0,maxDist):
        for j in range(0,len(activeLabels)):
            if(activeLabels[j] == 0):
                continue
            while(len(activeLabels[j].borderline) > 0):
                #abarbeiten des Stacks der zu verarbeitenden
                tmp = activeLabels[j].borderline.pop(0) #entferne aus zu verarbeitenden
                activeLabels[j].innerOnes.append(tmp) #add zu verarbeitete
                surrPix = [ (tmp[0]-1,tmp[1]) , (tmp[0],tmp[1]-1) , (tmp[0]+1,tmp[1]) , (tmp[0],tmp[1]+1) ]
                #Pixel in 4er-Nachbarschaft
                for k in range(0,4):
                    if(surrPix[k][0] < 0 or surrPix[k][0] >= PixelArray.shape[0]
                    or surrPix[k][1] < 0 or surrPix[k][1] >= PixelArray.shape[1]):
                        continue
                    tmpValue = int(seg_labeled[surrPix[k][0]][surrPix[k][1]])
                    if(tmpValue != 0):
                        #Pixel in Nachbarschaft schon gelabeled
                        if(tmpValue < (j+1) ): #j+1 == Nummer des aktiven Labels
                            #wenn kleineres label -> in dieser Interation schon abgearbeitet, labels fusionieren
                            #wenn gleich oder größer, do nothing, da größeres das momentan arbeitende später
                            #in der gleichen Iteration noch verschlingen kann, 
                            #ohne Konsistenzprobleme zu verursachen
                            activeLabels[j].devourLabel(activeLabels[tmpValue - 1], seg_labeled)
                            activeLabels[tmpValue - 1] = 0 #verschlungenes label deaktivieren
                    elif(abs(PixelArray[surrPix[k][0]][surrPix[k][1]] - tmp[2]) < threshold):
                        #Pixel in Nachbarschaft noch nicht gelabeled und Schwellenwert nicht überschritten
                        #an dieser Stelle vielleicht noch andere Parameter, wie zB. Gradienten einfügen
                        #oder OutThreshold
                        activeLabels[j].newBorderline.append((surrPix[k][0],surrPix[k][1],PixelArray[surrPix[k][0]][surrPix[k][1]]))
                        #hinzufügen für zu verarbeitende der nächsten Iteration (x,y,valueAtPosition)
                        seg_labeled[surrPix[k][0]][surrPix[k][1]] = j + 1
                        #Pixel als zum Label zugehörig markieren
            activeLabels[j].refreshBorder()

    #nicht-zusammengelaufene Labels als separate Partitionen
    #TODO zu einzelner Partition aendern; getrenntes Konzept verworfen
    tmp_result = np.zeros(PixelArray.shape)
    for j in range(0,len(activeLabels)):
        if(activeLabels[j] == 0):
            continue
        else:
            partition = seg_labeled
            ret, partition = cv.threshold(partition,j+1,255,cv.THRESH_TOZERO_INV)
            ret, partition = cv.threshold(partition,j,255,cv.THRESH_TOZERO)
            #thresholding to segment single label
            #cv.threshold(partition,0,1,cv.THRESH_BINARY) #!!!!line not working as intended!!!!
            partition = np.divide(partition,(j+1))
            #set positive to 1
            tmp_result += partition
            
    result.append(tmp_result)
            
    #result: list of full-resolution pixel arrays of each seperate label
    #contains only zeros and ones in each pixel array
    return result
#===============================================================================================
class RegionLabel:
    

    def __init__(self,seed,number):
        #constructor: seed(x,y,value), number of label
        self.borderline = [] #"seeds", die abgearbeitet werden
        self.innerOnes = [] #abgearbeitete
        self.label = 0
        self.newBorderline = [] #"seeds" für nächste Iteration 
        self.borderline.append(seed)
        self.label = number
        return
    #--------------------------------------------------------------------------------------------
    def refreshBorder(self):
        #at the end of iteration
        self.borderline = self.newBorderline
        self.newBorderline = []
        return
    #--------------------------------------------------------------------------------------------
    def devourLabel(self, other, seg_labeled):
        #rewrite label numbers on segmentation to new label and fuse innerOnes and borderline
        #!kind'a brute force, think of better variante!
        #switch to OpenCV thresholding?
        """
        while(len(other.innerOnes) > 0):
            tmp = other.innerOnes.pop(0)
            seg_labeled[tmp[0]][tmp[1]] = self.label
            self.innerOnes.append(tmp)
        """
        partition = seg_labeled
        ret, partition = cv.threshold(partition,other.label,255,cv.THRESH_TOZERO_INV)
        ret, partition = cv.threshold(partition,other.label-1,255,cv.THRESH_TOZERO)
        #thresholding to segment single label
        partition = np.divide(partition,(other.label))
        partition *= (self.label - other.label)
        #set value to difference in label numbers
        seg_labeled += partition
        #add difference for specified pixels to label picture

        """
        while(len(other.borderline) > 0):
            tmp = other.borderline.pop(0)
            #seg_labeled[tmp[0]][tmp[1]] = self.label
            #already caught in partition
            self.newBorderline.append(tmp)
        """
        self.newBorderline = self.newBorderline + other.borderline
        #no need to pop from stack if there's no need to change pixels
        return
#===============================================================================================
#Test-Main
"""
dt = pydicom.dcmread("medbv_data/P01/img0040.dcm")
gt = pydicom.dcmread("medbv_seg/P01/img0040.dcm")
dtarr = dt.pixel_array
gtarr = gt.pixel_array

print(dtarr[145,65])
print(dtarr[155,65])
print(dtarr[145,60])
print(dtarr[145,70])

seeds = np.array([[150,65,378],[145,65,363],[155,65,388],[150,60,397],[150,70,393]])
#seeds = np.array([[0,0,0]])
seg1 = RegionGrowing(dtarr,seeds)

for i in range(0, len(seg1)):
    plt.imshow(seg1[i])
    plt.show()
    plt.imshow(gtarr)
    plt.show()
    result = groundT.GroundTruthAbgleich(seg1[i], gtarr)
    print(result)
"""
