import pydicom
import numpy as np
import cv2 as cv
#===============================================================================================
def RegionGrowing(PixelArray,SeedArray,Outsider = (0,0)):
    #Input Dicom-PixelArray, Array der Seedpoints des Gitters und ihrer Werte in vorheriger Schicht, 
    #Punkt außerhalb der Leber (optional)

    #Parameters
    threshold = 10 #threshold region growing
    seedThreshold = 10 #threshold reject seed point
    outThreshold = PixelArray[Outsider[0]][Outsider[1]] + 10 
        #Abstand zum Outsider-Value, ab dem verworfen wird, Annahme: Outsider-Wert kleiner Leberwerte
    maxDist = 30 #max region growing iterations resultion in max distance from seed point


    activeLabels = np.zeros(SeedArray.shape[0])
    for i in range(0,SeedArray.shape[0]): #for all possible seeds
        if(abs(SeedArray[i][2] - PixelArray[SeedArray[i][0]][SeedArray[i][1]]) < seedThreshold):
            #if difference to earlier slice smaller threshold
            activeLabels[i] = RegionLabel(SeedArray[i],i+1)
            #create new label in array at position = i = labelname-1
    
    seg_labeled = np.zeros(PixelArray.shape)

    for i in range(0,maxDist):
        for j in range(0,activeLabels.shape[0]):
            if(activeLabels[j] == 0):
                continue
            while(len(activeLabels[j].borderline) > 0):
                #abarbeiten des Stacks der zu verarbeitenden
                tmp = activeLabels[j].borderline.pop(0) #entferne aus zu verarbeitenden
                activeLabels[j].innerOnes.append(tmp) #add zu verarbeitete
                surrPix = [ (tmp[0]-1,tmp[1]) , (tmp[0],tmp[1]-1) , (tmp[0]+1,tmp[1]) , (tmp[0],tmp[1]+1) ]
                #Pixel in 4er-Nachbarschaft
                for k in range(0,4):
                    tmpValue = seg_labeled[surrPix[k][0]][surrPix[k][1]]
                    if(tmpValue != 0):
                        #Pixel in Nachbarschaft schon gelabeled
                        if(tmpValue < tmp.label):
                            #wenn kleineres label -> in dieser Interation schon abgearbeitet, labels fusionieren
                            #wenn gleich oder größer, do nothing, da größeres das momentan arbeitende später
                            #in der gleichen Iteration noch verschlingen kann, 
                            #ohne Konsistenzprobleme zu verursachen
                            tmp.devourLabel(activeLabels[tmpValue - 1], seg_labeled)
                            activeLabels[tmpValue - 1] = 0 #verschlungenes label deaktivieren
                    elif(abs(PixelArray[surrPix[k][0]][surrPix[k][1]] - tmp[2]) < threshold):
                        #Pixel in Nachbarschaft noch nicht gelabeled und Schwellenwert nicht überschritten
                        #an dieser Stelle vielleicht noch andere Parameter, wie zB. Gradienten einfügen
                        #oder OutThreshold
                        activeLabels[j].newBorderline.append(surrPix[k][0],surrPix[k][1],PixelArray[surrPix[k][0]][surrPix[k][1]])
                        #hinzufügen für zu verarbeitende der nächsten Iteration (x,y,valueAtPosition)
                        seg_labeled[surrPix[k][0]][surrPix[k][1]] = j + 1
                        #Pixel als zum Label zugehörig markieren


    #nicht-zusammengelaufene Labels als separate Partitionen
    result = []
    for j in range(0,activeLabels.shape[0]):
        if(activeLabels[j] == 0):
            continue
        else:
            partition = seg_labeled
            cv.threshold(partition,j+1,255,cv.THRESH_TOZERO_INV)
            cv.threshold(partition,j,255,cv.THRESH_TOZERO)
            #thresholding to segment single label
            cv.threshold(partition,0,1,cv.THRESH_BINARY)
            #set positive to 1
            result.append(partition)

            
    #result: list of full-resolution pixel arrays of each seperate label
    #contains only zeros and ones in each pixel array
    return result
#===============================================================================================
class RegionLabel:
    borderline = [] #"seeds", die abgearbeitet werden
    innerOnes = [] #abgearbeitete
    label = 0
    newBorderline = [] #"seeds" für nächste Iteration

    def __init__(self,seed,number):
        #constructor: seed(x,y,value), number of label 
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
    def devourLabel(self, label, seg_labeled):
        #rewrite label numbers on segmentation to new label and fuse innerOnes and borderline
        #!kind'a brute force, think of better variante!
        while(len(label.innerOnes) > 0):
            tmp = label.innerOnes.pop(0)
            seg_labeled[tmp[0]][tmp[1]] = self.label
            self.innerOnes.append(tmp)
        while(len(label.borderline) > 0):
            tmp = label.borderline.pop(0)
            seg_labeled[tmp[0]][tmp[1]] = self.label
            self.newBorderline.append(tmp)
        return

