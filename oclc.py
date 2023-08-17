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
from os.path import join, dirname, exists
import yaml
import argparse
from oclcws import OclcService
from oclcreport import OclcReport
from flat import Flat
from log import Log
from flat2marcxml import MarcXML

#######test#########
# Use this so outputs match doctest expectations.
TEST = True
#######test#########
#######prod#########
# Use this for Sandbox or Production. 
# TEST = False
#######prod#########
VERSION='3.00.00_a'

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

# Used for reporting percents.
# param: value float value.
# param: prec integer precision of the returned float. 
# return: float value of requested precision.  
def trim_decimals(value, prec:int=2) ->float:
    f_str = f"%.{prec}f"
    return float(f_str % round(float(value), prec))



# Prints a consistent tally message of how things worked out. 
# param: action string, what type of service called this function. 
# param: tally dictionary provided by the report object of parsed JSON results. 
# param: Log object to write to the log file. 
# param: Remaining records, count of records that didn't get processed. This 
#   can be non-zero if the web service is interupted or you exceed quota of 
#   web service calls.
# return: none
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
    done_list = []
    while oclc_numbers:
        param_str, status_code, content = ws.set_institution_holdings(oclc_numbers)
        done = param_str.split(',')
        last_oclc_number = ''
        if done:
            last_oclc_number = done[-1]
        if not report.set_response(code=status_code, json_data=content, debug=debug):
            msg = f"The web service stopped while setting holdings:\n{last_oclc_number}"
            logger.logit(msg, level='error', include_timestamp=True)
            break
        done_list.extend(done)
    r_dict = report.get_set_holdings_results()
    print_tally('add / set', r_dict, logger)
    return done_list

# Checks list of OCLC control numbers as part of the institutional holdings.
# param: oclc number list of holdings to set.
# param: config_yaml string path to the YAML file, containing connection and authentication for 
#   a given server.
# param: Logger. 
# param: debug True for debug information.
# return: List of done OCLC numbers.
def check_institutional_holdings(
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
    done_list = []
    while oclc_numbers:
        param_str, status_code, content = ws.check_institution_holdings(oclc_numbers, debug=debug)
        done = param_str.split(',')
        last_oclc_number = ''
        if done:
            last_oclc_number = done[-1]
        if not report.check_holdings_response(code=status_code, json_data=content, debug=debug):
            msg = f"The web service stopped while checking numbers:\n{last_oclc_number}"
            logger.logit(msg, level='error', include_timestamp=True)
            break
        done_list.extend(done)
    r_dict = report.get_check_holdings_results()
    print_tally('holdings', r_dict, logger)
    return done_list

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
    done_list = []
    while oclc_numbers:
        param_str, status_code, content = ws.unset_institution_holdings(oclc_numbers, debug=debug)
        done = param_str.split(',')
        last_oclc_number = ''
        if done:
            last_oclc_number = done[-1]
        if not report.delete_response(code=status_code, json_data=content, debug=debug):
            msg = f"The web service stopped while deleting holdings:\n{last_oclc_number}"
            logger.logit(msg, level='error', include_timestamp=True)
            break
        done_list.extend(done)
    r_dict = report.get_delete_holdings_results()
    print_tally('delete / unset', r_dict, logger)
    return done_list

# Main entry to the application if not testing.
def main(argv):

    parser = argparse.ArgumentParser(
        prog = 'oclc',
        usage='%(prog)s [options]' ,
        description='Maintains holdings in OCLC WorldCat database.',
        epilog='See "--hints" for help more information.'
    )
    parser.add_argument('--version', action='version', version='%(prog)s ' + VERSION)
    parser.add_argument('--check', action='store', metavar='[/foo/check.lst]', help='Check if the OCLC numbers in the list are valid.')
    # parser.add_argument('--csv', action='store', metavar='[/foo/oclc_report.csv]', help='Read OCLC report as CSV. Numbers are appended to the remote, or unset list.')
    parser.add_argument('-d', '--debug', action='store_true', help='turn on debugging.')
    hints_msg = """
    Any file specified with --add, --delete, --check will have numbers extracted using methods appropriate to
    the extension of the file used. For example the app will extract the OCLC number from the appropriate '.035.'
    field of the record(s) in the file.
    Supported list files are '.flat', '.lst', '.txt', '.csv/.tsv'. The last two are the formats that OCLC uses
    in their holdings reports. See Readme.md for information on preparing holdings reports.
    """
    # parser.add_argument('-f', '--flat', action='store', metavar='[/foo/bibs.flat]', help=f"{flat_msg}")
    # parser.add_argument('-i', '--ignore', action='store', metavar='{"tag_num": "tag text"}', help=f"Ignore bib records that have a given tag that contains a specific value.")
    # parser.add_argument('-l', '--local', action='store', metavar='[/foo/local.lst]', help='Local OCLC numbers list collected from the library\'s ILS.')
    # parser.add_argument('-r', '--remote', action='store', metavar='[/foo/remote.lst]', help='Remote (OCLC) numbers list from WorldCat holdings report.')
    # parser.add_argument('-s', '--set', action='store', metavar='[/foo/bar.txt]', help='OCLC numbers to add or set in WorldCat.')
    # parser.add_argument('-u', '--unset', action='store', metavar='[/foo/bar.txt]', help='OCLC numbers to delete from WorldCat.')
    parser.add_argument('--add', action='store', metavar='[/foo/my_nums.lst]', help='List of OCLC numbers to add to OCLC\'s holdings database.')
    parser.add_argument('--delete', action='store', metavar='[/foo/oclc_nums.lst]', help='List of OCLC numbers to delete from OCLC\'s holdings database.')
    parser.add_argument('--hints', help=f"{hints_msg}")
    parser.add_argument('--update', action='store_true', default=False, help='Actually do the work.')
    # parser.add_argument('--update_instructions', action='store', help=f"File that contains instructions to update WorldCat.")
    # wl_msg = """ 
    # Computes the what is left to do in the master list based on what is in the receipt file. The master list is defined by the 
    # '--update_instructions' flag, while the receipt file is always named 'receipt.txt'. If the web service times out or you exceed 
    # quotas, you can use this to compare the two files and create a new master list. By default the master list is over-written 
    # with the remaining instructions, including any edits to the master list since the receipt was created. That is, if the script
    # created a receipt with '-11111111' as deleted, but the master list was later changed to '?11111111', the new check instruction
    # is preserved and written to the master list.

    # python oclc.py --whats_left --update_instructions=master.lst
    # """
    # parser.add_argument('--whats_left', action='store_true', help=f"{wl_msg}")
    # parser.add_argument('-x', '--xml_records', action='store', help='file of MARC21 XML catalog records to submit as special local holdings.')
    parser.add_argument('-y', '--yaml', action='store', default='test.yaml', metavar='[/foo/prod.yaml]', help='alternate YAML file for testing. Default to "test.yaml"')
    args = parser.parse_args()
    
    # Load configuration.
    yaml_file = 'test.yaml'
    if args.yaml:
        yaml_file = args.yaml
    if exists(yaml_file):
        configs = _load_yaml_(yaml_file)
        if 'error' in configs.keys():
            sys.stderr.write(configs.get('error'))
            sys.exit()
        logger = Log(log_file=configs.get('report'))
        hits_quota = configs.get('hitsQuota')
        logger.logit(f"=== starting version {VERSION}", include_timestamp=True)
    else:
        sys.stderr.write(f"*error, required (YAML) configuration file not found! No such file: '{yaml_file}'.\n")
        sys.exit()

    if args.debug:
        logger.logit(f"== vars ==")
        logger.logit(f"check: '{args.check}'")
        logger.logit(f"debug: '{args.debug}'")
        logger.logit(f"update: '{args.update_instructions}'")
        logger.logit(f"yaml: '{yaml_file}'")
        logger.logit(f"hits quota: '{hits_quota}'")
        logger.logit(f"== vars ==\n")

    # Upload XML MARC21 records.
    if args.xml_records:
        # TODO: Waiting for OCLC to respond with answers to why the XML throws an error. 
        print(f"currently not supported.")
        pass
    
    # Two lists, one for adding holdings and one for deleting holdings. 
    set_holdings_lst   = []
    unset_holdings_lst = []
    check_holdings_lst = []
    done_lst           = []
    

    # Add records to institution's holdings.
    if args.add:
        print(f"currently not supported.")
        pass
        
    # delete records from institutional holdings.
    if args.delete:
        print(f"currently not supported.")
        pass

    # Create a list of oclc numbers to check a list of holdings.
    if args.check:
        print(f"currently not supported.")
        pass

    

    # Call the web service with the appropriate list, and capture results.
    # try:
    #     if args.update:
    #         if args.update_instructions:
    #             set_holdings_lst, unset_holdings_lst, check_holdings_lst, done_lst = read_master(args.update_instructions, debug=args.debug)
    #             if args.debug:
    #                 sys.stderr.write(f"set: {set_holdings_lst[:3]}...\nunset: {unset_holdings_lst[:3]}...\ncheck: {check_holdings_lst[:3]}...\n")
    #             if check_holdings_lst:
    #                 check_holdings_lst = get_quota(check_holdings_lst, 'checkQuota', configs)
    #                 done = check_institutional_holdings(check_holdings_lst, configs=configs, logger=logger, debug=args.debug)
    #                 done_lst.extend(done)
    #             if unset_holdings_lst:
    #                 unset_holdings_lst = get_quota(unset_holdings_lst, 'deleteQuota', configs)
    #                 done = delete_holdings(unset_holdings_lst, configs=configs, logger=logger, debug=args.debug)
    #                 done_lst.extend(done)
    #             if set_holdings_lst:
    #                 set_holdings_lst = get_quota(set_holdings_lst, 'addQuota', configs)
    #                 done = add_holdings(set_holdings_lst, configs=configs, logger=logger, debug=args.debug)
    #                 done_lst.extend(done)
    #             write_update_instruction_file(path='receipt.txt', add_list=set_holdings_lst, del_list=unset_holdings_lst, check_list=check_holdings_lst, done_list=done_lst)
    #             if flat_manager:
    #                 my_updated_numbers = parse_log_for_updated_numbers(logger, debug=args.debug)
    #                 if my_updated_numbers:
    #                     flat_manager.update_and_write_slim_flat(my_updated_numbers)
    #                 else:
    #                     logger.logit(f"No slim file will be produced because no update numbers found in {logger.get_log_file()}\n")
    #         else:
    #             sys.stderr.write(f"*warning, nothing to do because you didn't use the --update_instructions flag.")
    #     logger.logit('done', include_timestamp=True)
    # except KeyboardInterrupt:
    #     write_update_instruction_file(path='receipt.txt', add_list=set_holdings_lst, del_list=unset_holdings_lst, check_list=check_holdings_lst, done_list=done_lst)
    #     logger.logit('!Warning, received keyboard interrupt!\nSaving work done.', level='error', include_timestamp=True)
    #     logger.logit('exited on <ctrl> + C interrupt.', include_timestamp=True)

if __name__ == "__main__":
    if TEST:
        import doctest
        doctest.testmod()
        doctest.testfile("oclc.tst")
    else:
        main(sys.argv[1:])
# EOF