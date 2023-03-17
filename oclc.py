#!/usr/bin/env python3
###############################################################################
#
# Purpose: Update OCLC local holdings for a given library.
# Date:    Tue Jan 31 15:48:12 EST 2023
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
import os
import sys
import yaml
import argparse
import re
from lib.oclcws import OclcService

# Master list of OCLC numbers and instructions produced with --local and --remote flags.
MASTER_LIST_PATH = 'reclamation_numbers.txt'

# Find set values in a string. 
# param: line str to search. 
# return: The matching OCLC number or nothing if none found.
def _find_set_(line):
    """ 
    >>> _find_set_('12345.012 is the number you are looking for')
    >>> _find_set_('12345')
    '12345'
    >>> _find_set_('-12345')
    >>> _find_set_('+12345')
    '12345'
    >>> _find_set_(' 12345')
    >>> _find_set_('12345 is the number you are looking for')
    '12345'
    """
    regex = re.compile(r'^[+]?\d{4,14}\b(?!\.)')
    match = regex.match(line)
    if match:
        if match.group(0).startswith('+'):
            return match.group(0)[1:]
        return match.group(0)

# Find unset values in a string. 
# param: line str to search. 
# return: The matching OCLC number or nothing if no match.
def _find_unset_(line):
    """ 
    >>> _find_unset_('12345.012 is the number you are looking for')
    >>> _find_unset_('12345')
    '12345'
    >>> _find_unset_('+12345')
    >>> _find_unset_('-12345')
    '12345'
    >>> _find_unset_(' 12345')
    >>> _find_unset_('12345 is the number you are looking for')
    '12345'
    """
    regex = re.compile(r'^[-]?\d{4,14}\b(?!\.)')
    match = regex.match(line)
    if match:
        if match.group(0).startswith('-'):
            return match.group(0)[1:]
        return match.group(0)

# Read OCLC numbers from a given file. OCLC numbers must appear 
# one-per-line and can use the following syntax. OCLC numbers in lines must:
#
# * Start the line with at least 4 and at most 9 digits. 
# * May include a leading '+', '-', or ' ' and are treated as follows.
#  
# * SET: the script will ignore lines that start with ' ', '-', or any
#   non-integer value.
#  
# * UNSET: the script will ignore lines that start with ' ', '+', or any
#   non-integer value. That is, if a line starts with an integer larger than 
#   9999, the OCLC number is considered a delete record if the '--unset' 
#   switch is used.
# param: Path to the list of OCLC numbers. 
# param: Keyword (str) of either 'set' or 'unset'. 
# param: Debug bool, if you want debug information displayed. 
# return: List of OCLC numbers to be set or unset.
def _read_num_file_(num_file:str, set_unset:str, debug:bool=False):
    """
    >>> _read_num_file_('test/test.set', 'set', False)
    ['12345', '6789']
    >>> _read_num_file_('test/test.set', 'unset', False)
    ['12345', '101112']
    """
    nums = []
    # Read in a list of OCLC numbers to set.
    with open(num_file, encoding='utf8', mode='r') as f:
        for line in f:
            if set_unset == 'set':
                num = _find_set_(line.rstrip())
                if num:
                    nums.append(num)
            elif set_unset == 'unset':
                num = _find_unset_(line.rstrip())
                if num:
                    nums.append(num)
            else: # neither 'set' nor 'unset'
                sys.stderr.write(f"*error, invalid or missing 'set_unset' value: '{set_unset}'!")
                break
    f.close()
    if debug:
        print(f"Found {len(nums)} OCLC numbers to {set_unset} in file '{num_file}'.")
        print(f"The first 3 numbers read are: {nums[:3]}...")
    return nums

# Adds or sets the institutional holdings.
# param: oclc number list of holdings to set.
# param: config_yaml string path to the YAML file, containing connection and authentication for 
#   a given server.
# return: TODO: TBD
# def _update_holdings_(oclc_numbers:list, config_yaml:str, debug:bool=False):
#     # Create a web service object. 
#     ws = OclcService(config_yaml, debug)
#     count = 0
#     while oclc_numbers:
#         start_length = len(oclc_numbers)
#         # TODO: handle results via the oclc report.
#         ws.set_holdings(oclc_numbers)
#         batch_count = start_length - len(oclc_numbers)
#         count += batch_count
#         print(f"batched {batch_count} records...")
#     print(f"processed {count} total records.")

# Given two lists, compute which numbers OCLC needs to add (or set), which they need to delete (unset)
# and which need no change.
# param:  List of oclc numbers to delete or unset.
# param:  List of oclc numbers to set or add. 
def _diff_(del_nums:list, add_nums:list) -> list:
    """
    >>> u = []
    >>> s = [2,3,4]
    >>> M = _diff_(u, s)
    >>> print(M)
    ['+2', '+3', '+4']
    >>> u = [1,2,3]
    >>> s = []
    >>> M = _diff_(u, s)
    >>> print(M)
    ['-1', '-2', '-3']
    >>> r = [1,2,3]
    >>> l = [2,3,4]
    >>> M = _diff_(r, l)
    >>> print(M)
    ['-1', ' 2', ' 3', '+4']
    """
    # Store uniq nums and sign.
    ret_dict = {}
    for oclcnum in del_nums:
        if oclcnum in add_nums:
            ret_dict[oclcnum] = " "
        else:
            ret_dict[oclcnum] = "-"
    for libnum in add_nums:
        if libnum in del_nums:
            ret_dict[libnum] = " "
        else:
            ret_dict[libnum] = "+"
    ret_list = []
    for (num, sign) in ret_dict.items():
        ret_list.append(f"{sign}{num}")
    return ret_list


# Main entry to the application if not testing.
def main(argv):

    parser = argparse.ArgumentParser(
        prog = 'oclc',
        usage='%(prog)s [options]' ,
        description='Maintains holdings in OCLC WorldCat Search.',
        epilog='See "-h" for help more information.'
    )
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('-s', '--set', action='store', metavar='[/foo/bar.txt]', help='OCLC numbers to add or set in WorldCat.')
    parser.add_argument('-u', '--unset', action='store', metavar='[/foo/bar.txt]', help='OCLC numbers to delete from WorldCat.')
    parser.add_argument('-r', '--remote', action='store', metavar='[/foo/remote.lst]', help='Remote (OCLC) numbers list from WorldCat holdings report.')
    parser.add_argument('-l', '--local', action='store', metavar='[/foo/local.lst]', help='Local OCLC numbers list collected from the library\'s ILS.')
    parser.add_argument('-x', '--xml_records', action='store', help='file of MARC21 XML catalog records to submit as special local holdings.')
    parser.add_argument('-d', '--debug', action='store_true', help='turn on debugging.')
    parser.add_argument('-y', '--yaml', action='store', metavar='[/foo/test.yaml]', required=True, help='alternate YAML file for testing. Default oclc.yaml')
    args = parser.parse_args()
    
    # Load configuration.
    if args.yaml and os.path.isfile(args.yaml) == False:
        sys.stderr.write(f"*error, required (YAML) configuration file not found! No such file: '{args.yaml}'.\n")
        sys.exit()
    
    if args.debug:
        print(f"debug: '{args.debug}'")
        print(f"yaml: '{args.yaml}'")
        print(f"set: '{args.set}'")
        print(f"unset: '{args.unset}'")
        print(f"local: '{args.local}'")
        print(f"remote: '{args.remote}'")
        print(f"xml records: '{args.xml_records}'")

    # Two lists, one for adding holdings and one for deleting holdings. 
    set_holdings   = []
    unset_holdings = []
    # Add records to institution's holdings.
    if args.set:
        if args.debug:
            print(f"Running set.")
        if os.path.isfile(args.set):
            set_holdings.clear()
            set_holdings = _read_num_file_(args.set, 'set', args.debug)
        else:
            sys.stderr.write(f"*error, 'set' requires file of oclc numbers but file '{args.set}' was not found.\n")
            sys.exit()


    # delete records from institutional holdings.
    if args.unset:
        if args.debug:
            print(f"Running unset")
        if os.path.isfile(args.unset):
            unset_holdings.clear()
            unset_holdings = _read_num_file_(args.unset, 'unset', args.debug)
        else:
            sys.stderr.write(f"*error, no such file: '{args.unset}'.\n")
            sys.exit()


    # Upload XML MARC21 records.
    if args.xml_records:
        if args.debug:
            print(f"Running XML MARC file upload.")
        if os.path.isfile(args.xml_records):
            pass
        else:
            sys.stderr.write(f"*error, no XML record file called '{args.xml_records}' was found!\n")
            sys.exit()
    
    # Reclamation report that is both files must exist and be read.
    if args.local and args.remote:
        # Read the list of local holdings. See Readme.md for more information on how
        # to collect OCLC numbers from the ILS.
        if args.debug:
            print(f"Reading local holdings list.")
        if os.path.isfile(args.local):
            set_holdings.clear()
            set_holdings = _read_num_file_(args.local, 'set', args.debug)
        else:
            sys.stderr.write(f"*error, local file list missing or empty ({args.local}).\n")
            sys.exit()
        # Read the report of remote holdings (holdings at OCLC)
        if args.debug:
            print(f"Reading remote holdings list from OCLC report.")
        if os.path.isfile(args.remote):
            unset_holdings.clear()
            unset_holdings = _read_num_file_(args.remote, 'unset', args.debug)
        else:
            sys.stderr.write(f"*error, remote file list missing or empty ({args.remote}).\n")
            sys.exit()

    
    # Create a 'master' list that indicates with are to be removed 
    # and which are to be added, then exit. The script can then be re-run
    # using the same file for both the '--set' and '--unset' flags to run
    # the master. Check the list first before beginning.
    master_list = _diff_(unset_holdings, set_holdings)
    with open(MASTER_LIST_PATH, encoding='utf8', mode='w') as f:
        for holding in master_list:
            if args.debug:
                print(f"{holding}")
            f.write(f"{holding}\n")
    f.close()

    if os.path.exists(MASTER_LIST_PATH) and os.path.getsize(MASTER_LIST_PATH) > 0:
        if args.debug:
            print(f"check {MASTER_LIST_PATH} for OCLC numbers and processing instructions.")
        with open(MASTER_LIST_PATH, encoding='utf-8', mode='r') as f:
            temp = f.readlines()
        f.close()
        set_holdings.clear()
        unset_holdings.clear()
        for number in temp:
            number = number.rstrip()
            print(f"DEBUG:>> {number}")
            if number.startswith('+'):
                set_holdings.append(number[1:])
            elif number.startswith('-'):
                unset_holdings.append(number[1:])
            else:
                continue
        print(f"DEBUG: ADD == {set_holdings}")
        print(f"DEBUG: DEL == {unset_holdings}")
    else:
        print(f"Nothing to do.")

if __name__ == "__main__":
    import doctest
    # Pass tests to run.
    if doctest.testmod():
        main(sys.argv[1:])
# EOF