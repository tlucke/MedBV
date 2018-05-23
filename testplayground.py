import numpy as np
import cv2 as cv

seg = np.ones((1000,1000))
for i in range(0, seg.shape[0]):
        for j in range(0, seg.shape[1]):
            seg[i][j] = np.random.randint(0,2)

cv.namedWindow('image', cv.WINDOW_NORMAL)
cv.resizeWindow('image',500,500)
cv.imshow('image',seg)
cv.waitKey()
cv.destroyAllWindows()