# -*- coding: utf-8 -*-
"""
Created on Mon May 28 17:24:46 2018

@author: Thorsten
"""

import pydicom
import cv2 as cv
import numpy as np

def next_seeds(previmg, prevseg, nextimg):
	'''
	sets new seeds for a new layer of DICOM data by comparing a given previous layer, using 
	its segmentation, with its successor.
	to be used for region growing.
	INPUT: 	-previous layer + previous layer segmentation
				-next layer
	OUTPUT:  -array with seed coordinates
	'''
	
	seed_arr = list()
	
	''' 
	convert images previmg, prevseg and nextimg 
	to arrays 320x320
	'''
	'''
	previmgarr = np.array(previmg.pixel_array)
	prevsegarr = np.array(prevseg.pixel_array)
	nextimgarr = np.array(nextimg.pixel_array)
	'''
	
	previmgarr = np.array(previmg)
	prevsegarr = np.array(prevseg)
	nextimgarr = np.array(nextimg)
	
	'''
	for: iterate through the segmentation
		if seg_color_Value = 3: (3 equals the color of the liver in the given DICOM dataset)
			if prev_coord ><= next_coord (given threshold)
				put the coordinate into the seed_arr
			elif
				continue
	'''
	
	#threshold = 3 #TODO: Play around with threshold for possible better results
	
	n = 5	#block size
	m = int(n/2)
	for j in range(m, 320-m):       #change to image shape
		for i in range(m, 320-m):
			tmp = [[prevsegarr[k][h] for k in range(i-m,i+m+1)] for h in range(j-m,j+m+1)]
			
			#tmp = prevsegarr[(i-m) : (i+m+1), (j-m) : (j+m+1)]
			#print(tmp[i,j])
			if( np.prod(tmp) != 0 ):
				seed_arr.append([i, j, previmgarr[i,j]])
				prevsegarr[i,j] = 0
			
	return seed_arr

'''TEST RANGE'''
'''
prev = pydicom.dcmread("medbv_data/P01/img0020.dcm")
prevseg = pydicom.dcmread("medbv_seg/P01/img0020.dcm")
nxt = pydicom.dcmread("medbv_data/P01/img0021.dcm")

newseeds = next_seeds(prev, prevseg, nxt)
print(newseeds)
'''
