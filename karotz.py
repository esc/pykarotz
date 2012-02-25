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

OFF    = "000000"
BLUE   = "0000FF"
CYAN   = "00FF9F"
GREEN  = "00FF00"
ORANGE = "FFA500"
PINK   = "FFCFAF"
PURPLE = "9F00FF"
RED    = "FF0000"
YELLOW = "75FF00"
WHITE  = "4FFF68"

COLORS = [OFF, BLUE, CYAN, GREEN,
          ORANGE, PINK, PURPLE, RED,
          YELLOW, WHITE]

def signed_rest_call(function, parameters, signature):
    query = urllib.urlencode(sorted(parameters.items()))
    digest_maker = hmac.new(signature, query, hashlib.sha1)
    sign_value = base64.b64encode(digest_maker.digest())
    parameters['signature'] = sign_value
    return assemble_rest_call(function, parameters)

def assemble_rest_call(function, parameters):
    query = urllib.urlencode(sorted(parameters.items()))
    return "%s%s?%s" % (BASE_URL, function, query)

def rest_call(function, parameters):
    file_like = urllib.urlopen(assemble_rest_call(function, parameters))
    token = file_like.read()
    unmarshall_voomsg(token)

def unmarshall_start_voomsg(token):
    parsed = le.fromstring(token)
    im = parsed.find("interactiveMode")
    if im is not None:
        unmarshalled = {"interactiveId": im.find("interactiveId").text,
               "access": [element.text
                    for element in
                    im.findall("access")]
                }
        return unmarshalled
    else:
        # something went wrong
        resp = parsed.find("response")
        if resp.find("code").text == 'ERROR':
            raise KarotzResponseError(
                    "Recived an 'ERROR' response, the full message was: \n%s"
                    % le.tostring(parsed, pretty_print=True))
        else:
            raise KarotzResponseError("Recived an unkonwen response:\n%s" % token)

def unmarshall_voomsg(token):
    """ Unmarshall a standard VooMsg

    Parameters
    ----------

    token : xml string
        the returned token from the REST call

    Returns
    -------
    unmarshalled : dict
        dictionary containing 'code', 'id' 'correlationId' and 'interactiveId'

    Notes
    -----
    Unfortunately the Karotz REST API does not return a proper errormessage in
    case you make a wrong call, but instead None. In this case this function
    raises a 'KarotzResponseError'.

    """
    if token is None:
        raise KarotzResponseError(
                "Rest call returned 'None', probably an error.")
    parsed = le.fromstring(token)
    unmarshalled = {'code': parsed.find("response").find("code").text}
    for field in ['id', 'correlationId', 'interactiveId']:
        unmarshalled[field] = parsed.find(field).text
    return unmarshalled

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

    def __del__(self):
        self.stop()

    def start(self):
        parameters = {'apikey': self.apikey, 'installid': self.installid}
        parameters['once'] = "%d" % random.randint(100000000, 99999999999)
        parameters['timestamp'] = "%d" % time.time()
        file_like = urllib.urlopen(signed_rest_call('start', parameters, self.secret))
        # should return an hex string if auth is ok, error 500 if not
        unmarshalled = unmarshall_start_voomsg(file_like.read())
        self.interactiveid = unmarshalled["interactiveId"]
        self.access = unmarshalled["access"]

    def stop(self):
        parameters = {'action': 'stop', 'interactiveid': self.interactiveId}
        rest_call('interactivemode', parameters)
        self.interactiveId = None

    def ears(self, left=0, right=0, relative=True, reset=False):
        parameters = locals().copy()
        del parameters['self']
        parameters['interactiveid'] = self.interactiveId
        rest_call('ears', parameters)

    def reset_ears(self):
        self.ears(reset=True)

    def sad(self):
        self.ears(left=23 ,right=23, relative=False)

    def led_light(self, color='FFFFFF'):
        parameters = {'action': 'light',
                      'color': color,
                      'interactiveid': self.interactiveId}
        rest_call('led', parameters)

    def demo_led(self):
        for color in COLORS:
            self.led_light(color=color)
            time.sleep(1)
        self.led_light(color=PINK)
