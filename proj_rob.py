import pydicom
import matplotlib.pyplot as plt
import matplotlib.colors
print ("42")
#from pydicom.data import get_testdata_files
#test1 = get_testdata_files("img0001.dcm")[42]
#ds = pydicom.dcmread("medbv_data/P01/img0015.dcm")
#gt = pydicom.dcmread("medbv_seg/P01/img0015.dcm")
#print(ds)
#plt.imshow(ds.pixel_array)
#plt.show()
#plt.imshow(gt.pixel_array)
#plt.show()
norm1 = matplotlib.colors.Normalize()
for i in range(40, 41):
    ds = pydicom.dcmread("medbv_data/P01/img00" + str(i) + ".dcm")
    plt.imshow(ds.pixel_array,0,0,0,0,norm1(0,1024,True))
    plt.show()