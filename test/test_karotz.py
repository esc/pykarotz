import os
import nose.tools as nt
from ConfigParser import NoSectionError, NoOptionError
import karotz as kz

BASE_PATH = "test/config_files/"

EXAMPLE_RESPONSE = """
<voosmsg>
  <id>23426660-beef-beee-baad-food0000babe</id>
  <correlationid>23426660-beef-beee-baad-food0000babe</correlationid>
  <interactiveid>23426660-beef-beee-baad-food0000babe</interactiveid>
  <response>
    <code>OK</code>
  </response>
</voosmsg>"""

DUMMY_VALUE = "23426660-beef-beee-baad-food0000babe"

def _f(filename):
    return os.path.join(BASE_PATH, filename)

def test_parse_config_good():
    settings = kz.parse_config(config_filename=_f("good_config"))
    for setting in ['apikey', 'secret', 'installid']:
        nt.assert_equal(DUMMY_VALUE, settings[setting])

def test_parse_config_bad():
    nt.assert_raises(NoSectionError,
            kz.parse_config, config_filename=_f("bad_config_no_section"))
    for i in range(1, 4):
        nt.assert_raises(NoOptionError,
                kz.parse_config,
                config_filename=_f("bad_config_no_option%i" % i))

def test_unmarshall_voomsg():
    um = kz.unmarshall_voomsg(EXAMPLE_RESPONSE)
    for field in ['id', 'correlationid', 'interactiveid']:
        nt.assert_equal(DUMMY_VALUE, um[field])
    nt.assert_equal('OK', um['code'])
