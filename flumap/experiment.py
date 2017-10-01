import patients, map_manipulation, api_functions
import numpy as np
from scipy import random
from sklearn import mixture
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy.stats import multivariate_normal
from models import Patient, PatientList, Gaussian
from social.apps.django_app.default.models import UserSocialAuth
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from django.conf import settings
if not settings.configured:
    settings.configure(DEBUG=True)

plot_dist = False

def load(sessionkey):
    # Get the token needed to receive data from the api
    socialdrchrono = UserSocialAuth.objects.filter(provider='drchrono')[0]

    # Get the patients from the api
    all_patients = api_functions.get_all_patients(socialdrchrono)

    # Keep track of which patients are on the map
    patients_on_map = []

    geolocator = Nominatim()

    for patient in all_patients:
        if not Patient.objects.filter(id=patient['id']).exists():
            # Locate the patient
            try:
                location = geolocator.geocode('{} {}, {}'.format(patient['address'], patient['city'], patient['state']))
            except GeocoderTimedOut:
                location = None
            # img top left = {lat: 37.492294, long: -122.2290802}
            # img bot right = {lat: 37.17454296, long: -121.80885315}

            onmap = False
            hasflu = False
            patientlatlong = None

            if not location is None:
                # Determine latitude and longitude for all patients
                patientlatlong = map_manipulation.latlong_to_map({'lat': 37.532293, 'long': -122.2290802},
                                                {'lat': 37.174235, 'long': -121.80885315},
                                                {'lat': location.latitude, 'long': location.longitude}, 500)

            if patientlatlong is None:
                patientlatlong = {'y': 0, 'x': 0}
            else:
                onmap = True
                # Find out whether a patient on the map is known to have the flu
                hasflu = api_functions.has_the_flu(socialdrchrono, patient['id'])


            saved_pat = Patient.objects.create(
                id=patient['id'],
                name=patient['last_name'],
                address=patient['address'],
                has_flu=hasflu,
                on_map=onmap,
                x_on_map=patientlatlong['x'],
                y_on_map=patientlatlong['y']
            )
            saved_pat.save()
            # Add patients that are on the map to the list
            if onmap:
                patients_on_map.append((patientlatlong['x'], patientlatlong['y'], hasflu))
        else:
            # If this patient is in the database already, add it to the patients on map list if it is on the map
            saved_pat = Patient.objects.filter(id=patient['id'])[0]

            # Find out if the patients flu value has changed
            print('checking flu for ', patient['last_name'])
            saved_pat.setflu(api_functions.has_the_flu(socialdrchrono, patient['id']))

            if saved_pat.on_map:
                patients_on_map.append((saved_pat.x_on_map, saved_pat.y_on_map, saved_pat.has_flu))
            #pass

    # Save all the info we want to save about the patients on the map
    if not PatientList.objects.filter(sessionkey=sessionkey).exists():
        plist = PatientList.objects.create(sessionkey=sessionkey, simulated=False)
    else:
        plist = PatientList.objects.filter(sessionkey=sessionkey)[0]
    plist.setpatients(patients_on_map, False)
    plist.save()

    # Add the patients to the image

    # Load the image the overlay will be placed on
    map_array, size_of_grid = load_img_and_size("San_Jose_map.tif")
    # Adds patients size 5 x 5, color blue to image
    # Healthy patients
    map_manipulation.add_patients_to_img(map_array, [p[:2] for p in patients_on_map if not p[2]], 5, [0, 0, 128, 255])
    # Ill patients
    map_manipulation.add_patients_to_img(map_array, [p[:2] for p in patients_on_map if p[2]], 5, [128, 0, 0, 255])
    print('patients added')
    # Session keys are used to store unique images for each session
    map_manipulation.image_from_array(map_array, "San_Jose_map-{}.tif".format(sessionkey))


def generate(sessionkey):
    # Load the image the overlay will be placed on
    map_array, size_of_grid = load_img_and_size("San_Jose_map.tif")

    # Create 10000 patients
    generated_patients = patients.generate_patients(size_of_grid, 10000)

    # Adds patients size 5 x 5, color blue to image
    map_manipulation.add_patients_to_img(map_array, generated_patients, 5, [0, 0, 128, 255])
    print('patients added')
    # Session keys are used to store unique images for each session
    map_manipulation.image_from_array(map_array, "San_Jose_map-{}.tif".format(sessionkey))

    # If this session has not patientlist yet, make one new, otherwise just update the list to the newly generated values
    if not PatientList.objects.filter(sessionkey=sessionkey).exists():
        plist = PatientList.objects.create(sessionkey=sessionkey, simulated=True)
    else:
        plist = PatientList.objects.filter(sessionkey=sessionkey)[0]
    plist.setpatients(generated_patients, True)
    plist.save()


def infect(sessionkey):
    # Check if we have generated or loaded patients in this session, if not just generate some now
    if not PatientList.objects.filter(sessionkey=sessionkey).exists():
        generate(sessionkey)

    # get the generated or loaded patients
    plist = PatientList.objects.filter(sessionkey=sessionkey)[0]
    generated_patients = plist.getpatients()

    # If patients have already got a flu boolean, do nothing
    if len(generated_patients[0]) > 2:
        return

    # Load the image that has patients plotted on
    map_array, size_of_grid = load_img_and_size("San_Jose_map-{}.tif".format(sessionkey))
    number_of_epicenters = 3
    # Three random places with oval covariance matrices will make flu epicenters
    generated_epicenters = patients.generate_patients(size_of_grid, number_of_epicenters)
    covariance_matrices = [random_pos_semidef_matrix() for _ in range(number_of_epicenters)]
    print('infecting...')

    # Infect patients with a chance proportional to their mahalonobis distance to the epicenters
    patients_with_infected = patients.randomly_infect_patients(generated_patients, generated_epicenters,
                                                               covariance_matrices, size_of_grid, sessionkey)
    # Plot the infected patients over their healthy positions
    map_manipulation.add_patients_to_img(map_array, [p[:2] for p in patients_with_infected if p[2]], 5, [128, 0, 0, 255])

    # Save the patients
    plist.setpatients(patients_with_infected, True)
    plist.save()

    # Create a new image with all infectd patients in red
    map_manipulation.image_from_array(map_array, 'San_Jose_map-infected-{}.tif'.format(sessionkey))


def mixturegaussian(sessionkey):
    # If there are no patients, generate and infect some
    if not PatientList.objects.filter(sessionkey=sessionkey).exists():
        infect(sessionkey)

    # get the generated or loaded patients
    plist = PatientList.objects.filter(sessionkey=sessionkey)[0]
    patients_with_infected = plist.getpatients()

    # If the patients do not have a flu value, give them one load them again
    if len(patients_with_infected[0]) == 2:
        infect(sessionkey)
        plist = PatientList.objects.filter(sessionkey=sessionkey)[0]
        patients_with_infected = plist.getpatients()

    map_array, size_of_grid = load_img_and_size("San_Jose_map-{}.tif".format(sessionkey))

    groupsize = 20
    # Calculate the number of people with the flu / total number of people in each area of groupsize x groupsize
    flu_density = patients.find_flu_density(patients_with_infected, groupsize, size_of_grid)

    # Find the areas in which this density value is above the cutoff value
    high_density = patients.find_density_cutoff(flu_density, groupsize, 0.085)

    # Find the best combination of Gaussian distributions that could generate this data
    distrib = mixture_gaussian(high_density, sessionkey)

    # remove all earlier saved gaussians
    Gaussian.objects.all().delete()

    for counter in range(len(distrib)):
        mean, covar = distrib[counter]

        gauss = Gaussian.objects.create(
        )
        # Save integer values, rounding does not make much difference because we work with high numbers
        gauss.setmean([int(m) for m in mean])
        gauss.setcovar([[int(c) for c in covrow] for covrow in covar])
        gauss.save()





def findme():
    # Load all patients
    # Get the token needed to receive data from the api
    socialonpatient = UserSocialAuth.objects.filter(provider='onpatient')[0]

    # Find the address of the patient
    patient_data = api_functions.get_a_patient(socialonpatient)
    geolocator = Nominatim()
    try:
        location = geolocator.geocode('{} {}, {}'.format(patient_data['address'][0]['line'][0],
                                            patient_data['address'][0]['city'], patient_data['address'][0]['state']))
    except GeocoderTimedOut:
        location = None

    patientlatlong = None

    if location is None:
        return 'unknownlocation'
    # Determine latitude and longitude for all patients
    patientlatlong = map_manipulation.latlong_to_map({'lat': 37.532293, 'long': -122.2290802},
                                                     {'lat': 37.174235, 'long': -121.80885315},
                                                     {'lat': location.latitude, 'long': location.longitude}, 500)

    if patientlatlong is None:
        return 'notonmap'

    # Find out whether the patient is close to a flu epicenter using the mahalanobis distance to the closest epicenter
    # A different way would be using the value in the found probability distribution
    for gauss in Gaussian.objects.all():
        # Load the relevant variables
        m = np.array(gauss.getmean())
        cov = np.array(gauss.getcovar())
        x = np.array([patientlatlong['x'], patientlatlong['y']])


        # Calculate mahalanobis distance
        mdist = np.sqrt(np.dot((x - m), np.dot(np.linalg.inv(cov), (x - m))))

        # Close is defined as a mahalanobis distance of less than 2
        if mdist < 2:
            return 'atrisk'
    return 'notatrisk'



def load_img_and_size(imgname):
    map_array = map_manipulation.array_from_image(imgname)
    return map_array, (len(map_array), len(map_array[0]))

#The session key is used to call the right images for the right users
def map_with_patients(sessionkey):
    map_array = map_manipulation.array_from_image("San_Jose_map.tif")
    size_of_grid = (len(map_array), len(map_array[0]))
    generated_patients = patients.generate_patients(size_of_grid, 10000)

    # Adds patients size 20 x 20, color blue
    map_manipulation.add_patients_to_img(map_array, generated_patients, 5, [0, 0, 128, 255])
    print('patients added')
    number_of_epicenters = 3
    generated_epicenters = patients.generate_patients(size_of_grid, number_of_epicenters)
    covariance_matrices = [random_pos_semidef_matrix() for _ in range(number_of_epicenters)]
    print('infecting...')
    patients_with_infected = patients.randomly_infect_patients(generated_patients, generated_epicenters,
                                                               covariance_matrices, size_of_grid, sessionkey)

    # Turns infected patients red
    map_manipulation.add_patients_to_img(map_array, [p[:2] for p in patients_with_infected if p[2]], 5, [128, 0, 0, 255])
    print('infected')
    groupsize = 20
    flu_density = patients.find_flu_density(patients_with_infected, groupsize, size_of_grid)
    #print('flu density: ', flu_density)
    high_density = patients.find_density_cutoff(flu_density, groupsize, 0.085)
    #mixture_gaussian(patients_with_infected)
    mixture_gaussian(high_density, sessionkey)
    #print(covariance_matrices)
    map_manipulation.image_from_array(map_array, 'maptest-{}.tif'.format(sessionkey))
    #print(map_array.shape)

# map_with_patients()

def random_pos_semidef_matrix():
    A = np.multiply(random.rand(2, 2) + 0.5, [[40, -1], [-1, 40]])
    return np.dot(A, A.transpose())

def mixture_gaussian(patients, sessionkey):
    positive_patients = np.vstack([[p[0], p[1]] for p in patients if p[2]])
    #print(positive_patients)
    clf = mixture.GaussianMixture(n_components=3, covariance_type='full')
    clf.fit(positive_patients)
    #print(clf.means_)
    #print(clf.covariances_)
#####################################################
    x, y = np.mgrid[0:500:1, 0:500:1]
    rvs = [multivariate_normal(mean=ep, cov=covmat) for ep, covmat in zip(clf.means_, clf.covariances_)]

    pos = np.empty(x.shape + (2,))
    pos[:, :, 0] = x
    pos[:, :, 1] = y
    probability_dist = sum([rv.pdf(pos) for rv in rvs])
    minp = min([min(p) for p in probability_dist])
    maxp = max([max(p) for p in probability_dist])
    probability_dist_img = [[[128, 0, 0, (p-minp)/(maxp-minp)] for p in row] for row in probability_dist]
    #print('probdistlimits ', maxp, minp)

    map_manipulation.image_from_array(probability_dist_img, 'result_contour-{}.png'.format(sessionkey))

    if plot_dist:
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
        #map_manipulation.image_from_array(imarray, 'result_contour.png')


        #figure.savefig(img_path)
        plt.close(figure)

    # Return the means and covariance matrices of the found distribution
    return zip(clf.means_, clf.covariances_)
