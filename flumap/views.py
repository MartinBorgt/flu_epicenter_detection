from django.shortcuts import render, redirect
from experiment import load, generate, infect, mixturegaussian, findme
import findmemessage
# Create your views here.

def index(request):
    return render(request, 'flumap/home.html')


def contact(request):

    return render(request, 'flumap/basic.html', {'information':
                 ['If you would like to contact me, please email me at martin.borgt at gmail.com or see any of the links at the bottom.']})



def flumap(request, functioncalled = None):
    template = 'flumap/flumap.html'
    if not request.session.get('has_session'):
        request.session['has_session'] = True
    sessionkey = request.session.session_key

    if functioncalled is None:
        return render(request, template, {'image_names': [('A map of San Jose', 'San_Jose_map.bmp')]})

    # Check if the function is a planned one
    if not functioncalled in ['load', 'generate', 'infect', 'mixturegaussian', 'findme']:
        return redirect('/flumap/flumap/')

    # Repeated if statements is not the most glamorous way to go over all functions, but its nice for addition and
    # deletion of arguments
    if functioncalled == 'load':
        load(sessionkey)
        return render(request, template, {'image_names':
                    [('Each dot represents the location of a patient, blue indicates no flu, red indicates flu',
                      'San_Jose_map-{}.tif'.format(sessionkey))]})

    elif functioncalled == 'generate':
        generate(sessionkey)
        return render(request, template, {'image_names':
                    [('Each blue dot represents the location of a patient', 'San_Jose_map-{}.tif'.format(sessionkey))]})
    elif functioncalled == 'infect':
        infect(sessionkey)
        return render(request, template, {'image_names': [('Each red dot represents the location of an ill patient', 'San_Jose_map-infected-{}.tif'.format(sessionkey))]})
    elif functioncalled == 'mixturegaussian':
        mixturegaussian(sessionkey)
        return render(request, template, {'image_names': [('The generated input distribution', 'generated_contour-{}.png'.format(sessionkey)),
                        ('The distribution found in the data', 'result_contour-{}.png'.format(sessionkey))]})
    elif functioncalled == 'findme':
        value = findme()
        message = findmemessage.findmessage(value)
        return render(request, template, {'image_names':
                    [], 'findme': message})


    #experiment.map_with_patients(request.session.session_key)
    return render(request, template, {'image_names': [('A map of San Jose', 'San_Jose_map.bmp')]})
