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


#==========================================================================================
#Main
satz = 1 #Datensatz
bildzahl = 80 #Anzahl Schichten im Datensatz
mitte = int(bildzahl / 2)

#Schema zum Einlesen eines Bildes; einsetzen für "bild"
#für Ground-Truth-Daten: "data" zu "seg"
#"medbv_data/P"+str(satz).zfill(2)+"/img"+str(bild).zfill(4)+".dcm"
m = pydicom.dcmread("medbv_data/P"+str(satz).zfill(2)+"/img"+str(mitte).zfill(4)+".dcm").pixel_array
u = pydicom.dcmread("medbv_data/P"+str(satz).zfill(2)+"/img"+str(mitte +1).zfill(4)+".dcm").pixel_array
l = pydicom.dcmread("medbv_data/P"+str(satz).zfill(2)+"/img"+str(mitte -1).zfill(4)+".dcm").pixel_array
#oeffnet die ersten 3 layer (aus der Mitte) des Datensatzes

uArr = uInter.user_interaction(m) #bestimmt Seeds fuer erste Schichten durch UserInteraction
outsider = uInter.user_interaction(m) 
#bestimmt einen Punkt ausserhalb des Zielbereiches durch UserInteraction
#only first one of returned valid/used
"""outValue = m[outsider[0][0]][outsider[0][1]]""" #Value in middle layer at position
"""doesn't yet work due to global defined variable in user_interaction"""
#TODO change user_interaction to different modes!
outValue = 0

paramsFirst = [20,50,100,outValue + 10,25,100]
#Parameter fuer's region growing auf der ersten Schicht: threshold, seedThreshold , Iterationen, 
#OutsiderThreshold, gradientThreshold, varianceThreshold
#eventuell abweichend von Parametern fuer spaetere Schichten
params = [20,50,100,outValue + 10]
#Parameter fuer's Region Growing der spaeteren Schichten:
#threshold, seedThreshold , Iterationen, OutsiderThreshold

first = fL.firstLayers(u,m,l,paramsFirst,uArr)
#Segmentierung der mittleren Schicht
downPath = nSeed.next_seeds(m,first,l)
upPath = nSeed.next_seeds(m,first,u)
#Generation der Seeds fuer naechste layer, 
#Abhaengigkeit vom naechsten Layer entfernen, sobald ordentlich implementiert

f = pydicom.dcmread("medbv_seg/P"+str(satz).zfill(2)+"/img"+str(mitte).zfill(4)+".dcm").pixel_array
result = groundT.GroundTruthAbgleich(first,f)
#oeffnet den Ground Truth des mittleren layer und nutzt ihn zur Initialisierung des Endergebnisses
#result[4] (dice-koeff. der Schicht) durch Additionen (s.u.) nicht mehr zu gebrauchen!
#am Ende Gesamtdice bestimmen!
#bei mehreren threads separate Ergebnisse erforderlich, die erst am Ende zusammengeführt werden!

#---------------------------------------------------------------------------------------------------
#Schichten ueber der Mitte
for i in range(mitte +1, bildzahl +1):
    #bildzahl +1, da 1-basierte Nummerierung in Datensatz
    pArr = pydicom.dcmread("medbv_data/P"+str(satz).zfill(2)+"/img"+str(i).zfill(4)+".dcm").pixel_array
    #laedt i-tes Bild und extrahiert pixelArray
    segParts = rG.RegionGrowing(pArr,upPath, params)
    
    tmpSeg = np.zeros(pArr.shape)
    for j in range (0,len(segParts)):
        tmpSeg += segParts[j]
    #fuegt die Partitionen der Segmentierung zusammen, um unverfaelscht die Qualitaet
    #der Segmentierung bestimmen = Vergleich mit Ground Truth machen zu koennen

    gArr = pydicom.dcmread("medbv_seg/P"+str(satz).zfill(2)+"/img"+str(i).zfill(4)+".dcm").pixel_array
    #laedt i-ten Ground Truth und extrahiert pixelArray
    result += groundT.GroundTruthAbgleich(segParts[j],gArr)
    #bestimmt Segmentierungsqualitaet der Schicht und addiert zum Gesamtergebnis

    #plt.imshow(tmpSeg)
    #plt.show()
    if(i != (bildzahl +1)):
        #Randbehandlung für letztes Bild, das kein naechstes hat
        imgNext = pydicom.dcmread("medbv_data/P"+str(satz).zfill(2)+"/img"+str(i+1).zfill(4)+".dcm").pixel_array
        upPath = nSeed.next_seeds(pArr,tmpSeg,imgNext)
        #laedt naechstes Bild und bestimmt den naechsten Satz Seeds
        #Abhaengigkeit von naechstem Bild und damit noetige Randbehandlung entfernen, sobald
        #next_seeds ordentlich implementiert

    #TODO so modifizieren, dass fuer jede Partition ab diesem Punkt eine seperates Growing erfolgt
    #vielleicht unnoetig / unnoetig umstaendlich?

#---------------------------------------------------------------------------------------------------
#Schichten unter der Mitte
for i in range(mitte -1, 0, -1):
    #range backwards, 0 not included (1-basierte Nummerierung in Datensatz)
    pArr = pydicom.dcmread("medbv_data/P"+str(satz).zfill(2)+"/img"+str(i).zfill(4)+".dcm").pixel_array
    #laedt i-tes Bild und extrahiert pixelArray
    segParts = rG.RegionGrowing(pArr,upPath, params)
    
    tmpSeg = np.zeros(pArr.shape)
    for j in range (0,len(segParts)):
        tmpSeg += segParts[j]
    #fuegt die Partitionen der Segmentierung zusammen, um unverfaelscht die Qualitaet
    #der Segmentierung bestimmen = Vergleich mit Ground Truth machen zu koennen

    gArr = pydicom.dcmread("medbv_seg/P"+str(satz).zfill(2)+"/img"+str(i).zfill(4)+".dcm").pixel_array
    #laedt i-ten Ground Truth und extrahiert pixelArray
    result += groundT.GroundTruthAbgleich(segParts[j],gArr)
    #bestimmt Segmentierungsqualitaet der Schicht und addiert zum Gesamtergebnis

    #plt.imshow(tmpSeg)
    #plt.show()
    if(i != (1)):
        #Randbehandlung für letztes Bild, das kein naechstes hat
        imgNext = pydicom.dcmread("medbv_data/P"+str(satz).zfill(2)+"/img"+str(i-1).zfill(4)+".dcm").pixel_array
        upPath = nSeed.next_seeds(pArr,tmpSeg,imgNext)
        #laedt naechstes Bild und bestimmt den naechsten Satz Seeds
        #Abhaengigkeit von naechstem Bild und damit noetige Randbehandlung entfernen, sobald
        #next_seeds ordentlich implementiert

    #TODO so modifizieren, dass fuer jede Partition ab diesem Punkt eine seperates Growing erfolgt
    #vielleicht unnoetig / unnoetig umstaendlich?

print(result)
print("Gesamt-3D-Dice-Koeffizient: " + ((2*result[0]) / (2*result[0] + result[1] + result[3])) )

    
