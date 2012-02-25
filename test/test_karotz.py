import os
import nose.tools as nt
from ConfigParser import NoSectionError, NoOptionError
import karotz as kz

BASE_PATH = "test/config_files/"

EXAMPLE_RESPONSE = """
<VoosMsg>
    <id>23426660-beef-beee-baad-food0000babe</id>
    <correlationId>23426660-beef-beee-baad-food0000babe</correlationId>
    <interactiveId>23426660-beef-beee-baad-food0000babe</interactiveId>
    <callback></callback>
    <response>
        <code>OK</code>
    </response>
</VoosMsg>
"""

EXAMPLE_START_OK = """
<VoosMsg>
    <id>23426660-beef-beee-baad-food0000babe</id>
    <recipient>23426660beefbeeebaadfood0000babe</recipient>
    <interactiveMode>
        <action>START</action>
        <interactiveId>23426660-beef-beee-baad-food0000babe</interactiveId>
        <configId>23426660-beef-beee-baad-food0000babe</configId>
        <access>ears</access>
        <access>led</access>
        <access>multimedia</access>
        <access>tts</access>
    </interactiveMode>
</VoosMsg> """

EXAMPLE_START_ERROR = """
<VoosMsg>
    <id>23426660-beef-beee-baad-food0000babe</id>
    <correlationId>23426660-beef-beee-baad-food0000babe</correlationId>
    <response>
        <code>ERROR</code>
    </response>
</VoosMsg> """

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
    for field in ['id', 'correlationId', 'interactiveId']:
        nt.assert_equal(DUMMY_VALUE, um[field])
    nt.assert_equal('OK', um['code'])
    nt.assert_raises(kz.KarotzResponseError, kz.unmarshall_voomsg, None)

def test_unmarshall_start_voomsg():
    um = kz.unmarshall_start_voomsg(EXAMPLE_START_OK)
    nt.assert_equal(DUMMY_VALUE, um["interactiveId"])
    nt.assert_equal(['ears', 'led', 'multimedia', 'tts'], um["access"])

