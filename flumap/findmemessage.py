def findmessage(method_name):
    # Options: 'unknownlocation', 'notonmap', 'atrisk', 'notatrisk'
    return eval(method_name)

def unknownlocation():
    return 'Unfortunately your location could not be determined.'

def notonmap():
    return 'Unfortunately your location is outside this map.'

def atrisk():
    return 'Your address is close to a detected flu epicenter.'

def notatrisk():
    return 'Your address is not close to a detected flu epicenter.'
