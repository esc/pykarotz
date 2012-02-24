#!/usr/bin/python
import os
import hmac
import urllib
import time
import random
import hashlib
import base64
import lxml.etree as le
import ConfigParser

BASE_URL = 'http://api.karotz.com/api/karotz/'

def signed_rest_call(function, parameters, signature):
    query = urllib.urlencode(sorted(parameters.items()))
    digest_maker = hmac.new(signature, query, hashlib.sha1)
    sign_value = base64.b64encode(digest_maker.digest())
    parameters['signature'] = sign_value
    return rest_call(function, parameters)

def rest_call(function, parameters):
    query = urllib.urlencode(sorted(parameters.items()))
    return "%s%s?%s" % (BASE_URL, function, query)

def parse_voomsg(message):
    parsed = le.fromstring(message)
    code = parsed.find("response").find("code").text
    if code == 'OK':
        pass
    elif code == 'ERROR':
        raise KarotzResponseError("Recived an 'ERROR' response.")
    else:
        raise Exception("Unknowen response code: %s" % code)

def unmarshall_voomsg(message):
    parsed = le.fromstring(message)
    um = {}
    for field in ['id', 'correlationid', 'interactiveid']:
        um[field] = parsed.find(field).text
    um['code'] = parsed.find("response").find("code").text
    return um

def parse_config(section="karotz-app-settings", config_filename=None):
    """ Parse a configuration file with app settings.

    Parameters
    ----------
    config_filename : str
        the name of the config file

    Returns
    -------
    settings : dict
        the settings, values for 'apikey', 'secret' and 'installid'

    Raises
    ------
    IOError:
        if config_filename does not exist
    NoSectionError
        if no section 'karotz-app-settings' exists
    NoOptionError
        if any one of 'apikey', 'secret' and 'installid' does not exist

    """
    # use the config file if none given
    if not config_filename:
        config_filename = os.path.expanduser("~/.pykarotz")
    # parse the config
    cp = ConfigParser.RawConfigParser()
    with open(config_filename) as fp:
        cp.readfp(fp)
    # convert to dict and return
    # doing it this way, will raise exceptions if the section or option doesn't
    # exist
    return dict((setting, cp.get(section, setting))
            for setting in ['apikey', 'secret', 'installid'])


class KarotzResponseError(Exception):
    pass


class Karotz(object):

    def __init__(self, settings=None, start=True):
        # if no settings given, search in the default location
        if settings is None:
            settings = parse_config()
        # this will set self.apikey, self.installid, and self.secret
        self.__dict__.update(settings)
        self.interactiveId = None
        if start:
            self.start()

    def start(self):
        parameters = {'apikey': self.apikey, 'installid': self.installid}
        parameters['once'] = "%d" % random.randint(100000000, 99999999999)
        parameters['timestamp'] = "%d" % time.time()
        f = urllib.urlopen(signed_rest_call('start', parameters, self.secret))
        # should return an hex string if auth is ok, error 500 if not
        token = f.read()
        parsed = le.fromstring(token)
        im = parsed.find("interactiveMode")
        if im is not None:
            # all is good
            self.interactiveId = im.find("interactiveId").text
        else:
            # something went wrong
            resp = parsed.find("response")
            if resp.find("code").text == 'ERROR':
                raise KarotzResponseError(
                        "Recived an 'ERROR' response, the full message was: \n%s"
                        % le.tostring(parsed, pretty_print=True))
            else:
                raise KarotzResponseError("Recived an unkonwen response:\n%s" % token)

    def stop(self):
        parameters = {'action': 'stop', 'interactiveid': self.interactiveId}
        f = urllib.urlopen(rest_call('interactivemode', parameters))
        token = f.read()
        parse_voomsg(token)
        self.interactiveId = None

    def ears(self, left=0, right=0, relative=True, reset=False):
        parameters = locals().copy()
        del parameters['self']
        parameters['interactiveid'] = self.interactiveId
        f = urllib.urlopen(rest_call('ears', parameters))
        #token = f.read()
        #parse_voomsg(token)

    def reset_ears(self):
        self.ears(reset=True)

    def led_light(self, color='FFFFFF'):
        parameters = {'action': 'light',
                      'color': color,
                      'interactiveid': self.interactiveId}
        f = urllib.urlopen(rest_call('led', parameters))
