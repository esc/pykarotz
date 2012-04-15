#!/usr/bin/env python

""" pykarotz - Python interface to Karotz """

import os
import hmac
import urllib
import time
import random
import hashlib
import base64
import lxml.etree as le
import ConfigParser

__version__ = "0.1.0-dev"
__author__ = "Valentin 'esc' Haenel <valentin.haenel@gmx.de>"
__docformat__ = "restructuredtext en"

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

ENGLISH = "EN"
GERMAN  = "DE"
FRENCH  = "FR"
SPANISH = "ES"

LANGUAGES = [ENGLISH, GERMAN, FRENCH, SPANISH]

SETTINGS = ['apikey', 'secret', 'installid']

def signed_rest_call(function, parameters, secret):
    query = urllib.urlencode(sorted(parameters.items()))
    digest_maker = hmac.new(secret, query, hashlib.sha1)
    sign_value = base64.b64encode(digest_maker.digest())
    parameters['signature'] = sign_value
    return assemble_rest_call(function, parameters)

def assemble_rest_call(function, parameters):
    """ Create a URL suitable for making a REST call to api.karotz.com.

    Parameters
    ----------
    function : str
        the api function to execute
    parameters : dict
        the parameters to use in the call

    Returns
    -------
    url : str
        an ready make url

    """
    query = urllib.urlencode(sorted(parameters.items()))
    return "%s%s?%s" % (BASE_URL, function, query)

def rest_call(function, parameters):
    """ Make a rest call.

    Will assemble the url and make the call. Does not return anything, but
    raises KarotzResponseError if the call was not OK or no response is
    received.

    Parameters
    ----------
    function : str
        the api function to execute
    parameters : dict
        the parameters to use in the call

    Raises
    ------
    KarotzResponseError
        if the call was unsucessful

    """
    file_like = urllib.urlopen(assemble_rest_call(function, parameters))
    unmarshall_voomsg(file_like.read())

def unmarshall_start_voomsg(token):
    parsed = le.fromstring(token)
    im = parsed.find("interactiveMode")
    if im is not None:
        unmarshalled = {"interactiveId": im.find("interactiveId").text,
                        "access": [element.text
                            for element in im.findall("access")]}
        return unmarshalled
    else:
        # something went wrong
        resp = parsed.find("response")
        if resp.find("code").text == 'ERROR':
            raise KarotzResponseError(
                    "Recived an 'ERROR' response, the full message was: \n%s"
                    % le.tostring(parsed, pretty_print=True))
        else:
            raise KarotzResponseError("Recived an unkonwen response:\n%s" %
                    le.tostring(parsed, pretty_print=True))

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
    if unmarshalled['code'] != 'OK':
        raise KarotzResponseError(
                "Recived an non 'OK' response, the full message was: \n%s"
                % le.tostring(parsed, pretty_print=True))
    for field in ['id', 'correlationId', 'interactiveId']:
        unmarshalled[field] = parsed.find(field).text
    return unmarshalled

def parse_config(section='karotz-app-settings', config_filename=None):
    """ Parse a configuration file with app settings.

    Parameters
    ----------
    section : str
        the name of the config section where to look for settings
        (default: 'karotz-app-settings')
    config_filename : str
        the path to and name of the config file

    Returns
    -------
    settings : dict
        the settings, values for 'apikey', 'secret' and 'installid'

    Raises
    ------
    IOError:
        if config_filename does not exist
    NoSectionError
        if no section with name 'section' exists
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
            for setting in SETTINGS)


class KarotzResponseError(Exception):
    pass


class Karotz(object):
    """ The main class of pykarotz

    Parameters
    ----------
    settings : dict (None)
        the settings, values for 'apikey', 'secret' and 'installid'
        if None, the default config file will be searched
    start : boolean
        if True, start() will be called from the constructor

    Attributes
    ----------
    settings : dict
        the settings, values for 'apikey', 'secret' and 'installid'
    interactiveId : str
        the interactiveId, when connected
    access : list of str
        the functions that the installed application has access to

    Examples
    --------
    >>> krtz = Karotz()
    >>> krtz.demo_led()

    """

    def __init__(self, settings=None, start=True):
        # if no settings given, search in the default location
        if settings is None:
            settings = parse_config()
        for setting in SETTINGS:
            assert setting in settings
        self.settings = settings
        self.interactiveId = None
        self.access = None
        if start:
            self.start()

    def __del__(self):
        if self.interactiveId:
            self.stop()

    def start(self):
        parameters = {'apikey':    self.settings['apikey'],
                      'installid': self.settings['installid'],
                      'once':      str(random.randint(100000000, 99999999999)),
                      'timestamp': str(int(time.time()))}
        file_like = urllib.urlopen(signed_rest_call('start',
                                   parameters,
                                   self.settings['secret']))
        # should return an hex string if auth is ok, error 500 if not
        unmarshalled = unmarshall_start_voomsg(file_like.read())
        self.interactiveId = unmarshalled["interactiveId"]
        self.access = unmarshalled["access"]

    def stop(self):
        rest_call('interactivemode', {'action': 'stop',
                                      'interactiveid': self.interactiveId})
        self.interactiveId = None

    def restart(self):
        self.stop()
        self.start()

    def ears(self, left=0, right=0, relative=True, reset=False):
        rest_call('ears', {'left': left,
                           'right' : right,
                           'relative' : relative,
                           'reset' : reset,
                           'interactiveid': self.interactiveId})

    def reset_ears(self):
        self.ears(reset=True)

    def sad(self):
        self.ears(left=5, right=5, relative=False)

    def spin_ca(self):
        self.ears(left=-17, right=17)

    def spin_ac(self):
        self.ears(left=17, right=-17)

    def happy(self):
        self.ears(left=-2, right=-2, relative=False)

    def led_pulse(self, color=RED, period=500, pulse=3000):
        rest_call('led', {'action': 'pulse',
                          'color': color,
                          'period': period,
                          'pulse': pulse,
                          'interactiveid': self.interactiveId})

    def led_fade(self, color=RED, period=3000):
        rest_call('led', {'action': 'fade',
                          'color': color,
                          'period': period,
                          'interactiveid': self.interactiveId})

    def led_light(self, color=RED):
        rest_call('led', {'action': 'light',
                          'color': color,
                          'interactiveid': self.interactiveId})

    def led_off(self):
        self.led_light(color=OFF)

    def tts(self, action='speak', text="", lang=ENGLISH):
        rest_call('tts', {'action': action,
                          'lang': lang,
                          'text': text,
                          'interactiveid': self.interactiveId})

    def say(self, text, lang=ENGLISH):
        self.tts(text=text, lang=lang)

    def mute(self):
        self.tts(action='stop')

    def demo_led(self):
        for color in COLORS:
            self.led_light(color=color)
            time.sleep(1)
