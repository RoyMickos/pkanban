import urllib, urlparse, logging, base64

"""parseResponse
Creates a dictionary out of data included in Django request objects. uses urlparse to create an
initial dictionary, which is unwrapped from lists if it has only one memeber
"""
def parseRequest(request):
    log = logging.getLogger('pkanban.application')
    dude = request.read()
    #log.debug('read: ' + dude)
    receivedData = urlparse.parse_qs(urllib.unquote(dude), True)
    for key,value in receivedData.iteritems():
        #log.debug('key:   ' + key)
        # turn arrays of lengt 1 to variables
        if isinstance(value, type(list())):
            if len(value) == 1:
                receivedData[key] = value[0]
        #print key + ' ' + receivedData[key]
        if key in ['description', 'name']:
            receivedData[key] = base64.urlsafe_b64decode(receivedData[key])
        #log.debug('value: ' + str(value))
        #log.debug('encoded: ' + receivedData[key])
    return receivedData

def encodeDescription(description):
    return base64.urlsafe_b64encode(description.encode('utf-8'))