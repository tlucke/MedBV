import pydicom
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import matplotlib.colors
import Ground_Truth_Abgleich_3D as groundT
import Region_Growing_v5 as rG
import user_interaction_08 as uInter
import next_seeds_03 as nSeed
import First_Layers as fL


    #==========================================================================================
def allSets(number,numberSlices):
    #Main
    satz = number #Datensatz
    bildzahl = numberSlices #Anzahl Schichten im Datensatz
    mitte = int(bildzahl / 2)

    #Schema zum Einlesen eines Bildes; einsetzen für "bild"
    #für Ground-Truth-Daten: "data" zu "seg"
    #"medbv_data/P"+str(satz).zfill(2)+"/img"+str(bild).zfill(4)+".dcm"
    m = pydicom.dcmread("medbv_data/P"+str(satz).zfill(2)+"/img"+str(mitte).zfill(4)+".dcm").pixel_array
    u = pydicom.dcmread("medbv_data/P"+str(satz).zfill(2)+"/img"+str(mitte +1).zfill(4)+".dcm").pixel_array
    l = pydicom.dcmread("medbv_data/P"+str(satz).zfill(2)+"/img"+str(mitte -1).zfill(4)+".dcm").pixel_array
    #oeffnet die ersten 3 layer (aus der Mitte) des Datensatzes

    uArr, outsider = uInter.user_interaction(m) #bestimmt Seeds fuer erste Schichten durch UserInteraction
    #uArr = [[150,108],[117,50],[169,48],[189,80],[243,133]]
    #outsider = [[217,90]]
    outValue = m[outsider[0][0]][outsider[0][1]]

    paramsFirst = [20,50,100,outValue,25,100]
    #Parameter fuer's region growing auf der ersten Schicht: threshold, seedThreshold , Iterationen, 
    #OutsiderThreshold, gradientThreshold, varianceThreshold
    #eventuell abweichend von Parametern fuer spaetere Schichten
    params = [30,50,20,outValue + 10]
    #Parameter fuer's Region Growing der spaeteren Schichten:
    #threshold, seedThreshold , Iterationen, OutsiderThreshold

    first = fL.firstLayers(u,m,l,paramsFirst,uArr)
    #plt.imshow(first)
    #plt.show()
    #Segmentierung der mittleren Schicht
    downPath = nSeed.next_seeds(m,first)
    upPath = nSeed.next_seeds(m,first)
    #Generation der Seeds fuer naechste layer, 
    #Abhaengigkeit vom naechsten Layer entfernen, sobald ordentlich implementiert

    f = pydicom.dcmread("medbv_seg/P"+str(satz).zfill(2)+"/img"+str(mitte).zfill(4)+".dcm").pixel_array
    result = groundT.GroundTruthAbgleich(first,f)
    #print(result)
    #print("Gesamt-3D-Dice-Koeffizient: " + str(((2*result[0]) / (2*result[0] + result[1] + result[3]))) )
    #oeffnet den Ground Truth des mittleren layer und nutzt ihn zur Initialisierung des Endergebnisses
    #result[4] (dice-koeff. der Schicht) durch Additionen (s.u.) nicht mehr zu gebrauchen!
    #am Ende Gesamtdice bestimmen!
    #bei mehreren threads separate Ergebnisse erforderlich, die erst am Ende zusammengeführt werden!
    visualizeImgUpper = first.copy()
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
        visualizeImgUpper += tmpSeg
        result += groundT.GroundTruthAbgleich(tmpSeg,gArr)
        #bestimmt Segmentierungsqualitaet der Schicht und addiert zum Gesamtergebnis

        """
        fig = plt.figure(figsize=(2,1))
        fig.add_subplot(2,1,1)
        plt.imshow(tmpSeg)
        fig.add_subplot(2,1,2)
        plt.imshow(gArr)
        plt.show()
        """

        #print(result)
        #print("Gesamt-3D-Dice-Koeffizient: " + str(((2*result[0]) / (2*result[0] + result[1] + result[3]))) )
        
        upPath = nSeed.next_seeds(pArr,tmpSeg)
        #bestimmt den naechsten Satz Seeds

        #TODO so modifizieren, dass fuer jede Partition ab diesem Punkt eine seperates Growing erfolgt
        #vielleicht unnoetig / unnoetig umstaendlich?

    #plt.imshow(visualizeImgUpper)
    #plt.show()
    visualizeImgLower = first.copy()
    #---------------------------------------------------------------------------------------------------
    #Schichten unter der Mitte
    for i in range(mitte -1, 0, -1):
        #range backwards, 0 not included (1-basierte Nummerierung in Datensatz)
        pArr = pydicom.dcmread("medbv_data/P"+str(satz).zfill(2)+"/img"+str(i).zfill(4)+".dcm").pixel_array
        #laedt i-tes Bild und extrahiert pixelArray
        segParts = rG.RegionGrowing(pArr,downPath, params)
        
        tmpSeg = np.zeros(pArr.shape)
        for j in range (0,len(segParts)):
            tmpSeg += segParts[j]
        #fuegt die Partitionen der Segmentierung zusammen, um unverfaelscht die Qualitaet
        #der Segmentierung bestimmen = Vergleich mit Ground Truth machen zu koennen

        gArr = pydicom.dcmread("medbv_seg/P"+str(satz).zfill(2)+"/img"+str(i).zfill(4)+".dcm").pixel_array
        #laedt i-ten Ground Truth und extrahiert pixelArray
        visualizeImgLower += tmpSeg
        visualizeImgUpper += tmpSeg
        result += groundT.GroundTruthAbgleich(tmpSeg,gArr)
        #bestimmt Segmentierungsqualitaet der Schicht und addiert zum Gesamtergebnis

        #plt.imshow(tmpSeg)
        #plt.show()

        #print(result)
        #print("Gesamt-3D-Dice-Koeffizient: " + str(((2*result[0]) / (2*result[0] + result[1] + result[3]))) )
        
        downPath = nSeed.next_seeds(pArr,tmpSeg)
        #bestimmt den naechsten Satz Seeds
        
        #TODO so modifizieren, dass fuer jede Partition ab diesem Punkt eine seperates Growing erfolgt
        #vielleicht unnoetig / unnoetig umstaendlich?

    #plt.imshow(visualizeImgLower)
    #plt.show()
    #visualizeImgLower += visualizeImgUpper
    plt.imshow(visualizeImgUpper)
    plt.show()
    #print(result)
    print("Satznummer: " + str(satz) + "; Gesamt-3D-Dice-Koeffizient: " + str(((2*result[0]) / (2*result[0] + result[1] + result[3]))) )

#==============================================================================
#allSets(1,80)
#allSets(2,80)
#allSets(3,80)
#allSets(4,80)
#allSets(5,75)
#allSets(6,80)
#allSets(8,93)
#allSets(9,80)
#allSets(10,80)
#allSets(11,80)
#allSets(12,70)

        
