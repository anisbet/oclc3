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
from flat2marcxml import MarcXML

# Master list of OCLC numbers and instructions produced with --local and --remote flags.
MASTER_LIST_PATH = 'master.lst'
# Runs doctests
# TEST = True
# Runs command line.
TEST = False

# OCLC number search regexes
OCLC_ADD_MATCHER = re.compile(r'^[+]?(\d|\(OCoLC\))?\d+\b(?!\.)')
OCLC_DEL_MATCHER = re.compile(r'^[\-]?(\d|\(OCoLC\))?\d+\b(?!\.)')
OCLC_CHK_MATCHER = re.compile(r'^[?]?(\d|\(OCoLC\))?\d+\b(?!\.)')
NUM_MATCHER  = re.compile(r'\d+')

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
def _find_set_(line:str):
    matches = re.search(OCLC_ADD_MATCHER, line)
    if matches:
        num_match = re.search(NUM_MATCHER, line)
        return num_match[0]

# Find unset values in a string. 
# param: line str to search. 
# return: The matching OCLC number or nothing if no match.
def _find_unset_(line):
    matches = re.search(OCLC_DEL_MATCHER, line)
    if matches:
        num_match = re.search(NUM_MATCHER, line)
        return num_match[0]

# Find oclc numbers that need checking. 
# param: line str from OCLC number list file. 
# return: The matching OCLC number or nothing if no match.
def _find_check_(line):
    matches = re.search(OCLC_CHK_MATCHER, line)
    if matches:
        num_match = re.search(NUM_MATCHER, line)
        return num_match[0]

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
        print(f"Reading {num_file}")
    if not exists(num_file):
        sys.stderr.write(f"*error, no such file: '{num_file}'.\n")
        return nums

    # Read in a list of OCLC numbers to set.
    with open(num_file, encoding='utf8', mode='r') as f:
        for l in f:
            line = l.rstrip()
            if set_unset == 'set':
                num = _find_set_(line)
                if num:
                    nums.append(num)
            elif set_unset == 'unset':
                num = _find_unset_(line)
                if num:
                    nums.append(num)
            elif set_unset == 'check':
                num = _find_check_(line)
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
                f.write(f"{holding}\n")
        else:
            for holding in add_list:
                f.write(f"+{holding}\n")
            for holding in del_list:
                f.write(f"-{holding}\n")
            for holding in check_list:
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
def read_master(path:str='master.lst', debug:bool=True):
    if exists(path) and getsize(path) > 0:
        if debug:
            print(f"checking {path} for OCLC numbers and processing instructions.")
        with open(path, encoding='utf-8', mode='r') as f:
            # Clear in case used from another switch.
            add_list = []
            del_list = []
            check_list = []
            skipped = 0
            for temp in f:
                number = temp.rstrip()  
                if number.startswith('+'):
                    add_list.append(number[1:])
                elif number.startswith('-'):
                    del_list.append(number[1:])
                elif number.startswith('?'):
                    check_list.append(number[1:])
                else:
                    skipped += 1
                    continue
            if debug:
                print(f"first 5 add records: {add_list[:5]}")
                print(f"first 5 del records: {del_list[:5]}")
                print(f"first 5 chk records: {check_list[:5]}")
                if skipped:
                    print(f"{skipped} records remained status quo")
    return add_list, del_list, check_list

# Given two lists, compute which numbers OCLC needs to add (or set), which they need to delete (unset)
# and which need no change.
# param:  List of oclc numbers to delete or unset.
# param:  List of oclc numbers to set or add. 
def diff_deletes_adds(del_nums:list, add_nums:list, debug:bool=False) -> list:
    # Store uniq nums and sign.
    ret_dict = {}
    p_count = 0
    total   = 0
    for oclcnum in del_nums:
        ret_dict[oclcnum] = "-"
        p_count += 1
    if debug :
        sys.stderr.write(f"total deletes: {p_count}\n")
    total += p_count
    p_count = 0
    for libnum in add_nums:
        if libnum in ret_dict:
            ret_dict[libnum] = " "
        else:
            ret_dict[libnum] = "+"
        p_count += 1
    total += p_count
    if debug :
        sys.stderr.write(f"total adds   : {p_count}\n")
        sys.stderr.write(f"total        : {total}\n")
    ret_list = []
    for (num, sign) in ret_dict.items():
        ret_list.append(f"{sign}{num}")
    return ret_list

# Prints a consistent tally message of how things worked out. 
# param: action string, what type of service called this function. 
# param: tally dictionary provided by the report object of parsed JSON results. 
# param: Log object to write to the log file. 
# param: Remaining records, count of records that didn't get processed. This 
#   can be non-zero if the web service is interupted or you exceed quota of 
#   web service calls.
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
    if not flat_records:
        print_tally('bib upload', {}, logger)
        return
    # TODO: This request throws an error on the test sandbox. I have submitted a query
    # to OCLC to determine why, but have not heard back yet. April 06, 2023.
    ws = OclcService(configs, logger=logger, debug=debug)
    report = OclcReport(logger=logger, debug=debug)
    left_over_record_count = 0
    for flat_record in flat_records:
        xml_record = MarcXML(flat_record)
        if debug:
            print(f"DEBUG HERE xml: {xml_record}")
        response = ws.create_intitution_level_bib_record(xml_record.as_bytes(), debug=debug)
        # response = ws.validate_add_bib_record(xml_record.as_bytes(), debug=debug)
        if debug:
            print(f"DEBUG HERE response: {response}")
        if not report.create_bib_response(response, debug=debug):
            left_over_record_count = len(flat_records)
            msg = f"The web service stopped while uploading XML holdings.\nThe last record processed was {flat_record}\n\n"
            logger.logit(msg, level='error', include_timestamp=True)
            break
    r_dict = report.get_bib_load_results()
    print_tally('bib upload', r_dict, logger)

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
    if not oclc_numbers:
        print_tally('add / set', {}, logger)
        return
    # Create a web service object. 
    ws = OclcService(configs, logger=logger, debug=debug)
    report = OclcReport(logger=logger, debug=debug)
    while oclc_numbers:
        param_str, status_code, content = ws.set_institution_holdings(oclc_numbers)
        if not report.set_response(code=status_code, json_data=content, debug=debug):
            msg = f"The web service stopped while setting holdings:\n{param_str}"
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
def check_our_holdings(
  oclc_numbers:list, 
  configs:dict, 
  logger:Log, 
  debug:bool=False):
    if not oclc_numbers:
        print_tally('check', {}, logger)
        return
    # Create a web service object. 
    ws = OclcService(configs, logger=logger, debug=debug)
    report = OclcReport(logger=logger, debug=debug)
    while oclc_numbers:
        param_str, status_code, content = ws.check_institution_holdings(oclc_numbers, debug=debug)
        if not report.check_holdings_response(code=status_code, json_data=content, debug=debug):
            msg = f"The web service stopped while checking numbers:\n{param_str}"
            logger.logit(msg, level='error', include_timestamp=True)
            break
    r_dict = report.get_check_holdings_results()
    print_tally('holdings', r_dict, logger)

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
    if not oclc_numbers:
        print_tally('delete / unset', {}, logger)
        return
    # Create a web service object. 
    ws = OclcService(configs, logger=logger, debug=debug)
    report = OclcReport(logger=logger, debug=debug)
    while oclc_numbers:
        param_str, status_code, content = ws.unset_institution_holdings(oclc_numbers, debug=debug)
        if not report.delete_response(code=status_code, json_data=content, debug=debug):
            msg = f"The web service stopped while deleting holdings:\n{param_str}"
            logger.logit(msg, level='error', include_timestamp=True)
            break
    r_dict = report.get_delete_holdings_results()
    print_tally('delete / unset', r_dict, logger)



# Main entry to the application if not testing.
def main(argv):

    parser = argparse.ArgumentParser(
        prog = 'oclc',
        usage='%(prog)s [options]' ,
        description='Maintains holdings in OCLC WorldCat database.',
        epilog='See "-h" for help more information.'
    )
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('-c', '--check', action='store', metavar='[/foo/check.lst]', help='Check if the OCLC numbers in the list are valid.')
    parser.add_argument('-d', '--debug', action='store_true', help='turn on debugging.')
    parser.add_argument('-l', '--local', action='store', metavar='[/foo/local.lst]', help='Local OCLC numbers list collected from the library\'s ILS.')
    parser.add_argument('-r', '--remote', action='store', metavar='[/foo/remote.lst]', help='Remote (OCLC) numbers list from WorldCat holdings report.')
    parser.add_argument('-s', '--set', action='store', metavar='[/foo/bar.txt]', help='OCLC numbers to add or set in WorldCat.')
    parser.add_argument('-u', '--unset', action='store', metavar='[/foo/bar.txt]', help='OCLC numbers to delete from WorldCat.')
    parser.add_argument('--update_instructions', action='store', default=MASTER_LIST_PATH, help=f"File that contains instructions to update WorldCat.Default {MASTER_LIST_PATH}")
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
        print(f"== vars ==")
        print(f"check: '{args.check}'")
        print(f"debug: '{args.debug}'")
        print(f"local: '{args.local}'")
        print(f"remote: '{args.remote}'")
        print(f"set: '{args.set}'")
        print(f"unset: '{args.unset}'")
        print(f"update: '{args.update_instructions}'")
        print(f"xml records: '{args.xml_records}'")
        print(f"yaml: '{args.yaml}'")
        print(f"== vars ==\n")

    # Upload XML MARC21 records.
    if args.xml_records:
        # TODO: Waiting for OCLC to respond with answers to why the XML throws an error. 
        pass
    
    # Two lists, one for adding holdings and one for deleting holdings. 
    set_holdings_lst   = []
    unset_holdings_lst = []
    check_holdings_lst = []
    # Add records to institution's holdings.
    if args.set:
        set_holdings_lst = _read_num_file_(args.set, 'set', args.debug)
        
    # delete records from institutional holdings.
    if args.unset:
        unset_holdings_lst = _read_num_file_(args.unset, 'unset', args.debug)

    # Create a list of oclc numbers to check a list of holdings.
    if args.check:
        check_holdings_lst = _read_num_file_(args.check, 'check', args.debug)

    # Reclamation report that is both files must exist and be read.
    if args.local and args.remote:
        # Read the list of local holdings. See Readme.md for more information on how
        # to collect OCLC numbers from the ILS.
        set_holdings_lst.clear()
        if args.debug:
            sys.stderr.write(f"DEBUG: starting to read local holdings.\n")
        set_holdings_lst = _read_num_file_(args.local, 'set', args.debug)
        if args.debug:
            sys.stderr.write(f"DEBUG: done.\n")
        # Read the report of remote holdings (holdings at OCLC)
        unset_holdings_lst.clear()
        if args.debug:
            sys.stderr.write(f"DEBUG: starting to read OCLC holdings.\n")
        unset_holdings_lst = _read_num_file_(args.remote, 'unset', args.debug)
        if args.debug:
            sys.stderr.write(f"DEBUG: done.\n")
        # Create a 'master' list that indicates with are to be removed 
        # and which are to be added, then exit. The script can then be re-run
        # using the same file for both the '--set' and '--unset' flags to run
        # the master. Check the list first before beginning.
        if args.debug:
            sys.stderr.write(f"DEBUG: compiling difference of holdings.\n")
        master_list = diff_deletes_adds(unset_holdings_lst, set_holdings_lst, debug=args.debug)
        if args.debug:
            sys.stderr.write(f"DEBUG: done.\n")
            sys.stderr.write(f"DEBUG: writing {args.update_instructions}.\n")
        write_master(path=args.update_instructions, master_list=master_list)
        if args.debug:
            sys.stderr.write(f"DEBUG: done.\n")

    # Call the web service with the appropriate list, and capture results.
    if args.update_instructions:
        set_holdings_lst, unset_holdings_lst, check_holdings_lst = read_master(args.update_instructions, debug=args.debug)
        if args.debug:
            sys.stderr.write(f"set: {set_holdings_lst[:3]}...\nunset: {unset_holdings_lst[:3]}...\ncheck: {check_holdings_lst[:3]}...\n")
        if check_holdings_lst:
            check_our_holdings(check_holdings_lst, configs=configs, logger=logger, debug=args.debug)
        if unset_holdings_lst:
            delete_holdings(unset_holdings_lst, configs=configs, logger=logger, debug=args.debug)
        if set_holdings_lst:
            add_holdings(set_holdings_lst, configs=configs, logger=logger, debug=args.debug)


if __name__ == "__main__":
    if TEST:
        import doctest
        doctest.testfile("oclc.tst")
    else:
        main(sys.argv[1:])
# EOF