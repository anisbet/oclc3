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

from os.path import join, dirname, exists, getsize, splitext
import re
from os import linesep

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
        self.file_path, self.file_ext = splitext(self.list_file)

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

    def get_check_list(self) -> list:
        return self._parse_('?')

    def get_done_list(self) -> list:
        return self._parse_('!')

    def get_no_change_list(self) -> list:
        return self._parse_(' ')

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

# Reads oclc.py's log file format and can return a dictionary of
# original oclc numbers (as keys), and updated OCLC numbers (as values). 
class LogDictFile:
    def __init__(self, fileName:str, debug:bool=False) -> dict:
        self.list_file = fileName
        self.debug     = debug
        if self.debug:
            print(f"DEBUG: reading {self.list_file}")
    
    def get_updated(self) -> dict:
        original_updated_numbers = {}
        ##############################################
        # Note: if the log format changes adjust here.
        ##############################################
        original_num_regex = re.compile(r'^\+\d+\s')
        updated_num_regex  = re.compile(r'(updated to)\s\d+\,')
        num_pos = len('updated to ')
        add_pos = len('+')
        with open(self.list_file, encoding='ISO-8859-1', mode='r') as log:
            line_num = 0
            for line in log:
                # Look for lines that contain 'updated to'.
                # That is the new oclc number. Example:
                # +1002030249  updated to 968312172, Record not ...
                # Should return 968312172.
                new_num_match = re.search(updated_num_regex, line)
                if not new_num_match:
                    # Quit search early, there's a lot to do.
                    continue
                new_num = new_num_match[0][num_pos:-1]
                # Look for original number submitted it looks
                # like '+nnnn...'. Example:
                # +1002030249  updated to 968312172, Record not ...
                # Should return +1002030249
                original_num_match = re.search(original_num_regex, line)
                if not original_num_match:
                    continue
                original_num = original_num_match[0][add_pos:-1]
                original_updated_numbers[f"{original_num}"] = str(new_num)
        return original_updated_numbers


# Reads various files extension type and manages the lists that it reads.
# It can read lists from .txt, .lst, .csv & .tsv (OCLC form), .flat, and
# .log, oclc.py's own log file format. 
class Lister:
    def __init__(self, fileName:str, debug:bool=False):
        self.list_file   = fileName
        self.debug       = debug
        self.list_reader = None
        # Guarding file tests.
        if not exists(self.list_file) or getsize(self.list_file) == 0:
            print(f"The {self.list_file} file is empty (or missing).")
        # Test that the class can read this type of list_file
        file_path, file_ext = splitext(self.list_file)
        if file_ext.lower() == '.csv' or file_ext.lower() == '.tsv':
            self.list_reader = OclcCsvListFile(fileName=fileName, debug=debug)
        elif file_ext.lower() == '.flat':
            self.list_reader = FlatListFile(fileName=fileName, debug=debug)
        elif file_ext.lower() == '.txt' or file_ext.lower() == '.lst' or file_ext.lower() == '':
            self.list_reader = SimpleListFile(fileName=fileName, debug=debug)
        elif file_ext.lower() == '.log':
            self.list_reader = LogDictFile(fileName=fileName, debug=debug)
        else:
            print(f"*error, file type: '{file_ext}' not supported yet.")
    
    # This method reads a file line by line and returns numbers 
    # prefixed with the appropriate instruction character.
    #    IMPORTANT: all numbers read are assumed to be for the same action!
    # Allowed list characters are '+,-, ,?,!'. 
    # param: action:str action character for each number match on a given line.
    #   For more information on reading instructions see List.read_instruction_numbers(). 
    def get_list(self, action:str) -> list:
        if not action:
            return []
        elif action == 'add':
            return self.list_reader.get_add_list()
        elif action == 'delete':
            return self.list_reader.get_delete_list()
        elif action == 'check':
            return self.list_reader.get_check_list()
        elif action == 'done':
            return self.list_reader.get_done_list()
        elif action == '':
            return self.list_reader.get_no_change_list()
        else:
            self.logger.logit(f"*unknown list type request '{action}'!")
            return []

    # Reads the transactions from a log and returns a dictionary 
    # of originally submitted oclc numbers as keys, and updated
    # OCLC numbers as values in a dictionary.  
    def get_updated_numbers(self):
        return self.list_reader.get_updated()

    # Compares two lists with '+', ' ', or '-' instructions and returns
    # a merged list. If duplicate numbers have the different instructions
    # the instruction character is replaced with a space ' ' character. 
    # If there are duplicate numbers and they are both '+' or '-', the 
    # duplicate is removed, and actions are reconciled by the following
    # algorithm: 
    # 1) '!' trumps all other rules. 
    # 2) '?' trumps any lower rule.
    # 3) Conflicting add ('+') and delete ('-') actions equates to an inaction ' ', do nothing.
    # 4) Any action ('+','-','!', or '?') over rules inaction ' '. 
    #  
    # param: list1:list of any set of oclc numbers with arbitrary instructions.
    # param: list2:list of any set of oclc numbers with arbitrary instructions.
    # return: list of instructions deduped with conflicting recociled as specified above.
    def merge(self, list1:list, list2:list) ->list:
        merged_dict = {}
        merged_list = []
        for l in [list1, list2]:
            for num in l:
                key = num[1:]
                sign= num[0]
                if sign == '!':
                    merged_dict[key] = sign
                    continue
                stored_sign = merged_dict.get(key)
                if stored_sign:
                    if stored_sign == '!':
                        continue
                    elif stored_sign == '?' or sign == '?':
                        merged_dict[key] = '?'
                    elif (stored_sign == '+' and sign == '-') or (stored_sign == '-' and sign == '+'):
                        merged_dict[key] = ' '
                    else:
                        merged_dict[key] = sign
                else:
                    merged_dict[key] = sign
        for number in sorted(merged_dict.keys()):
            sign = merged_dict[number]
            merged_list.append(f"{sign}{number}")
        return merged_list

    # Writes a list to file.
    # param: instructions:list 
    def write_instructions(self, instructions:list):
        with open(self.list_file, encoding='ISO-8859-1', mode='w') as f:
            for instruction in instructions:
                f.write(f"{instruction}" + linesep)

    # Reads instruction file. Instruction files are a series of numbers
    # one-per-line that start with '+', ' ', or '-' followed by an integer
    # which is expected to be an OCLC number.
    # param: action:str default add '+', but can be '-'.
    # return: list of integers without instruction character.  
    def read_instruction_numbers(self, action:str):
        numbers = []
        with open(self.list_file, encoding='ISO-8859-1', mode='r') as f:
            for line in f:
                if line and line.startswith(action):
                    numbers.append(line.rstrip()[1:])
        return numbers

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    doctest.testfile("listutils.tst")