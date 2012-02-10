import os
import nose.tools as nt
from ConfigParser import NoSectionError, NoOptionError
import karotz as kz

BASE_PATH = "test/config_files/"

def _f(filename):
    return os.path.join(BASE_PATH, filename)

def test_parse_config_good():
    dummy_value = "23426660-beef-beee-baad-food0000babe"
    settings = kz.parse_config(config_filename=_f("good_config"))
    for setting in ['apikey', 'secret', 'installid']:
        nt.assert_equal(dummy_value, settings[setting])

def test_parse_config_bad():
    nt.assert_raises(NoSectionError,
            kz.parse_config, config_filename=_f("bad_config_no_section"))
    for i in range(1, 4):
        nt.assert_raises(NoOptionError,
                kz.parse_config,
                config_filename=_f("bad_config_no_option%i" % i))
