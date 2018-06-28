
import cv2
import pydicom
import matplotlib.pyplot as plt
#==========================================================================================
#globale Variablen
outside_value = list()
mouse_coordinates = list()
#==========================================================================================
def mouse_callback1(event, x, y, flags, params):
    #mouse click tracker for seeds
	if event == cv2.EVENT_LBUTTONDOWN:
        #if mouse button pushed while in window
		global mouse_coordinates
		mouse_coordinates.append([y,x])
		#print(mouse_coordinates)
#==========================================================================================
def mouse_callback2(event, x, y, flags, params):
    #mouse click tracker for outsider
	if event == cv2.EVENT_LBUTTONDOWN:
        #if mouse button pushed while in window
		global outside_value
		outside_value.append([y,x])
		#print(outside_value)
#==========================================================================================
def user_interaction(image):
    del mouse_coordinates[:] #resets globel variables used for mouse callback
    del outside_value[:]
    plt.imsave("imgtest",image)
    img = cv2.imread("imgtest.png", 0)
    #save as + read, since OpenCV can't handle pixel array directly
	
    print("1. Select points inside the liver (INSIDE VALUES). Press any key to continue. Do not close the window manually!")
    cv2.namedWindow('INSIDE VALUES')
    cv2.setMouseCallback('INSIDE VALUES', mouse_callback1)
    cv2.imshow('INSIDE VALUES', img)
    cv2.waitKey(0)

    print("2. Select a point outside the liver (OUTSIDE VALUE). Press any key to continue. Do not close the window manually!")
    cv2.namedWindow('OUTSIDE VALUE')
    cv2.setMouseCallback('OUTSIDE VALUE', mouse_callback2)
    cv2.imshow('OUTSIDE VALUE', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    #returns list of seeds(x,y) and outsider(x,y)
    return mouse_coordinates, outside_value