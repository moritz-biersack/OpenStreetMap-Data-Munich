# -*- coding: utf-8 -*-
"""Clean OSM data and save it to CSV files for database import.

Source code by Udacity (Data Analyst Nanodegree - P3: Wrangle OpenStreetMap Data)
Adapted by Moritz Biersack for 'OpenStreetMap Data Munich'
"""

import sys
import csv
import codecs
import re
import xml.etree.cElementTree as ET

import cerberus

import schema
import check_correct as CC

NODES_PATH = "csv/nodes.csv"
NODE_TAGS_PATH = "csv/nodes_tags.csv"
WAYS_PATH = "csv/ways.csv"
WAY_NODES_PATH = "csv/ways_nodes.csv"
WAY_TAGS_PATH = "csv/ways_tags.csv"

PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%# $@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the
# sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset',
               'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def iter_tags(element, tags, problem_chars, element_tag_type):
    for tag in element.iter("tag"):
        tag_key = tag.attrib['k']

        if problem_chars.search(tag_key):
            continue

        # cleaning
        if element_tag_type == "node":
            CC.correct_node(tag)
        if element_tag_type == "way":
            CC.correct_way(tag)

        # update tag key 
        tag_key = tag.attrib['k']

        # default tag type
        tag_type = 'regular'

        # tag type for values including colon(s)
        s = tag_key.split(':')
        if len(s) > 1:
            # includes colon
            tag_key = ':'.join(s[1:])
            tag_type = s[0]

        tags.append({
            'key': tag_key,
            'id': element.attrib['id'],
            'value': tag.attrib['v'],
            'type': tag_type
            })

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  #  Handle secondary tags the same way for both node and way elements

    #  YOUR CODE HERE
    if element.tag == "node":
        #  node attributes
        for key, value in element.attrib.iteritems():
            if key in node_attr_fields:
                node_attribs[key] = value

        #  node children tags
        iter_tags(element, tags, problem_chars, "node")

        r_node = {'node': node_attribs, 'node_tags': tags}
        return r_node

    elif element.tag == 'way':
        #  way attributs
        for key, value in element.attrib.iteritems():
            if key in way_attr_fields:
                way_attribs[key] = value

        #  way children tags
        iter_tags(element, tags, problem_chars, "way")

        #  way children nd elements
        for i, nd in enumerate(element.iter("nd")):
            way_nodes.append({
                'id': element.attrib['id'],
                'node_id': nd.attrib['ref'],
                'position': i
                })
        
        r_way = {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
        return r_way


#  ================================================== # 
#                Helper Functions                     # 
#  ================================================== # 
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_strings = (
            "{0}: {1}".format(k, v if isinstance(v, str) else ", ".join(v))
            for k, v in errors.iteritems()
        )
        raise cerberus.ValidationError(
            message_string.format(field, "\n".join(error_strings))
        )


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


#  ================================================== #
#                Main Function                        #
#  ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    CC.init_values()

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    # pass
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    #  Note: Validation is ~ 10X slower. For the project consider using a small
    #  sample of the map when validating.

    if len(sys.argv) is not 2:
        print 'Error! Please provide filname as argument'
    else:
        process_map(sys.argv[1], validate=False)
