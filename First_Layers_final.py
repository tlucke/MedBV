import numpy as np
import cv2 as cv
import Region_Growing_final as rG
#===============================================================================================
def firstLayers(upperLayer, middleLayer, lowerLayer, parameters, uArr):
    #Input: PixelArrays of the middle +/- 1 Layers; Array with several parameters,
    #Liste von Seeds aus Nutzer-Interaktion(x,y,value)
    
    #Parameters for Region Growing
    threshold = parameters[0]      #threshold region growing
    seedThreshold = parameters[1]  #threshold seed reject
    maxDist = parameters[2]        #max iterations of region growing

    
    SeedArray = []
    for i in range(0, len(uArr)):
        SeedArray.append((uArr[i][0],uArr[i][1],middleLayer[uArr[i][0]][uArr[i][1]]))
    SeedArray = np.array(SeedArray)
    #fuegt den Positionen aus der UserInteraction die Werte hinzu
    outsiderThreshold = parameters[3]

    #Parameters for further processing
    gradientThreshold = parameters[4] #threshold for squared gradient 
    #(currently effectivly not used since it's set ways too low, also effect if used in doubt)
    varianceThreshold = parameters[5] #(nicht benutzt bisher)

    #Idee: thresholds durch Streuung und Wertebereich des SeedArrays/Outsiders anpassen,
    #am besten zusammen mit "Linienimplementation" der Nutzerinteraktion, weil mehr und 
    #repraesentativer verteilte Werte benoetigt

    #Inital Region Growing on Layers
    params = [threshold, seedThreshold, maxDist, outsiderThreshold]
    segUpper = rG.RegionGrowing(upperLayer,SeedArray,params)
    segMiddle = rG.RegionGrowing(middleLayer,SeedArray,params)
    segLower = rG.RegionGrowing(lowerLayer,SeedArray,params)

    #calculate gradients of layers
    sobelXUpper = cv.Sobel(upperLayer,cv.CV_64F,1,0,3)
    sobelYUpper = cv.Sobel(upperLayer,cv.CV_64F,0,1,3)
    absGradUpper = pow(sobelXUpper,2) + pow(sobelYUpper,2)
    sobelXMiddle = cv.Sobel(middleLayer,cv.CV_64F,1,0,3)
    sobelYMiddle = cv.Sobel(middleLayer,cv.CV_64F,0,1,3)
    absGradMiddle = pow(sobelXMiddle,2) + pow(sobelYMiddle,2)
    sobelXLower = cv.Sobel(lowerLayer,cv.CV_64F,1,0,3)
    sobelYLower = cv.Sobel(lowerLayer,cv.CV_64F,0,1,3)
    absGradLower = pow(sobelXLower,2) + pow(sobelYLower,2)

    #if pixel only in one segmantation, check some constraints
    #if not passed -> delete
    segAll = segUpper[0] + segMiddle[0] + segLower[0]
    for i in range(0,middleLayer.shape[0]):
        for j in range(0,middleLayer.shape[1]):
            if(segAll[i][j] == 1): 
                maxGrad = max(absGradUpper[i][j],absGradMiddle[i][j], absGradLower[i][j])
                if(maxGrad > gradientThreshold):
                    #local gradient too strong so likely on edge
                    segAll[i][j] = 0
                    continue
                #TODO:add more and better constraints
                #currently in effect only "voting", since constraints always failed, but might be better this way
            elif(segAll[i][j] > 1):
                segAll[i][j] = 1
    

    #morphological closing
    kernelY = np.array([[1],[1]])
    kernelX = np.array([[1,1]])
    #TODO test different kernels, don't forget to change "shift" parameter
    closingY = cv.morphologyEx(segAll, cv.MORPH_CLOSE, kernelY)
    closingX = cv.morphologyEx(closingY, cv.MORPH_CLOSE, kernelX)
    result = closingX
    shift = 1 #rows/columns for backshift
    for i in range(shift,middleLayer.shape[0]):
        for j in range(shift,middleLayer.shape[1]):
            result[i-shift][j-shift] = result[i][j]
    #shifts back up "shift" row/column after down/right shift due to closing
    #"deletes" top row/column, doubles bottom row/column
    #no errors expected, since region is irrelevant
    #TODO check if shift already in closing included! Aber Fehler von 1 Pixel in x,y auf einer Schicht kaum relevant
    return result
#===============================================================================================