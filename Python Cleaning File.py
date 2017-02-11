# -*- coding: utf-8 -*-
"""
Created on Sun Jan 01 17:56:29 2017

@author: Simon Tong
"""

import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow
from collections import defaultdict
import re
import pprint

OSM_FILE = "Sheepshead Bay.osm"  # Replace this with your osm file
SAMPLE_FILE = "sample.osm"

k = 10 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')
    
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
street_type_re_ave = re.compile(r'^\b\S+\.?', re.IGNORECASE) #Regular Expression for first word in string
#Count Tags from Udacity Exercise
def count_tags(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    dic = {root.tag : 1}
    for child in root:
        for branch in child:
            tag = branch.tag
            if tag in dic:
                dic[tag] += 1
            else:
                dic[tag] = 1
        leaf = child.tag
        if leaf in dic:
            dic[leaf] += 1
        else:
            dic[leaf] = 1
    return dic
    
print count_tags('Sheepshead Bay.osm')
#Expected(Common) Street Types
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Highway","Terrace","Path","Walk"]
#Return unexpected street types and the corresponding streets
def audit_street_type(street_types, street_name):
    if len(street_name.split(' ')[-1]) == 1:
        m = street_type_re_ave.search(street_name)
    else:
        m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:            
            street_types[street_type].add(street_name)
#For Bike Racks, streets are listed under cityracks.street as well            
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street" or elem.attrib['k'] == "cityracks.street")
#Zipcode is listed under tiger data as well
def is_zip(elem):
    return elem.get('k') == 'addr:postcode' or elem.get('k') == 'tiger:zip_left' or elem.get('k') == 'tiger:zip_right'
#Audit Streets function from Udacity Exercise
def auditStreet(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types
#Count types of Amenity
def auditAmenity(osmfile):
    osm_file = open(osmfile, "r")
    amenity_types = {}
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.get('k') == 'amenity':
                    aType = tag.get('v')
                    if aType in amenity_types:
                        amenity_types[aType] += 1
                    else:
                        amenity_types[aType] = 1
    osm_file.close()
    return amenity_types
print auditStreet('Sheepshead Bay.osm')
print auditAmenity('Sheepshead Bay.osm')
#Audit Restaurants and Fast Food joints and explore what data is given
def auditFood(osmfile):
    osm_file = open(osmfile, "r")
    amenity_types = {}
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.get('v') == 'restaurant' or tag.get('v') == 'fast_food':
                    for tag1 in elem.iter("tag"):
                        print tag1.attrib
    osm_file.close()
auditFood('Sheepshead Bay.osm')
#Audit Zipcodes to check for consistency and accuracy (Within Sheepshead Bay?)
def auditZip(osmfile):
    osm_file = open(osmfile, "r")
    zipcodes = {}
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_zip(tag):
                    zType = tag.get('v')
                    if zType in zipcodes:
                        zipcodes[zType] += 1
                    else:
                        zipcodes[zType] = 1
    osm_file.close()
    return zipcodes
print auditZip('Sheepshead Bay.osm')

mapping = {"St": "Street",
           "avenue": "Avenue",
           "Rd": "Road",
           "Av": "Avenue",
           "Ave": "Avenue",
            }
#Update the name for streets, including streets that start with street type and end with letter (e.g. Avenue U)
def update_name(name, mapping):
    if len(name.split(' ')[-1]) == 1:
        old = street_type_re_ave.search(name).group()
        if old in mapping:
            new = mapping[street_type_re_ave.search(name).group()]
            name = name.replace(old, new)
        return name
    else:
        old = street_type_re.search(name).group()
        if old in mapping:
            new = mapping[street_type_re.search(name).group()]
            name = name.replace(old, new)
        return name

#Update Zipcodes that have too many digits
def update_zip(name):
    if len(name) != 5:
        name = name[:5]
    return name

import csv
import codecs

import cerberus

import schema1

OSM_PATH = "Sheepshead Bay.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\, \t\r\n]')


SCHEMA = schema1.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # Shape elements that do not have problem characters and split on : and .(for cityracks)
    #Update street and zip
    if element.tag == 'node':
        for x in node_attr_fields:
            node_attribs[x] = element.get(x)
        for tag in element.iter('tag'):
            tagdic = {}
            keyval = tag.get('k')
            if PROBLEMCHARS.search(keyval):
                continue
            else:
                if ':' in keyval:
                    klist = keyval.split(':', 1 )
                    tagdic['type'] = klist[0]
                    tagdic['key'] = klist[1]
                elif '.' in keyval:
                    klist = keyval.split('.', 1 )
                    tagdic['type'] = klist[0]
                    tagdic['key'] = klist[1]
                else:
                    tagdic['type'] = 'regular'
                    tagdic['key'] = keyval
                tagdic['id'] = element.get('id')
                val = tag.get('v')
                if is_street_name(tag):
                    val = update_name(val, mapping)
                elif is_zip(tag):
                    val = update_zip(val)
                tagdic['value'] = val
            tags.append(tagdic)
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        for y in way_attr_fields:
            way_attribs[y] = element.get(y)
        for tag in element.iter('tag'):
            tagdic = {'id': element.get('id')}
            keyval = tag.get('k')
            if PROBLEMCHARS.search(keyval):
                continue
            else:
                if ':' in keyval:
                    klist = keyval.split(':', 1 )
                    tagdic['type'] = klist[0]
                    tagdic['key'] = klist[1]
                elif '.' in keyval:
                    klist = keyval.split('.', 1 )
                    tagdic['type'] = klist[0]
                    tagdic['key'] = klist[1]
                else:
                    tagdic['type'] = 'regular'
                    tagdic['key'] = keyval
                tagdic['id'] = element.get('id')
                val = tag.get('v')
                if is_street_name(tag):
                    val = update_name(val, mapping)
                elif is_zip(tag):
                    val = update_zip(val)
                tagdic['value'] = val
            tags.append(tagdic)
        count = 0
        for nd in element.iter('nd'):
            ndic = {'id' : element.get('id')}
            ndic['node_id'] = nd.get('ref')
            ndic['position'] = count
            count += 1
            way_nodes.append(ndic)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
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
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

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
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)
