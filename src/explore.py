# -*- coding: utf-8 -*-
"""Explore OSM data in an interactive shell.

Takes an OSM file name as first argument and either 'way' or 'node' as second.
After looping through the data, the most common tag keys and their values are
printed. These can be explored further by entering the tag key of interest.
"""

import sys
import xml.etree.cElementTree as ET

from collections import defaultdict


from util import to_str

def is_tag_type(elem, tag_type):
    """Return true if element is of type `tag_type`."""

    return elem.tag == tag_type


def audit(filename, tag_type='way'):
    """Process the file and do checks."""

    iterator = ET.iterparse(filename)
    tag_types = defaultdict(list)

    # iterate over all elements in tree
    sys.stderr.write("Audit tags of type `" + tag_type + "`\n")
    for _, elem in iterator:
        # check if it is a way element
        if is_tag_type(elem, tag_type):
            # go through the child elements of way element
            # add tag value to new or existing key in `tag_types`
            for tag in elem.iter('tag'):
                tag_types[to_str(tag.attrib['k'])].append(to_str(tag.attrib['v']))

    sys.stderr.write("This are all tag types used 5+ times:\n")
    for tag in sorted(tag_types,
                      key=lambda tag: len(tag_types[tag]),
                      reverse=True):
        if len(tag_types[tag]) > 5:
            sys.stderr.write(str(len(tag_types[tag])) + "\t" + tag + "\n")
    sys.stderr.write("\n---\n")

    return tag_types

def get_unique_values_and_count(values):
    """Take a list of values and return a dict with
    unique values and their count in the original list
    """
    unique_values = defaultdict(int)
    for value in values:
        unique_values[value] += 1
    return unique_values

def print_tag_values_and_counts(tag_values_unique, tag_key, limit=None):
    """Print tag values with appropriate count.
    Takes the dictionary with unique tag values, the `tag_key` of interest
    and an optional `limit` that defines the maximum number of printed values.
    """

    # get tag values of interest
    tag_values = tag_values_unique[tag_key]

    # loop the tag values, sorted by their count and limit if applicable
    for tag_value in sorted(tag_values,
                            key=tag_values.get,
                            reverse=True)[:limit]:
        try:
            # print tag value count, tab char and tag value
            print tag_values[tag_value], '\t', tag_value
        except UnicodeEncodeError:
            continue

def audit_unique_tags(tag_values_unique):
    """Interactive shell for exploring tags and their values in detail.
    Asks the user to specify a tag and displays the appropriate values
    with their count.
    """

    while True:
        # get tag type of user
        sys.stderr.write("\nEnter tag type or `.q` for quit\n")
        user_input = raw_input()

        if user_input == ".q":
            sys.stderr.write("Quiting...\n")
            break

        try:
            tag_values_unique[user_input]
        except KeyError:
            sys.stderr.write("Tag not found: " + user_input + "\n")
        else:
            # entered tag exists, print its values
            sys.stderr.write("Here are the values of " + user_input + ":\n---\n")
            print_tag_values_and_counts(tag_values_unique, user_input)

def audit_tags(tag_types):
    """ Analyze and print info about tags.

    Takes `tag_types` dict which consists of tag names as keys,
    mapping to a list of tag-values."""

    # Dict of tags and their corresponding total appereance (count)
    tag_count = {}
    # Dict of tags and their unique values
    tag_values_unique = {}

    # loop all tags and their values
    for tag, values in tag_types.iteritems():
        # store the count for the tag
        tag_count[tag] = len(values)

        # unique values for the tag
        tag_values_unique[tag] = get_unique_values_and_count(values)

    # Tags sorted by their count (greatest last)
    # plus count of their unique values
    for tag in sorted(tag_count, key=tag_count.get, reverse=True)[:10]:
        # Tag name, count, unique values
        print '---'
        print 'Tag Name:\t', tag
        print 'Count:\t\t', tag_count[tag]
        print 'Unique:\t\t', len(tag_values_unique[tag])
        print '\n-'

        print_tag_values_and_counts(tag_values_unique, tag, 20)

    audit_unique_tags(tag_values_unique)


def print_tag_types(tag_types):
    """Print all tag types."""

    for key in sorted(tag_types, key=tag_types.get):
        print key, ':', tag_types[key]

if __name__ == "__main__":
    #print_tag_types(audit(sys.argv[1]))
    if len(sys.argv) is not 3:
        print 'Error! Please provide filename and tag type as argument!'
    else:
        audit_tags(audit(sys.argv[1], sys.argv[2]))
