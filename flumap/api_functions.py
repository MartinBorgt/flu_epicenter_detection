import requests

def get_all_patients(social):

    patients = []
    patients_url = 'https://drchrono.com/api/patients'
    headers = {
        'Authorization': 'Bearer %s' % social.extra_data['access_token']
        }

    while patients_url:
        data = requests.get(patients_url, headers=headers)

        # Check for the case of no patients
        if not data:
            break

        json_data = data.json()
        patients.extend(json_data['results'])
        patients_url = json_data['next']  # A JSON null on the last page

    return patients

def get_a_patient(social):

    patients = []
    patients_url = 'https://drchrono.com//onpatient_api/fhir/Patient'
    headers = {
        'Authorization': 'Bearer %s' % social.extra_data['access_token']
        }

    while patients_url:
        data = requests.get(patients_url, headers=headers)

        # Check for the case of no patients
        if not data:
            break

        json_data = data.json()
        patients.extend(json_data['results'])
        patients_url = json_data['next']  # A JSON null on the last page

    return patients[0]

def has_the_flu(social, patientid):
    problems = []
    problems_url = 'https://drchrono.com/api/problems'
    headers = {
        'Authorization': 'Bearer %s' % social.extra_data['access_token'],
        }

    while problems_url:
        data = requests.get(problems_url, headers=headers, params={'patient': patientid})

        # Check for the case of no problems
        if not data:
            break

        json_data = data.json()
        problems.extend(json_data['results'])
        problems_url = json_data['next']  # A JSON null on the last page

    for problem in problems:
        print('sgjskfbnfbksjbnf')
        print(problem['name'])
        if problem['name'] == 'Influenza (disorder)':
            return True

    return False
