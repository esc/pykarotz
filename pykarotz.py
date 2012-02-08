#!/usr/bin/python
import hmac
import urllib
import time
import random
import hashlib
import base64

APIKEY= 'APIKEY'
SECRET= 'SECRET'
INSTALLID = 'INSTALLID'

# sign parameters in alphabetical order
def sign(parameters, signature):
    keys = parameters.keys()
    keys.sort()
    sortedParameters = [(key, parameters[key]) for key in keys]
    query = urllib.urlencode(sortedParameters)
    digest_maker = hmac.new(signature, query, hashlib.sha1)
    signValue = base64.b64encode(digest_maker.digest())
    query = query + "&signature=" + urllib.quote(signValue)
    return query

parameters = {}
parameters['installid'] = INSTALLID
parameters['apikey'] = APIKEY
parameters['once'] = "%d" % random.randint(100000000, 99999999999)
parameters['timestamp'] = "%d" % time.time()

query = sign(parameters, SECRET)
print query

f = urllib.urlopen("http://api.karotz.com/api/karotz/start?%s" % query)
token = f.read() # should return an hex string if auth is ok, error 500 if not

