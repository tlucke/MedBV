# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 09:39:13 2018

@author: Thorsten
"""

import cv2
import pydicom
import matplotlib.pyplot as plt

outside_value = list()
mouse_coordinates = list()

def mouse_callback1(event, x, y, flags, params):
	if event == cv2.EVENT_LBUTTONDOWN:
		global mouse_coordinates
		mouse_coordinates.append([y,x])
		print(mouse_coordinates)

def mouse_callback2(event, x, y, flags, params):
	if event == cv2.EVENT_LBUTTONDOWN:
		global outside_value
		outside_value.append([y,x])
		print(outside_value)

def user_interaction(image):
	choice = ""
	while(choice != "q"):
		choice = input("Please select mode:\n1. Inside values\n2. Outside values\nq. Quit\n-->")
		plt.imsave("imgtest",image)
		img = cv2.imread("imgtest.png", 0)
		
		if(choice == "1"):
			cv2.namedWindow('image')
			cv2.setMouseCallback('image', mouse_callback1)
			cv2.imshow('image', img)
			cv2.waitKey(0)
			cv2.destroyAllWindows()
		elif choice == "2":
			cv2.namedWindow('image')
			cv2.setMouseCallback('image', mouse_callback2)
			cv2.imshow('image', img)
			cv2.waitKey(0)
			cv2.destroyAllWindows()
	return mouse_coordinates, outside_value

path_image = "medbv_data/P01/img0020.dcm"
ds = pydicom.dcmread(path_image)
plt.imsave("imgtest", ds.pixel_array)
img = cv2.imread('imgtest.png',0)
in_coordinates, out_coordinates = user_interaction(img)
print(in_coordinates)
print(out_coordinates)
#print("Coordinates: " + str(coordinates))

			
			