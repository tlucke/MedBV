# -*- coding: utf-8 -*-
"""
Created on Mon May 28 17:24:46 2018
@author: Thorsten
"""

import pydicom
import cv2 as cv
import numpy as np
def next_seeds(previmg, prevseg):
    seed_arr = list()
    previmgarr = np.array(previmg)
    prevsegarr = np.array(prevseg)
    n = 11
    m = int(n/2)
    flag = 0
    for j in range(m, 320-m):
        for i in range(m, 320-m):
            for k in range(0,n):
                if(flag == 1):
                    continue
                for l in range (0,n):
                    if(prevsegarr[i-m+k][j-m+l] == 0):
                        flag = 1
                        continue
            if(flag == 0):
                seed_arr.append([i, j, previmgarr[i,j]])
                prevsegarr[i,j] = 0
            flag = 0		
    return seed_arr