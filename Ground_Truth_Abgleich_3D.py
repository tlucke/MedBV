#Ground-Truth-Werte:
# 0 -> Padding -> negative
# 1 -> außerhalb Körper -> negative
# 2 -> Körper -> negative
# 3 -> Leber -> positive
# 4 -> Lebertumor? -> positive
# 5 -> ??? irgendwie daran/daneben? -> negative (wenn mehr Info auch im Code ändern!)

# !Warning!
# Dice-Koeffizient ist nur 2D, also für eine Slice, nicht verwenden!
# 3D-Dice-Koeffizient in der Main nach Summation aller Slice-Ground-Truth-Abgleiche errechnen!

import pydicom
import numpy as np
#===============================================================================================
def GroundTruthAbgleich(Segmentierung, GroundTruth):
    #Input:Segmentierung(2D-Array, Werte 0,1), GroundTruth(dicom.pixelarray, Werte s.o.)
    result = np.zeros(5)
    #Rückgabearray: [TruePositive, FalsePositive, TrueNegative, FalseNegative, Dice-Koeff.]
    #Dice-Koeff. = 2TP / (2TP + FP + FN)
    Segmentierung = np.array(Segmentierung)
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
    #print(result)
    #TODO fix for no positive ground truth / segmentation
    return result
#===============================================================================================
#Testmain:
"""
gt = pydicom.dcmread("medbv_seg/P01/img0040.dcm")
gtarr = gt.pixel_array
seg = np.ones(gtarr.shape)
for i in range(0, gtarr.shape[0]):
        for j in range(0, gtarr.shape[1]):
            seg[i][j] = np.random.randint(0,2)
#array mit random 0, 1 gefüllt
result = GroundTruthAbgleich(seg, gtarr)
print(result)
"""