# Copyright (C) 2016 Open Tech Strategies, LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# This script takes an XML file generated by the CPD utility of PMD (see
# github.com/pmd/pmd) and relative path to the directory that CPD was
# run on.  It returns a list of duplicated files, sorted by their degree
# of similarity.
# 
# Ultimately it may also return a list of duplicated classes
# 
# Usage example:
# 
# $ python sort-duplicates.py <xml file to parse> <path to coeci-cms-mpsp tree, not including coeci-cms-mpsp>
#

import xml.etree.ElementTree as Tree
import sys


# with thanks to:
# http://stackoverflow.com/questions/845058/how-to-get-line-count-cheaply-in-python
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

# Takes a set of pre-parsed elements from an xml file and returns a list
# of lists.  Each list contains the relevant parts of each element:
# - number of lines duplicated
# - number of lines in first file
# - abbreviated path to first file
# - number of lines in second file
# - abbreviated path to second file
def find_filesizes(root):
    filesizes_array = []
    
    # for each `duplication` block in the xml file:
    for duplicate in root:
        # find the filenames
        filepath1 = duplicate._children[0].attrib['path']
        # TBD: Chop off the first part, up to "coeci-cms-mpsp." This is
        # an artifact of my particular CPD-generated XML file, so others
        # might not need to do this split.
        filepath1 = filepath1.split('../../../')[1]
        filepath2 = duplicate._children[1].attrib['path']
        filepath2 = filepath2.split('../../../')[1]
        # get the number of lines of each file
        # TBD: include relative path to the file
        filesize1 = file_len(filepath1)
        filesize2 = file_len(filepath2)
        # get the size of the duplication ("lines")
        dupe_size = duplicate.attrib['lines']
        filesizes_array.append([dupe_size, filesize1, filepath1, filesize2, filepath2])

    return filesizes_array


# Returns an array that consists of:
#  - percentage of lines of file 1 duplicated
#  - name of file 1
#  - percentage of lines of file 2 duplicated
#  - name of file 2
def percentage_duplicated(size_array):
    percent_array = []
    for arr in size_array:
        dupe = int(arr[0])
        percent1 = round(dupe/arr[1], 2)
        percent2 = round(dupe/arr[3], 2)
        percent_array.append([percent1, arr[2], percent2, arr[4]])

    return percent_array



# Returns a list of filename pairs, with their percentage duplicated,
# sorted from highest duplicate percentage to lowest (for the first file
# of the pair).
def sort_files(percent_array):
    # Thanks to https://wiki.python.org/moin/HowTo/Sorting
    sorted_array = sorted(percent_array, key=lambda array: array[0]) 
    return sorted_array



# Parses command line arguments (an XML file and a path to the top-level
# dir where the files referenced in that XML file reside), and returns a
# sorted list of the most-heavily-duplicated files.
def main(sys):
    if sys.argv[1]:
        tree = Tree.parse(sys.argv[1])
        root = tree.getroot()
        print("TESTING: okay, got root")
    else:
        print("Please provide the xml file.")
        return

    array_of_sizes = find_filesizes(root)
    print("TESTING: made the array of sizes")
    # 4. compare the size of the file(s) to the size of the duplication
    array_of_percents = percentage_duplicated(array_of_sizes)
    
    # 5. sort output based on the result of that comparison
    file_list = sort_files(array_of_percents)
    
    print(file_list)
    return file_list

main(sys)
