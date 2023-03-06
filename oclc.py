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

# TODO: Define workflow for comparing OCLC numbers at a library against OCLC holdings.
# TODO: Manage authentication. See oclcws.py for more information.

def _read_yaml_(yaml_file:str):
    """
    >>> c = _read_yaml_('oclc.yaml')
    >>> print(c['OCLC']['institutionalSymbol'])
    CNEDM
    """
    if os.path.isfile(yaml_file) == False:
        sys.stderr.write(f"**error, no such YAML file '{yaml_file}'.\n")
        sys.exit()
    with open(yaml_file, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

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
    >>> _read_num_file_('test.set', 'set', False)
    ['12345', '6789']
    >>> _read_num_file_('test.set', 'unset', False)
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
# param: config dictionary read from the YAML file, containing connection and authentication for 
#   a given server.
# return: TODO: TBD
def _set_holdings_(oclc_nums_path:str, config:dict, debug:bool=False):
    oclc_numbers = _read_num_file_(oclc_nums_path, 'set', debug)
    if debug:
        print(f"Read {len(oclc_numbers)} OCLC numbers from file '{oclc_nums_path}'.")
        print(f"The first 3 numbers to set are: {oclc_numbers[:3]}")
    # Create a web service object. 
    ws = OclcService(configs=config)


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
    parser.add_argument('-x', '--xml_records', action='store', help='file of MARC21 XML catalog records to submit as special local holdings.')
    parser.add_argument('-t', '--test', action='store_true', help='use test mode and test server settings in YAML.')
    parser.add_argument('-d', '--debug', action='store_true', help='turn on debugging.')
    parser.add_argument('-y', '--yaml', action='store', metavar='[/foo/bar.yaml]', default='oclc.yaml', help='alternate YAML file for configuration. Default epl.yaml')
    args = parser.parse_args()
    

    # End of arg parsing, set and check variables.
    if args.test == False:
        server = 'Production'
    else:
        server = 'Test'
    # Load configuration.
    if args.yaml and os.path.isfile(args.yaml) == False:
        sys.stderr.write(f"*error, required (YAML) configuration file not found! No such file: '{args.yaml}'.\n")
        sys.exit()
    config = _read_yaml_(args.yaml)[server]
    if args.debug:
        print(f"debug: '{args.debug}'")
        print(f"test: '{args.test}'")
        print(f"config: '{config['name']}'")
        print(f"set: '{args.set}'")
        print(f"unset: '{args.unset}'")
        print(f"xml records: '{args.xml_records}'")


    # Add records to institution's holdings.
    if args.set and os.path.isfile(args.set):
        _set_holdings_(args.set, config)
    else:
        sys.stderr.write(f"*error, 'set' requires file of oclc numbers but file '{args.set}' was not found.\n")
        sys.exit()


    # delete records from institutional holdings.
    if args.unset and os.path.isfile(args.unset):
        pass
    else:
        sys.stderr.write(f"*error, no such file: '{args.unset}'.\n")
        sys.exit()


    # Upload XML MARC21 records.
    if args.xml_records and os.path.isfile(args.xml_records):
        pass
    else:
        sys.stderr.write(f"*error, no XML record file called '{args.xml_records}' was found!\n")
        sys.exit()
    

if __name__ == "__main__":
    import doctest
    doctest.testmod()
else:
    main(sys.argv[1:])
# EOF