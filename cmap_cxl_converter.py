##
#
# cmap_cxl_converter.py
# Convert those cxl files to a consumable format
#
# Copyright 2016 Josh Pelkey
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing permissions and limitations under the
# License.
#
##

import glob
import itertools
import os
import re

# choose directory where cmap txt files are located
cmap_directory = './cmaps_test'

# get the files
files = glob.glob (cmap_directory + '/*.cxl')

# iterate over all the files and start doing stuffs
for cxl_file in files:
    # open a cmap text file and begin writing results
    f = open (cxl_file)

    # print the file name
    print os.path.basename(cxl_file)

    # get the concepts, linking phrases, and connections
    concepts = {}
    linking_phrases = {}
    connections = []
    for line in f:
        if "concept id=" in line:
            concept = re.findall (r'"([^"]*)"', line)
            concepts[concept[0]] = concept[1]

        # get the linking phrases
        if "linking-phrase id=" in line:
            linking_phrase = re.findall (r'"([^"]*)"', line)
            linking_phrases[linking_phrase[0]] = linking_phrase[1]

        # get the connections
        if "connection id=" in line:
            connections.append (re.findall (r'"([^"]*)"', line))

    # cycle through the linking phrase list, find all lines matching from-id and to-id
    # edges are combinations of from-id and to-id
    concepts_linked = []
    for key in linking_phrases:
        from_links = []
        to_links = []
        for connection in connections:
            # if linking phrase is in the from-id (linking phrase at beginning)
            if key == connection[1]:
                from_links.append ([linking_phrases[key],concepts[connection[2]]])
            # if linking phrase is in the to-id (linking phrase at the end)
            if key == connection[2]:
                to_links.append ([concepts[connection[1]], linking_phrases[key]])
        print to_links
        print from_links
        print "--"

        # now combine the lists, to_links to from_links
        for to_link in to_links:
            for  from_link in from_links:
                concepts_linked.append ([to_link[0], to_link[1], from_link[1]])

    for item in concepts_linked:
        print item


    print concepts.values ()
