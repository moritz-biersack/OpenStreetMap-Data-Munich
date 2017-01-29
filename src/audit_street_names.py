# -*- coding: utf-8 -*-
"""Check, if street names are well formed, print bad ones.

Takes an OSM file name as argument and loops over both ways and nodes.
Each element of type `addr:street` (`is_street_name`) is compared to a
regular expression. Bad values are stored in the `street_types` array
and printed in the end.
"""

import sys

import re
import xml.etree.cElementTree as ET

from util import to_str

def is_street_name(elem):
    """Return true if element is of street type."""

    return elem.attrib['k'] == 'addr:street'


def audit_street_name(street_types, street_name):
    """Check if street name is a well formed street name.

    Takes an array `street_types` to store bad formed strings.
    `street_names` is the string which is checked.
    """

    # regex including well formed street name patterns
    regex = (r'stra[sß]+e$|weg$|platz$|gasse$|ring$|allee$|anger$|bogen$' +
             r'|promenade$|^a[nm][-\s]|^i[nm][-\s]|^zu[rm]?[-\s]' +
             r'|^platz[-\s]|^untere?r?|feld$|hof$|brücke$|garten$|höhe$|insel$')
    result = re.compile(regex, re.IGNORECASE).search(street_name)

    if not result and street_name not in street_types:
        # the regex didn't match the streetname
        # -> save it as bad one
        street_types.append(street_name)


def is_tag_type(elem, tag_type):
    """Return true if element is of type `tag_type`."""

    return elem.tag == tag_type


def audit(filename):
    """Process the file and do checks.
    Return an array with bad street names.
    """

    iterator = ET.iterparse(filename)
    street_types = []

    # iterate over all elements in tree
    sys.stderr.write("Audit street names:\n\n")
    for _, elem in iterator:
        # check if it is either a way or node element
        if is_tag_type(elem, 'way') or is_tag_type(elem, 'node'):
            # go through the child elements of the element
            for tag in elem.iter('tag'):
                if is_street_name(tag):
                    # audit the tag
                    audit_street_name(street_types, to_str(tag.attrib['v']))

    return street_types

if __name__ == '__main__':
    if len(sys.argv) is not 2:
        print 'Error! Please provide filename as argument!'
    else:
        for value in audit(sys.argv[1]):
            print value
