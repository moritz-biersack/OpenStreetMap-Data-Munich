# -*- coding: utf-8 -*-
"""Functions for checking and correcting Munich OSM data.
Before using this module, it `init_values()` has to be used to read external
data and assing it to global variables. Afterwards, `correct_node(tag)` and
`correct_way(tag)` check a given tag and corrects it (in place), if necessary.
"""

from util import to_str
from audit_phone_no import get_clean_phone_no

MUNICH_NAMES_FILE = 'audit-mapping/munich-names.txt'
CITY_FILE = 'audit-mapping/city-names.txt'
CITY_TAG = 'addr:city'
STREET_TAG = 'addr:street'
STREET_FILE = 'audit-mapping/street-names.txt'
GOOD_MUNICH = 'München'
COUNTRY_DE = 'DE'
PHONE_TAG = 'phone'

MUNICH_NAMES = []
CITY_DICT = {}
STREET_DICT = {}



# --- Utility Functions ---
# ////////////////////////////////////////////////////////////////////

def get_key_value_of_tag(tag):
    """Return tuple with key and value of tag."""

    tag_key = to_str(tag.attrib['k'])
    tag_value = to_str(tag.attrib['v'])

    return tag_key, tag_value


def get_city_dict(city_file=CITY_FILE):
    """Return a dict including dublicate cities,
    with original city name as key and substitution name as value."""

    city_dict = {}
    with open(city_file) as f:
        for line in f:
            city_names = line.split(':')
            if len(city_names) > 1:
                city_dict[to_str(city_names[0])] = city_names[1]
    return city_dict


def get_street_names_dict(street_file=STREET_FILE):
    """Return a dict with street name map,
    including the original street name as key and substitution as value.
    """

    street_names_dict = {}
    with open(street_file) as f:
        for line in f:
            street_names = line.split(':')
            if len(street_names) > 1:
                street_names_dict[to_str(street_names[0])] = street_names[1]
    return street_names_dict



def get_munich_names(munich_file=MUNICH_NAMES_FILE):
    """Load Munich names from file."""

    munich_names = []
    with open(munich_file) as f:
        for line in f:
            munich_names.append(line.strip())
    return munich_names

# --- Checks ---
# ////////////////////////////////////////////////////////////////////


# Node related
# ------------

def is_munich_name(tag):
    """Return True if tag is city (CITY_TAG) and its value
    is one of the Munich name variants specified in MUNICH_NAMES file."""

    tag_key, city_name = get_key_value_of_tag(tag)

    return tag_key == CITY_TAG and (city_name in MUNICH_NAMES)

def is_not_germany(tag):
    """Return True if tag is country and its value is not `DE`."""

    tag_key, country = get_key_value_of_tag(tag)

    return tag_key == 'addr:country' and (country != COUNTRY_DE)

# Way related
# ------------

def is_city(tag):
    """Return True if tag is of type `addr:city`."""

    tag_key, _ = get_key_value_of_tag(tag)

    return tag_key == CITY_TAG

# Node & Way related
# ------------------

def is_street_name(tag):
    """Return True if tag is of type `addr:street`."""

    tag_key, _ = get_key_value_of_tag(tag)

    return tag_key == STREET_TAG

def is_phone_no(tag):
    """Return True if tag is phone number."""

    tag_key, _ = get_key_value_of_tag(tag)
    
    return tag_key == PHONE_TAG

# --- Correct Functions ---
# ////////////////////////////////////////////////////////////////////

# Node related
# ------------

def correct_munich_name(tag):
    """Replace the value of `tag` with the correct Munich name."""

    tag.attrib['v'] = GOOD_MUNICH
    return tag


def correct_country(tag):
    """Replace the value of `tag` with the correct German symbol."""

    tag.attrib['v'] = COUNTRY_DE
    return tag

# Way related
# ------------

def correct_city_names(tag):
    """Replace duplicate cities with uniqe city name."""

    city_dict = CITY_DICT
    city_name_og = to_str(tag.attrib['v'])
    if city_name_og in city_dict.keys():
        tag.attrib['v'] = city_dict[city_name_og]
        print 'Change City:', city_name_og, ' => ', city_dict[city_name_og]
    return tag

# Node & Way related
# ------------------

def correct_street_name(tag):
    """Check the form and spelling of street names and
    correct them, if necessary.
    """

    street_names_dict = STREET_DICT
    street_name_og = to_str(tag.attrib['v'])
    if street_name_og in street_names_dict.keys():
        tag.attrib['v'] = street_names_dict[street_name_og]
        print 'Change Street:', street_name_og, ' => ' + \
                street_names_dict[street_name_og]
    return tag

def correct_phone_no(tag):
    """Check the form of phone numbers and replace them by
    harmonized ones.
    """
    _, raw_phone_no = get_key_value_of_tag(tag)
    clean_phone_no = get_clean_phone_no(raw_phone_no)
    if clean_phone_no is not None:
        print 'Change phone#:', raw_phone_no, '=>', clean_phone_no
        tag.attrib['v'] = clean_phone_no
    else:
        print 'Bad phone# format:', raw_phone_no, 'make `phone_bad` tag'
        tag.attrib['k'] = 'phone_bad'
        tag.attrib['v'] = raw_phone_no

# --- Major correct handler ---
# ////////////////////////////////////////////////////////////////////

def correct_tag(tag, test_f, correct_f):
    """Test the tag with the test and if True
    correct the tag with the correct function.
    Return corrected tag.
    """

    if test_f(tag):
        correct_f(tag)
    return tag

def correct_node(tag):
    """Fires all checks and corrections for the given node `tag`."""

    correct_tag(tag, is_city, correct_city_names)
    correct_tag(tag, is_munich_name, correct_munich_name)
    correct_tag(tag, is_not_germany, correct_country)
    correct_tag(tag, is_street_name, correct_street_name)
    correct_tag(tag, is_phone_no, correct_phone_no)

def correct_way(tag):
    """Fires all checks and corrections for the given way `tag`."""

    correct_tag(tag, is_city, correct_city_names)
    correct_tag(tag, is_street_name, correct_street_name)
    correct_tag(tag, is_phone_no, correct_phone_no)

# --- Initialize Globals ---
# ////////////////////////////////////////////////////////////////////

def init_values():
    """Init the global variables.
    Needs to be called before other functions are used."""

    global MUNICH_NAMES
    global CITY_DICT
    global STREET_DICT

    MUNICH_NAMES = get_munich_names()
    CITY_DICT = get_city_dict()
    STREET_DICT = get_street_names_dict()
