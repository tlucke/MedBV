import pydicom
import numpy as np
import cv2 as cv
#===============================================================================================
def RegionGrowing(PixelArray,SeedArray, parameters):
    #Input Dicom-PixelArray, Array der Seedpoints des Gitters und ihrer Werte in vorheriger Schicht, 
    #Parameter-Array (s.u.)

    #Parameters
    threshold = parameters[0] #threshold region growing
    seedThreshold = parameters[1] #threshold reject seed point
    maxDist = parameters[2] #max region growing iterations resultion in max distance from seed point
    outThreshold = parameters[3] 
    #Abstand zum Outsider-Value, ab dem verworfen wird, Annahme: Outsider-Wert kleiner Leberwerte

    
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
            activeLabels.append(0) #"devalued" label for indexing purposes, not particulary necessary
    
    #Vorarbeitung/Schwellenwertsegmentierung:
    _, PixelArray = cv.threshold(PixelArray,outThreshold,255,cv.THRESH_TOZERO)

    result = []
    
    if(validSeedFlag == 0): #if there are no valid seeds return empty segmentation
        #print("no valid seeds") #not exactly an error, since there are empty slices
        result.append(seg_labeled)
        return result #can't return invalid value to indicate and terminate loop in main early,
        #since tests need to check later slices, if emptiness is correct

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
                            #wenn gleich oder groesser, do nothing, da groesseres das momentan arbeitende spaeter
                            #in der gleichen Iteration noch verschlingen kann, ohne Konsistenzprobleme zu verursachen
                            activeLabels[j].devourLabel(activeLabels[tmpValue - 1], seg_labeled)
                            activeLabels[tmpValue - 1] = 0 #verschlungenes label deaktivieren
                    elif(abs(PixelArray[surrPix[k][0]][surrPix[k][1]] - tmp[2]) < threshold):
                        #Pixel in Nachbarschaft noch nicht gelabeled und Schwellenwert nicht ueberschritten
                        #an dieser Stelle vielleicht noch andere Parameter, wie zB. Gradienten einfügen
                        activeLabels[j].newBorderline.append((surrPix[k][0],surrPix[k][1],PixelArray[surrPix[k][0]][surrPix[k][1]]))
                        #hinzufuegen für zu verarbeitende der naechsten Iteration (x,y,valueAtPosition)
                        seg_labeled[surrPix[k][0]][surrPix[k][1]] = j + 1
                        #Pixel als zum Label zugehoerig markieren
            activeLabels[j].refreshBorder()

    #zu einzelner "Partition" zusammenfuegen; getrenntes Konzept/separate Partitionen verworfen
    tmp_result = np.zeros(PixelArray.shape)
    for j in range(0,len(activeLabels)):
        if(activeLabels[j] == 0):   #devoured labels
            continue
        else:
            partition = seg_labeled #TODO check if really hard-copy - but code works the way it is
            _, partition = cv.threshold(partition,j+1,255,cv.THRESH_TOZERO_INV)
            _, partition = cv.threshold(partition,j,255,cv.THRESH_TOZERO)
            #thresholding to segment single label
            partition = np.divide(partition,(j+1)) #set positive to 1
            tmp_result += partition #add to fusion
            
    result.append(tmp_result)        
    #result: full-resolution pixel array of fused labels; contains only zeros and ones
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
        partition = seg_labeled #TODO check if really hard-copy - but code works the way it is
        _, partition = cv.threshold(partition,other.label,255,cv.THRESH_TOZERO_INV)
        _, partition = cv.threshold(partition,other.label-1,255,cv.THRESH_TOZERO)
        #thresholding to segment single label
        partition = np.divide(partition,(other.label))
        partition *= (self.label - other.label)
        #set value to difference in label numbers
        seg_labeled += partition
        #add difference for specified pixels to label picture

        self.newBorderline = self.newBorderline + other.borderline
        #no need to pop from stack if there's no need to change pixels - concatenate stacks
        return
#===============================================================================================
