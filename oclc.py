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
from lib.oclcws import OclcService
# Debug mode
# DEBUG_MODE= True
DEBUG_MODE= False
APP      = 'oclc'
YAML     = 'oclc.yaml'

# TODO: Define workflow for comparing OCLC numbers at a library against OCLC holdings.
# TODO: Manage authentication. See oclcws.py for more information.

def _read_yaml_(yaml_file:str):
    """
    >>> c = _read_yaml_('epl_oclc.yaml')
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

def _update_holdings_(mode:str, num_file:str, config:dict):
    oclc_numbers = []
    # Read in a list of OCLC numbers to set.
    with open(num_file, encoding='utf8') as f:
        for line in f:
            oclc_numbers.append(line.strip())
    f.close()
    if DEBUG_MODE:
        print(f"numbers to set: {oclc_numbers}")
        print(f"    using mode: {mode}")
    if mode == 'set':
        ws = OclcService(config)
        # while oclc_numbers:
        #     results = ws.check_control_numbers(set_numbers)
        #     print(f"result: {results[1]}")
        #     print(f"and the list now contains: {results[0]}")
        pass
    elif mode == 'unset':
        pass
    elif mode == 'upload':
        pass
    else:
        return False

def main(argv):
    server = 'Test'
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
    
    # Test all the args
    if args.unset and os.path.isfile(args.unset) == False:
        sys.stderr.write(f"*error, no such file: '{args.unset}'.\n")
        sys.exit()
    if args.set and os.path.isfile(args.set) == False:
        sys.stderr.write(f"*error, no such file: '{args.set}'.\n")
        sys.exit()
    if args.xml_records and os.path.isfile(args.xml_records) == False:
        sys.stderr.write(f"*error, no such file: '{args.xml_records}'.\n")
        sys.exit()
    if args.yaml:
        if os.path.isfile(args.yaml) == False:
            sys.stderr.write(f"*error, no such file: '{args.yaml}'.\n")
            sys.exit()
    if args.test == False:
        server = 'Production'
    DEBUG_MODE = args.debug
    ##### End of arg parsing.
    set_numbers = []
    unset_numbers = []
    config = _read_yaml_(args.yaml)[server]
    if DEBUG_MODE:
        print(f"debug: '{DEBUG_MODE}'")
        print(f"test: '{args.test}'")
        print(f"config: '{config['name']}'")
        print(f"set: '{args.set}'")
        print(f"unset: '{args.unset}'")
        print(f"xml records: '{args.xml_records}'")
    # Read in a list of OCLC numbers to set.
    if args.set:
        if _update_holdings_('set', args.set, config) == False:
            sys.stderr.write(f"*error, while adding holdings in WorldCat!\nSee log for more details.")
            sys.exit()
    if args.unset:
        if _update_holdings_('unset', args.unset, config) == False:
            sys.stderr.write(f"*error, while deleting holdings in WorldCat!\nSee log for more details.")
            sys.exit()
    # print(f"config is a {type(config)} :: {config}")
    # Don't do anything if the input list is empty. 
    

if __name__ == "__main__":
    if DEBUG_MODE == True:
        import doctest
        doctest.testmod()
    else:
        main(sys.argv[1:])
# EOF