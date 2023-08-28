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
from lib.oclcws import OclcService
from lib.oclcreport import OclcReport
from log import Logger
from lib.listutils import Lister, InstructionManager
# from lib.flat import Flat
# from lib.flat2marcxml import MarcXML

VERSION='3.00.01'

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

# Prints a consistent tally message of how things worked out. 
# param: action string, what type of service called this function. 
# param: tally dictionary provided by the report object of parsed JSON results. 
# param: Logger object to write to the log file. 
# param: Remaining records, count of records that didn't get processed. This 
#   can be non-zero if the web service is interupted or you exceed quota of 
#   web service calls.
# return: none
def print_tally(action:str, tally:dict, logger:Logger, remaining:int=0):
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
# def upload_bib_record(
#   flat_records:list, 
#   configs:dict, 
#   logger:Logger, 
#   debug:bool=False):
#     if not flat_records:
#         print_tally('bib upload', {}, logger)
#         return
#     # TODO: This request throws an error on the test sandbox. I have submitted a query
#     # to OCLC to determine why, but have not heard back yet. April 06, 2023.
#     ws = OclcService(configs, debug=debug)
#     report = OclcReport(debug=debug)
#     left_over_record_count = 0
#     for flat_record in flat_records:
#         xml_record = MarcXML(flat_record)
#         if debug:
#             print(f"DEBUG HERE xml: {xml_record}")
#         response = ws.create_intitution_level_bib_record(xml_record.as_bytes(), debug=debug)
#         # response = ws.validate_add_bib_record(xml_record.as_bytes(), debug=debug)
#         if debug:
#             print(f"DEBUG HERE response: {response}")
#         if not report.create_bib_response(response, debug=debug):
#             left_over_record_count = len(flat_records)
#             msg = f"The web service stopped while uploading XML holdings.\nThe last record processed was {flat_record}\n\n"
#             logger.logit(msg, level='error', include_timestamp=True)
#             break
#     r_dict = report.get_bib_load_results()
#     print_tally('bib upload', r_dict, logger)

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
  logger:Logger, 
  debug:bool=False):
    if not oclc_numbers:
        print_tally('add / set', {}, logger)
        return
    # Create a web service object. 
    ws = OclcService(configs, debug=debug)
    report = OclcReport(debug=debug)
    done_list = []
    while oclc_numbers:
        param_str, status_code, content = ws.set_institution_holdings(oclc_numbers)
        done = param_str.split(',')
        last_oclc_number = ''
        if done:
            last_oclc_number = done[-1]
        went_okay, messages = report.set_response(code=status_code, json_data=content, debug=debug)
        if went_okay:
            logger.logem(messages)
        else:
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
  logger:Logger, 
  debug:bool=False):
    if not oclc_numbers:
        print_tally('check', {}, logger)
        return
    # Create a web service object. 
    ws = OclcService(configs, debug=debug)
    report = OclcReport(debug=debug)
    done_list = []
    while oclc_numbers:
        param_str, status_code, content = ws.check_institution_holdings(oclc_numbers, debug=debug)
        done = param_str.split(',')
        last_oclc_number = ''
        if done:
            last_oclc_number = done[-1]
        went_okay, messages = report.check_holdings_response(code=status_code, json_data=content, debug=debug)
        if went_okay:
            logger.logem(messages)
        else:
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
  logger:Logger, 
  debug:bool=False):
    if not oclc_numbers:
        print_tally('delete / unset', {}, logger)
        return
    # Create a web service object. 
    ws = OclcService(configs, debug=debug)
    report = OclcReport(debug=debug)
    done_list = []
    while oclc_numbers:
        param_str, status_code, content = ws.unset_institution_holdings(oclc_numbers, debug=debug)
        done = param_str.split(',')
        last_oclc_number = ''
        if done:
            last_oclc_number = done[-1]
        went_okay, messages = report.delete_response(code=status_code, json_data=content, debug=debug)
        if went_okay:
            logger.logem(messages)
        else:
            msg = f"The web service stopped while deleting holdings:\n{last_oclc_number}"
            logger.logit(msg, level='error', include_timestamp=True)
            break
        done_list.extend(done)
    r_dict = report.get_delete_holdings_results()
    print_tally('delete / unset', r_dict, logger)
    return done_list

# Main entry to the application if not testing.
def main(argv):
    
#     hints_msg = '''
#     Any file specified with --add, --delete, --check will have numbers extracted using methods appropriate to
#     the extension of the file used. For example the app will extract the OCLC number from the appropriate '.035.'
#     field of the record(s) in a flat file. In that case the first sub-field 'a' is assumed to be the OCLC number.

#     CSV (or TSV) files are assumed to be OCLC holding reports converted from XSLX (see Readme.md for instructions).
#     Currently these reports start with '=HYPERLINK...' and the OCLC number is extracted from the alt text of the
#     first field.

#     All other file formats are assumed to contain OCLC numbers somewhere on each line and the first number match
#     is assumed to be the OCLC number. See Readme.md for more information and limitations.

#     Supported list files are 
#       * '.flat'
#       * '.lst'
#       * '.txt'
#       * '.csv/.tsv'
#     The last two are the formats that OCLC uses in their holdings reports.

#     You may supply an --add and/or --delete file. In any case duplicate requests are removed, and conflicting
#     requests are neutralized. For example, requesting '1111111' in an --add and --delete list will output an
#     instruction of ' 1111111', which will not be submitted to OCLC since it would count against quotas.

#     YAML Files
#     ----------
# # Test YAML
# author:          'Andrew Nisbet'
# service: 
#   name:          'WCMetaDataTest'
#   clientId:      '[supplied by OCLC]'
#   secret:        '[supplied by OCLC]'
#   registryId:    '[supplied by OCLC]'
#   principalId:   '[supplied by OCLC]'
#   principalIdns: 'urn:oclc:wms:da'
#   institutionalSymbol: 'OCPSB'
#   branchName:    'MAIN'
# ignoreTags: 
#   '250': 'Expected release'
# hitsQuota:       100
# dataDir:         'data'
#     '''
    parser = argparse.ArgumentParser(
        prog = 'oclc',
        usage='%(prog)s [options]' ,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''\
            Maintains holdings in OCLC WorldCat database.
            ''',
        epilog='''\
    Any file specified with --add, --delete, --check will have numbers extracted using methods appropriate to
    the extension of the file used. For example the app will extract the OCLC number from the appropriate '.035.'
    field of the record(s) in a flat file. In that case the first sub-field 'a' is assumed to be the OCLC number.

    CSV (or TSV) files are assumed to be OCLC holding reports converted from XSLX (see Readme.md for instructions).
    Currently these reports start with '=HYPERLINK...' and the OCLC number is extracted from the alt text of the
    first field.

    All other file formats are assumed to contain OCLC numbers somewhere on each line and the first number match
    is assumed to be the OCLC number. See Readme.md for more information and limitations.

    Supported list files are 
      * '.flat'
      * '.lst'
      * '.txt'
      * '.csv/.tsv'
    The last two are the formats that OCLC uses in their holdings reports.

    You may supply an --add and/or --delete file. In any case duplicate requests are removed, and conflicting
    requests are neutralized. For example, requesting '1111111' in an --add and --delete list will output an
    instruction of ' 1111111', which will not be submitted to OCLC since it would count against quotas.

    YAML Files
    ----------
# Test YAML
author:          'Andrew Nisbet'
service: 
  name:          'WCMetaDataTest'
  clientId:      '[supplied by OCLC]'
  secret:        '[supplied by OCLC]'
  registryId:    '[supplied by OCLC]'
  principalId:   '[supplied by OCLC]'
  principalIdns: 'urn:oclc:wms:da'
  institutionalSymbol: 'OCPSB'
  branchName:    'MAIN'
ignoreTags: 
  '250': 'Expected release'
hitsQuota:       100
dataDir:         'data'           
        '''
    )
    parser.add_argument('--add', action='store', metavar='[/foo/my_nums.lst]', help='List of OCLC numbers to add to OCLC\'s holdings database.')
    parser.add_argument('--check', action='store', metavar='[/foo/check.lst]', help='Check if the OCLC numbers in the list are valid.')
    parser.add_argument('-d', '--debug', action='store_true', default=False, help='turn on debugging.')
    parser.add_argument('--delete', action='store', metavar='[/foo/oclc_nums.lst]', help='List of OCLC numbers to delete from OCLC\'s holdings database.')
    parser.add_argument('--done', action='store', metavar='[/foo/completed.lst]', help='Used if the process was interrupted.')
    parser.add_argument('--instructions', action='store', metavar='[/foo/instructions.lst]', help='OCLC update instructions file name.')
    parser.add_argument('--log', action='store', default='oclc.log', metavar='[/foo/oclc_YYYY-MM-DD.log]', help=f"Log file.")
    parser.add_argument('--run', action='store', metavar='[/foo/instructions.lst]', help=f"File that contains instructions to update WorldCat holdings.")
    parser.add_argument('--version', action='version', version='%(prog)s ' + VERSION)
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
        logger = Logger(log_file=args.log)
        hits_quota = configs.get('hitsQuota')
        logger.logit(f"=== starting version {VERSION}", include_timestamp=True)
    else:
        sys.stderr.write(f"*error, required (YAML) configuration file not found! No such file: '{yaml_file}'.\n")
        sys.exit()

    if args.debug:
        logger.logit(f"== vars ==")
        logger.logit(f"add: '{args.add}'")
        logger.logit(f"delete: '{args.delete}'")
        logger.logit(f"check: '{args.check}'")
        logger.logit(f"done: '{args.done}'")
        logger.logit(f"debug: '{args.debug}'")
        logger.logit(f"instructions: '{args.instructions}'")
        logger.logit(f"run: '{args.run}'")
        logger.logit(f"yaml: '{yaml_file}'")
        logger.logit(f"hits quota: '{hits_quota}'")
        logger.logit(f"== vars ==\n")

    # Upload XML MARC21 records.
    # if args.xml_records:
    #     # TODO: Waiting for OCLC to respond with answers to why the XML throws an error.
    #     # TODO: Move to different class that works with the flat file to create xml for 
    #     # TODO: records that don't have OCLC numbers, and to create a slim file for updating ILS
    #     # TODO: records.  
    #     print(f"currently not supported.")
    #     pass
    
    # Two lists, one for adding holdings and one for deleting holdings. 
    set_holdings_lst   = []
    unset_holdings_lst = []
    check_holdings_lst = []
    done_lst           = []

    # Add records to institution's holdings.
    if args.add:
        lister = Lister(args.add, debug=args.debug)
        set_holdings_lst = lister.get_list('+')
        
    # delete records from institutional holdings.
    if args.delete:
        lister = Lister(args.delete, debug=args.debug)
        unset_holdings_lst = lister.get_list('-')

    # Create a list of oclc numbers to check a list of holdings.
    if args.check:
        lister = Lister(args.check, debug=args.debug)
        check_holdings_lst = lister.get_list('?')

    if args.done:
        lister = Lister(args.done, debug=args.debug)
        done_lst = lister.get_list('!')

    if args.instructions:
        # Merge any and all lists and write out instructions.
        instruction_manager = InstructionManager(args.instructions, debug=args.debug)
        instruction_list = instruction_manager.merge(set_holdings_lst, unset_holdings_lst, check_holdings_lst, done_lst)
        # Output the instructions list. 
        instruction_manager.write_instructions(instruction_list)
    elif args.run:
        # Load instruction list specified by args.run. 
        instruction_manager = InstructionManager(args.run, debug=args.debug)
        set_holdings_lst    = instruction_manager.read_instruction_numbers('+')
        unset_holdings_lst  = instruction_manager.read_instruction_numbers('-')
        check_holdings_lst  = instruction_manager.read_instruction_numbers('?')
        # If there are done items in the file, mark them done for when we write to '.completed'.
        done_lst            = list('!' + num for num in instruction_manager.read_instruction_numbers('!'))
        
        # Call the web service with the appropriate list, and capture results.
        try:
            if args.debug:
                sys.stderr.write(f"set: {set_holdings_lst[:3]}...\nunset: {unset_holdings_lst[:3]}...\ncheck: {check_holdings_lst[:3]}...\n")
            if check_holdings_lst:
                check_holdings_lst = check_holdings_lst[0:int(hits_quota)]
                done = check_institutional_holdings(check_holdings_lst, configs=configs, logger=logger, debug=args.debug)
                done_lst.extend(list('!' + num for num in done))
            if unset_holdings_lst:
                unset_holdings_lst = unset_holdings_lst[0:int(hits_quota)]
                done = delete_holdings(unset_holdings_lst, configs=configs, logger=logger, debug=args.debug)
                done_lst.extend(list('!' + num for num in done))
            if set_holdings_lst:
                set_holdings_lst = set_holdings_lst[0:int(hits_quota)]
                done = add_holdings(set_holdings_lst, configs=configs, logger=logger, debug=args.debug)
                done_lst.extend(list('!' + num for num in done))
            # Write out the lists
            instruction_manager = InstructionManager(args.run + '.completed', debug=args.debug)
            completed_list = instruction_manager.merge(set_holdings_lst, unset_holdings_lst, check_holdings_lst, done_lst)
            # Output the completed instructions list. Note this won't include numbers beyond quotas.
            instruction_manager.write_instructions(completed_list)
            logger.logit('done', include_timestamp=True)
        except KeyboardInterrupt:
            instruction_manager = InstructionManager(args.run + '.interrupted', debug=args.debug)
            # Save the instructions that haven't been done yet.
            set_holdings_lst   = list('+' + num for num in set_holdings_lst)
            unset_holdings_lst = list('-' + num for num in unset_holdings_lst)
            check_holdings_lst = list('?' + num for num in check_holdings_lst)
            # Don't add another action character to the done_lst
            complete_incomplete_list = instruction_manager.merge(set_holdings_lst, unset_holdings_lst, check_holdings_lst, done_lst)
            # Output the state of the lists as they were at the time of the interrupt.
            instruction_manager.write_instructions(complete_incomplete_list)
            logger.logit('!Warning, received keyboard interrupt!\nSaving work done.', level='error', include_timestamp=True)
            logger.logit('exited on <ctrl> + C interrupt.', include_timestamp=True)
    else:
        logger.logit(f"Warning, nothing to do. Either use --instructions or --run. See --help for more information.")
        
if __name__ == "__main__":
    main(sys.argv[1:])
# EOF