# drchrono Flu Epicenter Detection

### Website:
martinborgt.com

### What is this
An app that detects epicenters of flu outbreaks, configured to detect three epicenters in San Jose that has the ability to generate input data for simulation purposes.

### Forked from
https://github.com/drchrono/api-example-django

### Requirements
- [pip](https://pip.pypa.io/en/stable/)
- [python virtual env](https://packaging.python.org/installing/#creating-and-using-virtual-environments)

### Setup
``` bash
$ pip install -r requirements.txt
$ python manage.py runserver
```

### In order to get this working, set in /drchrono/settings.py:

```
SOCIAL_AUTH_DRCHRONO_KEY
SOCIAL_AUTH_DRCHRONO_SECRET

SOCIAL_AUTH_ONPATIENT_KEY
SOCIAL_AUTH_ONPATIENT_SECRET
```
