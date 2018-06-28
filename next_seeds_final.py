import numpy as np
def next_seeds(previmg, prevseg):
    #laesst einen modifizierten Minimum-Filter ueber das Bild wandern, um neue Seeds zu berechnen
    #Input: Bild und zugehörige Segmentierung
    seed_arr = list()
    previmgarr = np.array(previmg) #TODO check if hardcopies; in current pipeline irrelevant
    prevsegarr = np.array(prevseg) #but in different order might have side effects
    n = 11 #Kernelgroesse
    m = int(n/2) #halbe Kernelgroesse fuer Randbehandlung(keine Seeds setzen dort)
    flag = 0
    for j in range(m, 320-m):
        for i in range(m, 320-m): #Bild minus Rand an allen Seiten
            for k in range(0,n):
                if(flag == 1): #vorzeitiger Abbruch, wenn bereits 0 gefunden
                    continue
                for l in range (0,n):
                    if(prevsegarr[i-m+k][j-m+l] == 0): #erste 0 gefunden -> flag fuer Abbruch
                        flag = 1
                        continue
            if(flag == 0): #wenn kompletter Kernel 1
                seed_arr.append([i, j, previmgarr[i,j]]) #Seed aus Position und Wert anfuegen
                prevsegarr[i,j] = 0 #Pixel im Bild entwerten, damit Seeds Mindestabstand haben (halber Kernel)
            flag = 0 #reset flag
    #Output: Liste von Seeds (x,y,value)
    return seed_arr