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



# sign parameters in alphabetical order
def sign(parameters, signature):
    query = urllib.urlencode(sorted(parameters.items()))
    digest_maker = hmac.new(signature, query, hashlib.sha1)
    signValue = base64.b64encode(digest_maker.digest())
    query = query + "&signature=" + urllib.quote(signValue)
    return query

def parse_config(config_filename=None):
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
    section = 'karotz-app-settings'
    return dict((setting, cp.get(section, setting))
            for setting in ['apikey', 'secret', 'installid'])


class Karotz(object):

    def __init__(self, settings):
        self.__dict__.update(settings)

    def start(self):
        parameters = {'apikey': self.apikey, 'installid': self.installid}
        parameters['once'] = "%d" % random.randint(100000000, 99999999999)
        parameters['timestamp'] = "%d" % time.time()
        query = sign(parameters, self.secret)
        f = urllib.urlopen("http://api.karotz.com/api/karotz/start?%s" % query)
        # should return an hex string if auth is ok, error 500 if not
        token = f.read()
        parsed = le.fromstring(token)
        self.interactiveId = parsed.find("interactiveMode").find("interactiveId").text
