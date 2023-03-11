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
    with open(num_file, encoding='utf8') as f:
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
        print(f"numbers read from {num_file}:")
        print(f"numbers start -> {nums}")
    return nums

# Adds or sets the institutional holdings.
# param: oclc_nums_file path string to the list of OCLC numbers to add as institutional holdings.
# param: config_yaml string path to the YAML file, containing connection and authentication for 
#   a given server.
# return: TODO: TBD
def _set_holdings_(oclc_nums_path:str, config_yaml:str, debug:bool=False):
    oclc_numbers = _read_num_file_(oclc_nums_path, 'set', debug)
    if debug:
        print(f"Read {len(oclc_numbers)} OCLC numbers from file '{oclc_nums_path}'.")
        print(f"The first 3 numbers to set are: {oclc_numbers[:3]}...")
    # Create a web service object. 
    ws = OclcService(config_yaml)
    remaining_list = []
    while oclc_numbers:
        ws.set_holdings(oclcNumbers)

# Given two lists, compute which numbers OCLC needs to add (or set), which they need to delete (unset)
# and which need no change.
# param:  oclcnum_file path to OCLC numbers they have on record. 
# param:  librarynums_file path to list of numbers library has.
def _diff_(remote_nums:list, local_nums:list) -> list:
    """
    >>> r = [1,2,3]
    >>> l = [2,3,4]
    >>> R = _diff_(r, l)
    >>> print(R)
    ['-1', ' 2', ' 3', '+4']
    """
    # Store uniq nums and sign.
    ret_dict = {}
    for oclcnum in remote_nums:
        if oclcnum in local_nums:
            ret_dict[oclcnum] = " "
        else:
            ret_dict[oclcnum] = "-"
    for libnum in local_nums:
        if libnum in remote_nums:
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
    parser.add_argument('-y', '--yaml', action='store', metavar='[/foo/test.yaml]', default='oclc.yaml', help='alternate YAML file for testing. Default oclc.yaml')
    args = parser.parse_args()
    
    # Load configuration.
    if args.yaml and os.path.isfile(args.yaml) == False:
        sys.stderr.write(f"*error, required (YAML) configuration file not found! No such file: '{args.yaml}'.\n")
        sys.exit()
    config_yaml = args.yaml
    if args.debug:
        print(f"debug: '{args.debug}'")
        print(f"config_yaml: '{config_yaml}'")
        print(f"set: '{args.set}'")
        print(f"unset: '{args.unset}'")
        print(f"local: '{args.local}'")
        print(f"remote: '{args.remote}'")
        print(f"xml records: '{args.xml_records}'")


    # Add records to institution's holdings.
    if args.set:
        if os.path.isfile(args.set):
            _set_holdings_(args.set, config_yaml)
        else:
            sys.stderr.write(f"*error, 'set' requires file of oclc numbers but file '{args.set}' was not found.\n")
            sys.exit()


    # delete records from institutional holdings.
    if args.unset:
        if os.path.isfile(args.unset):
            pass
        else:
            sys.stderr.write(f"*error, no such file: '{args.unset}'.\n")
            sys.exit()


    # Upload XML MARC21 records.
    if args.xml_records:
        if os.path.isfile(args.xml_records):
            pass
        else:
            sys.stderr.write(f"*error, no XML record file called '{args.xml_records}' was found!\n")
            sys.exit()
    
    # Reclamation report
    local_holdings = []
    remote_holdings= []
    if args.local and os.path.isfile(args.local):
        # read the local file with _find_set_().
        local_holdings = _read_num_file_(args.local, 'set', True)
    else:
        sys.stderr.write(f"*error, local file list missing or empty ({args.local}).\n")
        sys.exit()
    if args.remote and os.path.isfile(args.remote):
        # read the remote file with _find_set_().
        remote_holdings = _read_num_file_(args.remote, 'unset', True)
    else:
        sys.stderr.write(f"*error, remote file list missing or empty ({args.remote}).\n")
        sys.exit()
    if local_holdings and remote_holdings:
        reclamation_list = _diff_(remote_holdings, local_holdings)
        with open('reclamation.lst', encoding='utf8') as f:
            for holding in reclamation_list:
                print(f"{holding}")
                f.write(f"{holding}")
        f.close()
    else:
        sys.stderr.write(f"*error, both local or remote lists required, but not supplied:\n")
        sys.stderr.write(f"*error, local list: ({args.local}), remote list: ({args.remote}).\n")
        sys.exit()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    main(sys.argv[1:])
# EOF