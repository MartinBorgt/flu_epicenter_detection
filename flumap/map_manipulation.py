import numpy as np
import matplotlib.pyplot as plt
import os
from django.conf import settings
if not settings.configured:
    settings.configure(DEBUG=True)
from django.contrib.staticfiles.templatetags.staticfiles import static
import random

def array_from_image(imagename):
    # Can read PNG or TIFF
    # type of returned array is ndarray
    #print(os.path.join(settings.STATIC_ROOT))

    #url = static(imagename)
    #print(url)
    #print('{}\\flumap\\{}'.format(os.path.join(settings.STATIC_ROOT), imagename))
    return plt.imread('{}/flumap/img/{}'.format(os.path.join(settings.STATIC_ROOT), imagename))

def image_from_array(numpy_array, targetname):
    # creates an image and stores it in flumap with the chosen name

    plt.imsave('{}/flumap/img/{}'.format(os.path.join(settings.STATIC_ROOT), targetname), numpy_array)

# Takes an array and adds (size x size) gray for patients
def add_patients_to_img(numpy_array, patients, size, color):
    #print(patients)
    for col, row in patients:
        # Check if the patient is on the grid
        if (col >= 0 and row >= 0) and (len(numpy_array) > row and len(numpy_array[0]) > col):
            # Set them to grey
            numpy_array[max(0, row - size//2):min(len(numpy_array), row + size//2),
                    max(0, col - size//2):min(len(numpy_array[0]), col + size//2)] = color
    return numpy_array

# Take values of map and latitude longtitude of patient and put patient on map, return None if patient is off map
# size is the number of pixels on a row, we assume a square image
def latlong_to_map(topleft,  botright, patientloc, size):
    # return None if patient not on map
    if botright['lat'] > patientloc['lat'] or patientloc['lat'] > topleft['lat'] or \
        botright['long'] < patientloc['long'] or patientloc['long'] < topleft['long']:
        return None

    # Compute the latitude and longitude on the map
    # We assume we are zoomed in enough for the map to be practically square
    # (0, 0) is top left on image
    lat_on_map = int((topleft['lat'] - patientloc['lat'])/(topleft['lat'] - botright['lat']) * size)
    long_on_map = int((patientloc['long'] - topleft['long'])/(botright['long'] - topleft['long']) * size)
    return {'y': lat_on_map, 'x': long_on_map}
