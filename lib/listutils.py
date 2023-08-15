###############################################################################
#
# Purpose: Provide wrappers reading, comparing, and writing lists from and
#   to file.
# Date:    Tue 15 Aug 2023 02:34:18 PM EDT
# Copyright 2023 Andrew Nisbet
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###############################################################################

import os.path as path
import re

# Reads simple lists of integers of which the first in the line are added to 
# a list.
# Examples of valid lines:
# +123456 Treasure Isl... # The record 123456 will be added when '--set' is used.
# 123456 Treasure Isla... # Added when using '--set' and deleted if using `--unset`.
# -7756632                # Delete this record if '--unset' is used.
# 7756632                 # Deleted if '--unset' is used, added if using '--set' or `--local`.
#  654321 any text        # This will be ignored in all cases.
# (OCoLC)7756632  blah    # Set or unset the number '7756632' depending on flag.
# -(OCoLC)7756632  blah   # Unset number '7756632' if '--unset' is used, ignored otherwise.
# (OCoLC)7756632  blah    # Set or unset the number '7756632' depending on switch.
# ?(OCoLC)7756632  blah   # Check number '7756632'.
# Random text on a line   # Ignored.
class SimpleListFile:
    def __init__(self, fileName:str, debug:bool=False):
        self.list_file = fileName
        self.debug     = debug
        if self.debug:
            print(f"DEBUG: reading {self.list_file}")
        # Test that the class can read this type of list_file
        self.file_path, self.file_ext = path.splitext(self.list_file)

    # Reads and parses the input file returning a list of a given 'type'.
    # Valid types are 'add' and 'del' list. The list is returned with the
    # appropriate instruction prefix '+' for adds and '-' for deletes. 
    def _parse_(self, which:str=' ') -> list:
        # In the most basic parser type read a file of integers one per line.
        numbers = []
        num_matcher  = re.compile(r'\d+')
        with open(self.list_file, encoding='ISO-8859-1', mode='r') as lf:
            for line in lf:
                num_match = re.search(num_matcher, line)
                if num_match:
                    numbers.append(f"{which}{num_match[0]}")
        return numbers

    def get_add_list(self) -> list:
        return self._parse_('+')

    def get_delete_list(self) -> list:
        return self._parse_('-')

# Reads lines from a CSV report from OCLC which requires special parsing.
# Example:
# =HYPERLINK("http://www.worldcat.org/oclc/1834", "1834")	Book, Print	Juvenile ...
class OclcCsvListFile(SimpleListFile):
    def __init__(self, fileName:str, debug:bool=False):
        super().__init__(fileName, debug=debug)

    def _parse_(self, which:str='-') -> list:
        # In the most basic parser type read a file of integers one per line.
        numbers = []
        num_matcher  = re.compile(r'"\d+"')
        with open(self.list_file, encoding='ISO-8859-1', mode='r') as lf:
            for line in lf:
                num_match = re.search(num_matcher, line)
                if num_match:
                    # Trim off the double-quotes
                    number = num_match[0][1:-1]
                    numbers.append(f"{which}{number}")
        return numbers

# Parses Symphony FLAT files returning a list of values from 035 OCLC tags.
# Example:
# *** DOCUMENT BOUNDARY ***
# FORM=MUSIC               
# .000. |ajm7i0n a         
# .001. |aon1347755731     
# .596.   |a1
# .035.   |a(OCoLC)769428891|z(OCoLC)1011913436|z(OCoLC)1014370726|z(OCoLC)1016090501
# .035.   |a(Sirsi) 111111111
# .250.   |aOn-order so don't send to OCLC.
# .035.   |a(EPL)on1347755731 
# Parses the number '769428891'
class FlatListFile(SimpleListFile):
    def __init__(self, fileName:str, debug:bool=False):
        super().__init__(fileName, debug=debug)

    # Returns all OCLC numbers from each bib record in the flat file - even if the 
    # record contains multiple OCLC numbers.
    def _parse_(self, which:str='+') -> list:
        # Reads flat files line by line and extracts the .035. with the OCoLC number.
        numbers = []
        number_start_pos = len('|a(OCoLC)')
        num_matcher  = re.compile(r'\|a\(OCoLC\)\d+')
        with open(self.list_file, encoding='ISO-8859-1', mode='r') as lf:
            for line in lf:
                num_match = re.search(num_matcher, line)
                if num_match:
                    # Trim off the double-quotes
                    number = num_match[0][number_start_pos:]
                    numbers.append(f"{which}{number}")
        return numbers

# Determines what type of file reader to use. Reads and parses
# the file and manages the list of numbers.
class Lister:
    def __init__(self, fileName:str, debug:bool=False):
        self.list_file   = fileName
        self.debug       = debug
        self.list_reader = None
        # Test that the class can read this type of list_file
        file_path, file_ext = path.splitext(self.list_file)
        if file_ext.lower() == '.csv' or file_ext.lower() == '.tsv':
            self.list_reader = OclcCsvListFile(fileName=fileName, debug=debug)
        elif file_ext.lower() == '.flat':
            self.list_reader = FlatListFile(fileName=fileName, debug=debug)
        elif file_ext.lower() == '.txt' or file_ext.lower() == '.lst' or file_ext.lower() == '':
            self.list_reader = SimpleListFile(fileName=fileName, debug=debug)
        else:
            print(f"*error, file type: '{file_ext}' not supported yet.")

    def get_list(self, action:str) -> list:
        if not action:
            return []
        if action == 'add':
            return self.list_reader.get_add_list()
        if action == 'delete':
            return self.list_reader.get_delete_list()

    # Compares two lists with '+', ' ', or '-' instructions and returns
    # a merged list. If duplicate numbers have the different instructions
    # the instruction character is replaced with a space ' ' character. 
    # If there are duplicate numbers and they are both '+' or '-', the 
    # duplicate is removed.
    # param: list1:list of either adds, deletes, or even a mixture of both or ' '.
    # param: list2:list of either adds, deletes, or even a mixture of both or ' '.
    # return: list of instructions deduped with conflicting instructions set to ' '.
    def merge(self, list1:list, list2:list) ->list:
        merged_dict = {}
        merged_list = []
        for num in list1:
            key = num[1:]
            sign= num[0]
            # print(f"sign={sign}, num={key}")
            if merged_dict.get(key):
                # The number is here but has a different sign. 
                if merged_dict[key] == ' ':
                    merged_dict[key] = sign
                elif merged_dict[key] != sign:
                    merged_dict[key] = ' '
            else:
                merged_dict[key] = sign
        for num in list2:
            key = num[1:]
            sign= num[0]
            if merged_dict.get(key):
                if merged_dict[key] == ' ':
                    merged_dict[key] = sign
                elif merged_dict[key] != sign:
                    merged_dict[key] = ' '
            else:
                merged_dict[key] = sign
        for number in sorted(merged_dict.keys()):
            sign = merged_dict[number]
            merged_list.append(f"{sign}{number}")
        return merged_list

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    doctest.testfile("listutils.tst")