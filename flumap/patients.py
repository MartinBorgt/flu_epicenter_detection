import random, math, os
import map_manipulation, matplotlib
import numpy as np
from scipy.stats import multivariate_normal
from matplotlib import pyplot as plt
from django.conf import settings
if not settings.configured:
    settings.configure(DEBUG=True)

plot_dist = False
# Creates num patients, all without flu, so no bool for that needed
# maxrow and maxcol define the limits of the grid the patients are created on, num is the number of patients generated
def generate_patients(dimensions, num):
    maxrow, maxcol = dimensions
    # A patient has an x and a y location on the map and a flu boolean
    return [(random.randint(0, maxcol-1), random.randint(0, maxrow-1)) for _ in range(num)]

# patient_group is a list of all patients
# epicenters is a list defining the places at which the chance of contracting  the flu is highest
# cov_mats is a list containing covariance matrices that define the shape of the areas where there is a higher
# chance of contracting the flu
# shape
def randomly_infect_patients(patient_group, epicenters, cov_mats, shape, sessionkey):
    # Initialize a probability distribution
    print(epicenters)
    x, y = np.mgrid[0:shape[0]:1, 0:shape[1]:1]

    # Find the probability distribution for each of the mean, cov matrix pairs
    # 500 - ep[1] because 0 is at the top of the image
    rvs = [multivariate_normal(mean=[ep[0], 500 - ep[1]], cov=covmat) for ep, covmat in zip(epicenters, cov_mats)]
    #rv = multivariate_normal(mean=[50, 20], cov=[[200, 30], [30, 50]])
    pos = np.empty(x.shape + (2,))
    pos[:, :, 0] = x
    pos[:, :, 1] = y
    probability_dist = sum([rv.pdf(pos) for rv in rvs])

    # normalize the data
    minp = min([min(p) for p in probability_dist])
    maxp = max([max(p) for p in probability_dist])
    probability_dist_img = [[[128, 0, 0, (p-minp)/(maxp-minp)] for p in row] for row in probability_dist]

    map_manipulation.image_from_array(probability_dist_img, 'generated_contour-{}.png'.format(sessionkey))
    #print('probdistlimits ', max([max(p) for p in probability_dist]), min([min(p) for p in probability_dist]))

    if plot_dist:
        print('before')
        figure, ax = plt.subplots(1)

        # Set whitespace to 0
        figure.subplots_adjust(left=0, right=1, bottom=0, top=1)
        plt.contourf(x, y, probability_dist)

        ax.axis('off')
        ax.axis('tight')
        figure.canvas.draw()

        # Get the RGBA buffer from the figure
        w, h = figure.canvas.get_width_height()
        imarray = np.fromstring(figure.canvas.tostring_argb(), dtype=np.uint8)
        imarray.shape = (h, w, 4)
        imarray = np.roll(imarray, 3, axis=2)
        map_manipulation.image_from_array(imarray, 'generated_contour.png')

        figure.clf()
        plt.close(figure)
        print('after')
    # Infect high risk patients
    returnpatients = []
    for i, j in patient_group:
        # "f" for flu and "" for not flu instead of Boolean to make patients JSON serializable, still evaluate to True
        # and False
        returnpatients.append((i, j, "f" if probability_dist[i][j] > np.random.random() * 0.00075 - 0.00001 else ""))

    return returnpatients

# patients is a list of all patients
# (groupsize x groupsize) determines the size of each cluster for which a density is determined
# totalsize is a tuple containing the width and height of the area the density clustering is done in
def find_flu_density(patients, groupsize, totalsize):
    # A dictionary is made to group all patients
    grouped_patients = {(a, b): [] for a in range(0, totalsize[0], groupsize) for b in range(0, totalsize[1], groupsize)}

    # The flu value of each patient is added to their group
    for row, col, flu in patients:
        groupindex = (row - row % groupsize, col - col % groupsize)
        if groupindex in grouped_patients:
            grouped_patients[groupindex].append(flu)
    # The densities are calculated for each location
    densities = {loc: float(len([p for p in pat if p])) / len(pat) if len(pat) > 0 else 0.0 for loc, pat in grouped_patients.iteritems()}
    return densities

# TO better adapt to input data the cutoff could just be modified to return the 20% highest density points
def find_density_cutoff(flu_density, groupsize, cutoff):
    cutoff_patients = []
    for (row, col), density in flu_density.iteritems():
        if density > cutoff:
            cutoff_patients.append((row + groupsize // 2, col + groupsize // 2, True))
    return cutoff_patients
