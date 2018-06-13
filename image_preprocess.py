# -*- coding: utf-8 -*-

import cv2
import pydicom
import numpy as np
import matplotlib.pyplot as plt

def image_preprocess(image):
    
    #n = 100
    plt.imsave("imgtest", image)
    #plt.imshow(image)
    img = cv2.imread('imgtest.png', 0)
    kernel = np.ones((2,2), np.uint8)
    edges = cv2.Canny(img, 100, 200)
    edges2 = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    combined = img + (img * edges)
    combined2 = img + (img * edges2)
    cv2.namedWindow('image')
    cv2.imshow('image', img)
    cv2.imshow('edges', edges)
    cv2.imshow('edges2', edges2)
    cv2.imshow('result', combined)
    cv2.imshow('result2', combined2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return combined
    
#TEST#RANGE##################################################
#Bild aus dcm wird als png gespeichert. TODO: bessere Ansätze

mouse_coordinates = list()
  
path_image = "medbv_data/P01/img0020.dcm"
ds = pydicom.dcmread(path_image)
plt.imsave("imgtest", ds.pixel_array)
img = cv2.imread('imgtest.png',0)
#coordinates = user_interaction(img)
image_preprocess(ds.pixel_array)
#print("Coordinates: " + str(coordinates))