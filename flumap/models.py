from django.db import models
import json

# Create your models here.

class Patient(models.Model):
    # The patient's id
    id = models.CharField(max_length=140, primary_key=True)

    # The patient's name
    name = models.CharField(max_length=140)

    # Their address
    address = models.TextField()

    # True if they have the flu
    has_flu = models.BooleanField(default=False)

    # True if they are located on the displayed map
    on_map = models.BooleanField(default=False)

    # The location on the map (Couldn't find a good way to store a pair of values?)
    x_on_map = models.IntegerField(default=0)
    y_on_map = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name

    def setflu(self, val):
        self.has_flu = val

class PatientList(models.Model):
    # The key for this user's session
    sessionkey = models.CharField(max_length=140, primary_key=True)
    # The list of latitude and longitude of patients
    # Using json to store the list as text
    patients = models.CharField(max_length=200000, default="")

    # Whether the data is simulated or real, to concat real data
    simulated = models.BooleanField(default=False)


    def setpatients(self, x, newsim):
        # Concat the patients to the list if the data is real
        if self.simulated or newsim:
            newpatients = []
        else:
            newpatients = self.getpatients()

        self.simulated = newsim
        self.patients = json.dumps(newpatients.extend(x))

    def getpatients(self):
        return json.loads(self.patients)

class Gaussian(models.Model):
    # Using json to save mean and covar
    mean = models.CharField(max_length=200, default="")
    covar = models.CharField(max_length=200, default="")

    def setmean(self, x):
        self.mean = json.dumps(x)

    def getmean(self):
        return json.loads(self.mean)

    def setcovar(self, x):
        self.covar = json.dumps(x)

    def getcovar(self):
        return json.loads(self.covar)
