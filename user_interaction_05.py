# -*- coding: utf-8 -*-
"""
@author: Thorsten
"""

import cv2
import pydicom
import matplotlib.pyplot as plt


def mouse_callback(event, x, y, flags, params):
    
    if event == cv2.EVENT_LBUTTONDOWN:
        global right_clicks
        
        right_clicks.append([x, y])
        
        print(right_clicks)


def user_interaction(image):
    print("Please select coordinates from which seed points are to be calculated.")
    print("For example first one point inside the liver and one outside for better processing")
    print("Press Q when you're finished.")
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', mouse_callback)
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return right_clicks


#TEST#RANGE##################################################
#Bild aus dcm wird als png gespeichert. TODO: bessere Ansätze
right_clicks = list()    
path_image = "medbv_data/P01/img0020.dcm"
ds = pydicom.dcmread(path_image)
plt.imsave("imgtest", ds.pixel_array)
img = cv2.imread('imgtest.png',0)
coordinates = user_interaction(img)
print("Coordinates: " + str(coordinates))