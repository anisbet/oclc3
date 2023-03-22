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
from lib.oclcreport import OclcReport

# Master list of OCLC numbers and instructions produced with --local and --remote flags.
MASTER_LIST_PATH = 'master.lst'
TEST = True
# Find set values in a string. 
# param: line str to search. 
# return: The matching OCLC number or nothing if none found.
def _find_set_(line):
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
    regex = re.compile(r'^[-]?\d{4,14}\b(?!\.)')
    match = regex.match(line)
    if match:
        if match.group(0).startswith('-'):
            return match.group(0)[1:]
        return match.group(0)

# Find oclc numbers that need checking. 
# param: line str from OCLC number list file. 
# return: The matching OCLC number or nothing if no match.
def _find_check_(line):
    regex = re.compile(r'^[?]?\d{4,14}\b(?!\.)')
    match = regex.match(line)
    if match:
        if match.group(0).startswith('?'):
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
def _read_num_file_(num_file:str, set_unset:str, debug:bool=False) ->list:
    nums = []
    if debug:
        print(f"Running {set_unset}")
    if not os.path.isfile(num_file):
        sys.stderr.write(f"*error, no such file: '{num_file}'.\n")
        return nums

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
            elif set_unset == 'check':
                num = _find_check_(line.rstrip())
                if num:
                    nums.append(num)
            else: # neither 'set', 'check', nor 'unset'
                sys.stderr.write(f"*error, invalid parameter: '{set_unset}'!")
                break
    f.close()
    if debug:
        print(f"Found {len(nums)} OCLC numbers to {set_unset} in file '{num_file}'.")
        print(f"The first 3 numbers read are: {nums[:3]}...")
    return nums

# Write out the master list. Do not append, delete if exists.
# param: path string of the master list. Default 'master.lst'.
# param: list of oclc numbers to write to the master file. The 
#   list will consist of integers prefixed with either '+', '-'
#   '?', or ' '.
# param: debug writes diagnostic info to stdout if True.
def write_master(
    path:str='master.lst', 
    master_list:list=[],
    add_list:list=[], 
    del_list:list=[], 
    check_list:list=[], 
    debug:bool=True):
    with open(path, encoding='utf8', mode='w') as f:
        if master_list:
            for holding in master_list:
                if debug:
                    print(f"{holding}")
                f.write(f"{holding}\n")
        else:
            for holding in add_list:
                if debug:
                    print(f"+{holding}")
                f.write(f"+{holding}\n")
            for holding in del_list:
                if debug:
                    print(f"-{holding}")
                f.write(f"-{holding}\n")
            for holding in check_list:
                if debug:
                    print(f"?{holding}")
                f.write(f"?{holding}\n")
    f.close()

# Reads the master list of instructions. The master list is created by a
# either '--set', '--unset', or the combination of '--local' and '--remote'.
# param: path of the master list. String.
# param: list of oclc numbers to add. The list is just integers.
# param: list of oclc numbers to delete. List of integers.
# param: list of oclc numbers to check. Ditto integers.
# param: debug writes diagnostic info to stdout if True.
# return:
def read_master(
    path:str='master.lst', 
    debug:bool=True):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        if debug:
            print(f"checking {path} for OCLC numbers and processing instructions.")
        with open(path, encoding='utf-8', mode='r') as f:
            temp = f.readlines()
        f.close()
        if debug:
            print(f"read {len(temp)} lines from {path}")
        # Clear in case used from another switch.
        add_list = []
        del_list = []
        check_list = []
        for number in temp:
            number = number.rstrip()
            if number.startswith('+'):
                add_list.append(number[1:])
            elif number.startswith('-'):
                del_list.append(number[1:])
            elif number.startswith('?'):
                check_list.append(number[1:])
            else:
                continue
        if debug:
            print(f"first 5 add records: {add_list[:5]}")
            print(f"first 5 del records: {del_list[:5]}")
            print(f"first 5 chk records: {check_list[:5]}")
    return add_list, del_list, check_list

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

# Adds or sets the institutional holdings.
# param: oclc number list of holdings to set.
# param: config_yaml string path to the YAML file, containing connection and authentication for 
#   a given server.
# return: OclcReport object.
def _check_holdings_(oclc_numbers:list, config_yaml:str, debug:bool=False):
    # Create a web service object. 
    ws = OclcService(config_yaml, debug)
    report = OclcReport(config_yaml, debug)
    results = []
    while oclc_numbers:
        response = ws.set_holdings(oclc_numbers)
    #     results = report.check_response(response, debug=debug)
    #     # TODO: Move to the ws object: print(f"batched {batch_count} records...")
    # r_dict = report.get_check_results()
    # print(f"processed {r_dict['total']} total records with {r_dict['errors']} errors")

# Given two lists, compute which numbers OCLC needs to add (or set), which they need to delete (unset)
# and which need no change.
# param:  List of oclc numbers to delete or unset.
# param:  List of oclc numbers to set or add. 
def _diff_(del_nums:list, add_nums:list) -> list:
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
    parser.add_argument('-c', '--check', action='store', metavar='[/foo/check.lst]', help='Check if the OCLC numbers in the list are valid.')
    parser.add_argument('-d', '--debug', action='store_true', help='turn on debugging.')
    parser.add_argument('-l', '--local', action='store', metavar='[/foo/local.lst]', help='Local OCLC numbers list collected from the library\'s ILS.')
    parser.add_argument('-r', '--remote', action='store', metavar='[/foo/remote.lst]', help='Remote (OCLC) numbers list from WorldCat holdings report.')
    parser.add_argument('-s', '--set', action='store', metavar='[/foo/bar.txt]', help='OCLC numbers to add or set in WorldCat.')
    parser.add_argument('-u', '--unset', action='store', metavar='[/foo/bar.txt]', help='OCLC numbers to delete from WorldCat.')
    parser.add_argument('--update', action='store_true', default=False, help='Will update the database with instructions found in the "master.lst".')
    parser.add_argument('-x', '--xml_records', action='store', help='file of MARC21 XML catalog records to submit as special local holdings.')
    parser.add_argument('-y', '--yaml', action='store', metavar='[/foo/test.yaml]', required=True, help='alternate YAML file for testing.')
    args = parser.parse_args()
    
    # Load configuration.
    if args.yaml and os.path.isfile(args.yaml) == False:
        sys.stderr.write(f"*error, required (YAML) configuration file not found! No such file: '{args.yaml}'.\n")
        sys.exit()
    
    if args.debug:
        print(f"check: '{args.check}'")
        print(f"debug: '{args.debug}'")
        print(f"local: '{args.local}'")
        print(f"remote: '{args.remote}'")
        print(f"set: '{args.set}'")
        print(f"unset: '{args.unset}'")
        print(f"update: '{args.update}'")
        print(f"xml records: '{args.xml_records}'")
        print(f"yaml: '{args.yaml}'")

    # Upload XML MARC21 records.
    if args.xml_records:
        pass
    
    # Two lists, one for adding holdings and one for deleting holdings. 
    set_holdings   = []
    unset_holdings = []
    check_holdings = []
    # Add records to institution's holdings.
    if args.set:
        set_holdings = _read_num_file_(args.set, 'set', args.debug)
        
    # delete records from institutional holdings.
    if args.unset:
        unset_holdings = _read_num_file_(args.unset, 'unset', args.debug)

    if args.check:
        check_holdings = _read_num_file_(args.check, 'check', args.debug)

    # Reclamation report that is both files must exist and be read.
    if args.local and args.remote:
        # Read the list of local holdings. See Readme.md for more information on how
        # to collect OCLC numbers from the ILS.
        set_holdings.clear()
        set_holdings = _read_num_file_(args.local, 'set', args.debug)
        # Read the report of remote holdings (holdings at OCLC)
        unset_holdings.clear()
        unset_holdings = _read_num_file_(args.remote, 'unset', args.debug)
        # Create a 'master' list that indicates with are to be removed 
        # and which are to be added, then exit. The script can then be re-run
        # using the same file for both the '--set' and '--unset' flags to run
        # the master. Check the list first before beginning.
        master_list = _diff_(unset_holdings, set_holdings)
        write_master(MASTER_LIST_PATH, master_list=master_list)
        read_master(MASTER_LIST_PATH, debug=args.debug)

        
    # Call the web service with the appropriate list, and capture results.
    if args.update:
        
        pass


if __name__ == "__main__":
    if TEST:
        import doctest
        doctest.testfile("tests/oclc.tst")
    else:
        main(sys.argv[1:])
# EOF