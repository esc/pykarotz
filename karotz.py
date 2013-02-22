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
from lxml import objectify

__version__ = "0.2.0"
__author__ = "Valentin 'esc' Haenel <valentin.haenel@gmx.de> - Franck Roudet"
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
    proxies : dict (None)
        dict for proxies (see urllib.open)

    Attributes
    ----------
    settings : dict
        the settings, values for 'apikey', 'secret' and 'installid'
    interactive_id : str
        the interactive_id, when connected, None when not
    access : list of str
        the functions that the installed application has access to

    Examples
    --------
    >>> krtz = Karotz()
    >>> krtz.led.demo()

    """

    def __init__(self, settings=None, start=True, proxies=None):
        # if no settings given, search in the default location
        if settings is None:
            settings = parse_config()
        for setting in SETTINGS:
            assert setting in settings
        self.settings = settings
        self.proxies=proxies
        self.interactive_id = None
        self.access = None
        self.ears = Karotz.Ears(self)
        self.led = Karotz.Led(self)
        self.tts = Karotz.TTS(self)
        self.config = Karotz.Config(self)
        self.webcam = Karotz.Webcam(self)
        self.multimedia = Karotz.Multimedia(self)
        if start:
            self.start()

    def __del__(self):
        self._rest_call('interactivemode', {'action': 'stop'})

    def _basic_rest_call(self, function, parameters):
        """ Make a rest call.

        Will assemble the url and make the call. Return hte body

        Parameters
        ----------
        function : str
            the api function to execute
        parameters : dict
            the parameters to use in the call

        """
        parameters['interactiveid'] = self.interactive_id
        file_like = urllib.urlopen(assemble_rest_call(function, parameters), proxies=self.proxies)
        return file_like.read()
    
    def _rest_call(self, function, parameters):
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

        Returns
        -------
        unmarshalled : dict
            dictionary containing 'code', 'id' 'correlationId' and 'interactiveId'

        Raises
        ------
        KarotzResponseError
            if the call was unsucessful

        """
        file_like = self._basic_rest_call(function, parameters)
        return unmarshall_voomsg(file_like)

    class Ears(object):
        """ Karotz' ears.

        Parameters
        ----------
        _karotz : Karotz
            a karotz instance

        """
        def __init__(self, _karotz):
            self._karotz = _karotz

        def __call__(self, left=0, right=0, relative=True, reset=False):
            return self._karotz._rest_call('ears',
                    {'left': left,
                    'right' : right,
                    'relative' : relative,
                    'reset' : reset,
                    })
        def move(self, left=0, right=0, relative=True):
            """ Move the ears.

            Parameters
            ----------
            left : int
                number of slots to move left ear
            right : int
                number of slots to move right ear
            relative : bool
                is movement to be relative to current position
            """
            return self(left=left, right=right, relative=relative)

        def reset(self):
            """ Reset the ears to the base position. """
            return self(reset=True)

        def sad(self):
            """ Ears down. """
            return self(left=5, right=5, relative=False)

        def happy(self):
            """ Ears up. """
            return self(left=-2, right=-2, relative=False)

        def spin_ca(self):
            """ Spin left ear clockwise, right ear anticlockwise. """
            return self(left=-17, right=17)

			
        def spin_ac(self):
            """ Spin left ear anticlockwise, right ear anticlockwise. """
            return self(left=17, right=-17)

    class Led(object):
        """ Karotz' led.

        Parameters
        ----------
        _karotz : Karotz
            a karotz instance

        """
        def __init__(self, _karotz):
            self._karotz = _karotz

        def __call__(self, action='light', color=RED, period=500, pulse=3000):
            return self._karotz._rest_call('led',
                    {'action': action,
                    'color': color,
                    'period': period,
                    'pulse': pulse,
                    })

        def pulse(self, color=RED, period=500, pulse=3000):
            """ Pulse the led.

            Will pulse the led from current color to target color and back
            again.

            Parameters
            ----------
            color : string
                hex color, like karotz.COLORS
            period : int
                half a period in ms
            pulse : int
                the total duration in ms
            """
            return self(action='pulse', color=color, period=period, pulse=pulse)

        def fade(self, color=RED, period=3000):
            """ Fade the led.

            Will fade the led from current color to target color.

            Parameters
            ----------
            color : string
                hex color, like karotz.COLORS
            period : int
                time to fade
            """
            return self(action='fade', color=color, period=period)

        def light(self, color=RED):
            """ Set the led to a given color.

            Will fade the led from current color to target color.

            Parameters
            ----------
            color : string
                hex color, like karotz.COLORS
            """
            return self(action='light', color=color)

        def off(self):
            """ Turn the led off. """
            return self(color=OFF)

        def demo(self):
            """ Fade through the available colors. """
            period=5000
            for color in COLORS:
                self.fade(color=color, period=period)
                time.sleep(period/1000)

    class TTS(object):
        """ Karotz' text to speech (tts).

        Parameters
        ----------
        _karotz : Karotz
            a karotz instance

        """
        def __init__(self, _karotz):
            self._karotz = _karotz

        def __call__(self, action='speak', text="", lang=ENGLISH):
            return self._karotz._rest_call('tts',
                    {'action': action,
                    'lang': lang,
                    'text': text,
                    })

        def speak(self, text, lang=ENGLISH):
            """ Say something.

            Parameters
            ----------
            text : string
                the text to say
            lang : str
                the language to use, one of kz.LANGUAGES
            """
            return self(text=text, lang=lang)

        def stop(self):
            """ Interrupt the currently spoken words. """
            return self(action='stop')

    class Config(object):
        """ Karotz' config.

        Parameters
        ----------
        _karotz : Karotz
            a karotz instance

        """
        def __init__(self, _karotz):
            self._karotz = _karotz

        def __call__(self):
            """ Karotz' Config.
    
            Returns
            -------
              An object (lxml) that is the karotz configuration
    
            """
            res = self._karotz._basic_rest_call('config', {})
            return objectify.fromstring(res)
            

    class Webcam(object):
        """ Karotz' Webcam.

        Parameters
        ----------
        _karotz : Karotz
            a karotz instance

        """
        def __init__(self, _karotz):
            self._karotz = _karotz

        def video(self):
            """ Get the video stream.

            Returns
            -------
                the url of the video stream
            """

            parameters = { 'interactiveid' :self._karotz.interactive_id, 'action': 'video' }
            return assemble_rest_call('webcam', parameters)


    class Multimedia(object):
        """ Karotz' Multemdia.

        Parameters
        ----------
        _karotz : Karotz
            a karotz instance

        """
        def __init__(self, _karotz):
            self._karotz = _karotz

        def __call__(self, action, ):
            return self._karotz._rest_call('multimedia',
                    {'action': action,
                     })
            
        def play(self,url):
            """ Play multimedia.

            Parameters
            ----------
                url : Media to play (mp3?)
            """
            return self._karotz._rest_call('multimedia',
                    {'action': 'play',
                     'url' : url,
                    })

        def pause(self):
            """ Pause media.

            """
            return self('pause')

        def resume(self):
            """ Resume media.

            """
            return self('resume')

        def stop(self):
            """ Resume media.

            """
            return self('stop')

    def start(self):
        print "start..."
        parameters = {'apikey':    self.settings['apikey'],
                      'installid': self.settings['installid'],
                      'once':      str(random.randint(100000000, 99999999999)),
                      'timestamp': "%d" % time.time()}
        file_like = urllib.urlopen(signed_rest_call('start',
                                   parameters,
                                   self.settings['secret']),proxies=self.proxies)
        # should return an hex string if auth is ok, error 500 if not
        res=file_like.read()
        unmarshalled = unmarshall_start_voomsg(res)
        self.interactive_id = unmarshalled["interactiveId"]
        self.access = unmarshalled["access"]

    def stop(self):
        if self.interactive_id:
            self._rest_call('interactivemode', {'action': 'stop'})
            self.interactive_id = None

    def restart(self):
        self.stop()
        self.start()

