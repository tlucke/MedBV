import pydicom
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import matplotlib.colors
#==========================================================================================
import Ground_Truth_Abgleich_3D_final as groundT
import Region_Growing_final as rG
import user_interaction_final as uInter
import next_seeds_final as nSeed
import First_Layers_final as fL
#==========================================================================================
def allSets(number,numberSlices):
    #Main
    visualizeSlices = False
    Tests = False
    printSlices = False #only if Tests == True
    

    satz = number #Datensatz
    bildzahl = numberSlices #Anzahl Schichten im Datensatz
    mitte = int(bildzahl / 2)

    #Schema zum Einlesen eines Bildes; einsetzen für "bild"; für Ground-Truth-Daten: "data" zu "seg"
    #"medbv_data/P"+str(satz).zfill(2)+"/img"+str(bild).zfill(4)+".dcm"
    m = pydicom.dcmread("medbv_data/P"+str(satz).zfill(2)+"/img"+str(mitte).zfill(4)+".dcm").pixel_array
    u = pydicom.dcmread("medbv_data/P"+str(satz).zfill(2)+"/img"+str(mitte +1).zfill(4)+".dcm").pixel_array
    l = pydicom.dcmread("medbv_data/P"+str(satz).zfill(2)+"/img"+str(mitte -1).zfill(4)+".dcm").pixel_array
    #oeffnet die ersten 3 layer (aus der Mitte) des Datensatzes

    uArr, outsider = uInter.user_interaction(m) #bestimmt Seeds fuer erste Schichten durch UserInteraction
    outValue = m[outsider[0][0]][outsider[0][1]]

    paramsFirst = [20,50,100,outValue,25,100]
    #Parameter fuer's region growing auf der ersten Schicht: threshold, seedThreshold , Iterationen, 
    #OutsiderThreshold, gradientThreshold, varianceThreshold(nicht benutzt letztendlich)
    #abweichend von Parametern fuer spaetere Schichten
    params = [30,50,20,outValue + 10]
    #Parameter fuer's Region Growing der spaeteren Schichten:
    #threshold, seedThreshold , Iterationen, OutsiderThreshold

    first = fL.firstLayers(u,m,l,paramsFirst,uArr)
    #Segmentierung der mittleren Schicht
    visualizeImg = first.copy() 
    #initialisiert Schicht-Summen-Bild
    downPath = nSeed.next_seeds(m,first)
    upPath = nSeed.next_seeds(m,first)
    #Generation der Seeds fuer naechste layer, 

    f = pydicom.dcmread("medbv_seg/P"+str(satz).zfill(2)+"/img"+str(mitte).zfill(4)+".dcm").pixel_array
    #zeigt Segmentierung der ersten Schicht neben Grundwahrheit
    if(visualizeSlices):
        fig = plt.figure(figsize=(2,1))
        fig.add_subplot(2,1,1)
        plt.imshow(first)
        fig.add_subplot(2,1,2)
        plt.imshow(f)
        plt.show()        
    #---------------------------------------------------------------------------------------------------
    #Qualitätsmetriken auf erste Schicht / Initialisierung der Summierungen
    if(Tests):
        result = groundT.GroundTruthAbgleich(first,f)
        #oeffnet den Ground Truth des mittleren layer und nutzt ihn zur Initialisierung des Endergebnisses
        #result[4] (dice-koeff. der Schicht) durch Additionen (s.u.) nicht mehr zu gebrauchen!
        #am Ende Gesamtdice bestimmt
        Hausdorff = [0,0,0,0] #max,gesamt,anzahl schichten in Wertung,anzahl falsch leerer Schichten
        hd = groundT.Hausdorff(first,f)
        if (hd >= 0):
            if (Hausdorff[0] < hd):
                Hausdorff[0] = hd
            Hausdorff[1] += hd
            Hausdorff[2] += 1
        if(hd == -1):
            Hausdorff[3] += 1
        if(printSlices):
            print(result)
            print("1.Schicht-Dice-Koeffizient: " + str(((2*result[0]) / (2*result[0] + result[1] + result[3]))) )
            print("1.Schicht-Hausdorff-Distanz: " + str(hd) )
    #---------------------------------------------------------------------------------------------------
    #Schichten ueber der Mitte
    for i in range(mitte +1, bildzahl +1):
        #bildzahl +1, da 1-basierte Nummerierung in Datensatz
        pArr = pydicom.dcmread("medbv_data/P"+str(satz).zfill(2)+"/img"+str(i).zfill(4)+".dcm").pixel_array
        #laedt i-tes Bild und extrahiert pixelArray
        segSlice = rG.RegionGrowing(pArr,upPath, params)
        visualizeImg += segSlice[0] #addiert zum Schicht-Summen-Bild

        #laedt i-ten Ground Truth und extrahiert pixelArray
        gArr = pydicom.dcmread("medbv_seg/P"+str(satz).zfill(2)+"/img"+str(i).zfill(4)+".dcm").pixel_array
        #zeigt Segmentierung der Schicht neben Grundwahrheit
        if(visualizeSlices):
            fig = plt.figure(figsize=(2,1))
            fig.add_subplot(2,1,1)
            plt.imshow(segSlice[0])
            fig.add_subplot(2,1,2)
            plt.imshow(gArr)
            plt.show()
        #bestimmt Segmentierungsqualitaet der Schicht und addiert zum Gesamtergebnis        
        if(Tests):
            result += groundT.GroundTruthAbgleich(segSlice[0],gArr)
            hd = groundT.Hausdorff(segSlice[0],gArr)
            if (hd >= 0):
                if (Hausdorff[0] < hd):
                    Hausdorff[0] = hd
                Hausdorff[1] += hd
                Hausdorff[2] += 1
            if(hd == -1):
                Hausdorff[3] += 1
            if(printSlices):
                print(result)
                print(str(i) + ".Schicht bis Mitte 3D-Dice-Koeffizient: " + str(((2*result[0]) / (2*result[0] + result[1] + result[3]))) )
                print(str(i) + ".Schicht-Hausdorff-Distanz: " + str(hd) )
        
        upPath = nSeed.next_seeds(pArr,segSlice[0])
        #bestimmt den naechsten Satz Seeds
    #---------------------------------------------------------------------------------------------------
    #Schichten unter der Mitte
    for i in range(mitte -1, 0, -1):
        #range backwards, 0 not included (1-basierte Nummerierung in Datensatz)
        pArr = pydicom.dcmread("medbv_data/P"+str(satz).zfill(2)+"/img"+str(i).zfill(4)+".dcm").pixel_array
        #laedt i-tes Bild und extrahiert pixelArray
        segSlice = rG.RegionGrowing(pArr,downPath, params)
        visualizeImg += segSlice[0]

        #laedt i-ten Ground Truth und extrahiert pixelArray
        gArr = pydicom.dcmread("medbv_seg/P"+str(satz).zfill(2)+"/img"+str(i).zfill(4)+".dcm").pixel_array
        #zeigt Segmentierung der Schicht neben Grundwahrheit
        if(visualizeSlices):
            fig = plt.figure(figsize=(2,1))
            fig.add_subplot(2,1,1)
            plt.imshow(segSlice[0])
            fig.add_subplot(2,1,2)
            plt.imshow(gArr)
            plt.show()        
        #bestimmt Segmentierungsqualitaet der Schicht und addiert zum Gesamtergebnis
        if(Tests):
            result += groundT.GroundTruthAbgleich(segSlice[0],gArr)
            hd = groundT.Hausdorff(segSlice[0],gArr)
            if (hd >= 0):
                if (Hausdorff[0] < hd):
                    Hausdorff[0] = hd
                Hausdorff[1] += hd
                Hausdorff[2] += 1
            if(hd == -1):
                Hausdorff[3] += 1
            if(printSlices):
                print(result)
                print(str(i) + ".Schicht bis Mitte 3D-Dice-Koeffizient: " + str(((2*result[0]) / (2*result[0] + result[1] + result[3]))) )
                print(str(i) + ".Schicht-Hausdorff-Distanz: " + str(hd) )
        
        downPath = nSeed.next_seeds(pArr,segSlice[0])
        #bestimmt den naechsten Satz Seeds   
    #---------------------------------------------------------------------------------------------------
    #Endausgabe
    plt.imshow(visualizeImg) #Summenbild der Segmentierung über alle Schichten
    plt.show()
    if(Tests):
        #print(result) #wenn summierte Zahlenwerte, statt Verhaeltnisse interessant
        print("Satznummer: " + str(satz) + "; Gesamt-3D-Dice-Koeffizient: " + str(((2*result[0]) / (2*result[0] + result[1] + result[3]))) )
        print("HausdorffDistanz: Maximum = "+str(Hausdorff[0])+"; Average = "+str(Hausdorff[1]/Hausdorff[2]))
        print("Fehlende Schichten : " + str(Hausdorff[3]))
#==============================================================================
#Datensaetze auswaehlen (2. Argument ist Zahl der Schichten - konstant fuer Datensatz)
#allSets(1,80)
#allSets(2,80)
#allSets(3,80)
#allSets(4,80)
#allSets(5,75)
#allSets(6,80)
allSets(8,93)
#allSets(9,80)
#allSets(10,80)
#allSets(11,80)
#allSets(12,70)

        
