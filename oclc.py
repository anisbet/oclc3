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
import sys
from os.path import join, dirname, exists, getsize
import yaml
import argparse
import re
from oclcws import OclcService
from oclcreport import OclcReport
from log import Log

# Master list of OCLC numbers and instructions produced with --local and --remote flags.
MASTER_LIST_PATH = 'master.lst'
TEST = True


# Loads the yaml file for configs.
# param: path of the yaml file. 
# return: dictionary of settings, or an empty dict if there was an error.
def _load_yaml_(yaml_path:str) -> dict:
    yaml_file = join(dirname(__file__), yaml_path)
    config = {}
    if exists(yaml_file):
        with open(yaml_file) as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                config['error'] = f"{exc}"
    else:
        msg = f"*error, yaml file not found! Expected '{yaml_file}'"
        config['error'] = msg
    return config

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
    if not exists(num_file):
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
    if exists(path) and getsize(path) > 0:
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

# Given two lists, compute which numbers OCLC needs to add (or set), which they need to delete (unset)
# and which need no change.
# param:  List of oclc numbers to delete or unset.
# param:  List of oclc numbers to set or add. 
def diff_deletes_adds(del_nums:list, add_nums:list) -> list:
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

# Adds or sets the institutional holdings.
# param: oclc number list of holdings to set.
# param: config_yaml string path to the YAML file, containing connection and authentication for 
#   a given server. 
# param: Logger. 
# param: debug True for debug information.
# return: None
def add_holdings(
  oclc_numbers:list, 
  configs:dict, 
  logger:Log, 
  debug:bool=False):
    # Create a web service object. 
    ws = OclcService(configs, logger=logger, debug=debug)
    report = OclcReport(logger=logger, debug=debug)
    left_over_record_count = 0
    while oclc_numbers:
        number_str, status_code, json_response = ws.set_institution_holdings(oclc_numbers)
        if not report.set_response(code=status_code, json_data=json_response, debug=debug):
            left_over_record_count = len(oclc_numbers)
            msg = f"The web service stopped while setting holdings.\nThe following numbers weren't processed.\n{oclc_numbers}"
            logger.logit(msg, level='error', include_timestamp=True)
            break
    r_dict = report.get_set_holdings_results()
    print_tally('add / set', r_dict, logger)

# Checks list of OCLC control numbers as part of the institutional holdings.
# param: oclc number list of holdings to set.
# param: config_yaml string path to the YAML file, containing connection and authentication for 
#   a given server.
# param: Logger. 
# param: debug True for debug information.
# return: None
def check_holdings(
  oclc_numbers:list, 
  configs:dict, 
  logger:Log, 
  debug:bool=False):
    # Create a web service object. 
    ws = OclcService(configs, logger=logger, debug=debug)
    report = OclcReport(logger=logger, debug=debug)
    left_over_record_count = 0
    while oclc_numbers:
        response = ws.check_oclc_numbers(oclc_numbers)
        if not report.check_response(response, debug=debug):
            left_over_record_count = len(oclc_numbers)
            msg = f"The web service stopped while checking numbers.\nThe following numbers weren't processed.\n{oclc_numbers}"
            logger.logit(msg, level='error', include_timestamp=True)
            break
    r_dict = report.get_check_results()
    print_tally('check', r_dict, logger)

# Checks list of OCLC control numbers as part of the institutional holdings.
# param: oclc number list of holdings to set.
# param: config_yaml string path to the YAML file, containing connection and authentication for 
#   a given server.
# param: Logger. 
# param: debug True for debug information.
# return: None
def delete_holdings(
  oclc_numbers:list, 
  configs:dict, 
  logger:Log, 
  debug:bool=False):
    # Create a web service object. 
    ws = OclcService(configs, logger=logger, debug=debug)
    report = OclcReport(logger=logger, debug=debug)
    left_over_record_count = 0
    while oclc_numbers:
        response = ws.unset_institution_holdings(oclc_numbers)
        if not report.delete_response(response, debug=debug):
            left_over_record_count = len(oclc_numbers)
            msg = f"The web service stopped while deleting holdings.\nThe following numbers weren't processed.\n{oclc_numbers}"
            logger.logit(msg, level='error', include_timestamp=True)
            break
    r_dict = report.get_delete_holdings_results()
    print_tally('delete / unset', r_dict, logger)

def print_tally(action:str, tally:dict, logger:Log, remaining:int=0):
    msg =  f"operation '{action}' results.\n"
    msg += f"          succeeded: {tally['success']}\n"
    msg += f"           warnings: {tally['warnings']}\n"
    msg += f"             errors: {tally['errors']}\n"
    if remaining and remaining > 0:
        msg += f"unprocessed records: {remainig}\n"
    msg += f"      total records: {tally['total']}"
    logger.logit(f"{msg}", include_timestamp=False)

# Creates an institutional-specific bib record. 
# param: list of records as lists of FLAT strings, where FLAT refers to 
#  SirsiDynix's Symphony FLAT record format.
def upload_bib_record(
  flat_records:list, 
  configs:dict, 
  logger:Log, 
  debug:bool=False):
    ws = OclcService(configs, logger=logger, debug=debug)
    report = OclcReport(logger=logger, debug=debug)
    left_over_record_count = 0
    for flat_record in flat_records:
        xml_record = MarcXML(flat_record)
        response = ws.create_intitution_level_bib_record(record_xml)
        if not report.create_bib_response(response, debug=debug):
            left_over_record_count = len(flat_records)
            msg = f"The web service stopped while uploading XML holdings.\nThe last record processed was {flat_record}\n\n"
            logger.logit(msg, level='error', include_timestamp=True)
            break
        # if the report.create_bib_response returns false it means errors.
        # stop the loop and report the rest of the records that didn't get completed 
    r_dict = report.get_bib_load_results()
    print_tally('bib upload', r_dict, logger)


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
    if args.yaml and exists(args.yaml):
        configs = _load_yaml_(args.yaml)
        if 'error' in configs.keys():
            sys.stderr.write(configs.get('error'))
            sys.exit()
        logger = Log(log_file=configs['report'])
    else:
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
    set_holdings_lst   = []
    unset_holdings_lst = []
    check_holdings     = []
    # Add records to institution's holdings.
    if args.set:
        set_holdings_lst = _read_num_file_(args.set, 'set', args.debug)
        
    # delete records from institutional holdings.
    if args.unset:
        unset_holdings_lst = _read_num_file_(args.unset, 'unset', args.debug)

    if args.check:
        check_holdings = _read_num_file_(args.check, 'check', args.debug)

    # Reclamation report that is both files must exist and be read.
    if args.local and args.remote:
        # Read the list of local holdings. See Readme.md for more information on how
        # to collect OCLC numbers from the ILS.
        set_holdings_lst.clear()
        set_holdings_lst = _read_num_file_(args.local, 'set', args.debug)
        # Read the report of remote holdings (holdings at OCLC)
        unset_holdings_lst.clear()
        unset_holdings_lst = _read_num_file_(args.remote, 'unset', args.debug)
        # Create a 'master' list that indicates with are to be removed 
        # and which are to be added, then exit. The script can then be re-run
        # using the same file for both the '--set' and '--unset' flags to run
        # the master. Check the list first before beginning.
        master_list = diff_deletes_adds(unset_holdings_lst, set_holdings_lst)
        write_master(MASTER_LIST_PATH, master_list=master_list)
        read_master(MASTER_LIST_PATH, debug=args.debug)

        
    # Call the web service with the appropriate list, and capture results.
    if args.update:
        
        pass


if __name__ == "__main__":
    if TEST:
        import doctest
        doctest.testfile("oclc.tst")
    else:
        main(sys.argv[1:])
# EOF